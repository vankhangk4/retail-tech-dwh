# ============================================================
# FILE: etl/orchestrator/main_etl.py
# Mô tả: ETL Orchestrator — vòng lặp tenant, chạy đầy đủ pipeline
# ============================================================

import os
import sys
import logging
import glob
import shutil
import pandas as pd
import pymssql
from datetime import date, datetime
from email.mime.text import MIMEText
import smtplib
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from etl.extract.extract_sales import (
    get_last_watermark,
    update_watermark,
    extract_sales_from_excel,
    extract_inventory_from_excel,
    extract_csv_file,
    load_to_staging,
)
from etl.transform.transform_sales import transform_sales

# ---- Configuration ----
MSSQL_SERVER   = os.environ.get('MSSQL_SERVER', 'localhost')
MSSQL_USER     = os.environ.get('MSSQL_USER', 'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', '')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant')

SMTP_HOST      = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT      = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER      = os.environ.get('SMTP_USER', '')
SMTP_PASS      = os.environ.get('SMTP_PASS', '')
ALERT_FROM     = os.environ.get('ALERT_FROM_EMAIL', 'etl@company.com')
ALERT_TO       = os.environ.get('ALERT_TO_EMAIL', 'admin@company.com')
SLACK_WEBHOOK  = os.environ.get('SLACK_WEBHOOK_URL', '')

LANDING_DIR_NAME = '1_landing'
ARCHIVE_DIR_NAME = '2_archive'
ERROR_DIR_NAME = '3_error'
STAGE_DIR_NAMES = {LANDING_DIR_NAME, ARCHIVE_DIR_NAME, ERROR_DIR_NAME}

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)
logger = logging.getLogger(__name__)


def resolve_tenant_root(data_dir: str) -> str:
    """Normalize legacy tenant paths and return the tenant root folder."""
    normalized = os.path.normpath(data_dir)
    if os.path.basename(normalized) in STAGE_DIR_NAMES:
        return os.path.dirname(normalized)
    return normalized


def ensure_tenant_stage_dirs(data_dir: str) -> dict:
    tenant_root = resolve_tenant_root(data_dir)
    stage_dirs = {
        'root': tenant_root,
        'landing': os.path.join(tenant_root, LANDING_DIR_NAME),
        'archive': os.path.join(tenant_root, ARCHIVE_DIR_NAME),
        'error': os.path.join(tenant_root, ERROR_DIR_NAME),
        'logs': os.path.join(tenant_root, 'logs'),
    }
    for path in stage_dirs.values():
        os.makedirs(path, exist_ok=True)
    return stage_dirs


def unique_destination(dest_dir: str, filename: str) -> str:
    candidate = os.path.join(dest_dir, filename)
    if not os.path.exists(candidate):
        return candidate

    stem, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(dest_dir, f'{stem}_{timestamp}{ext}')


def move_processed_file(file_path: str, dest_dir: str) -> str:
    os.makedirs(dest_dir, exist_ok=True)
    destination = unique_destination(dest_dir, os.path.basename(file_path))
    shutil.move(file_path, destination)
    return destination


def setup_tenant_logging(tenant_id: str, log_dir: str):
    """Add per-tenant rotating log file handler for this ETL run."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'etl_{timestamp}.log')
    try:
        fh = logging.FileHandler(log_file, encoding='utf-8')
    except PermissionError:
        # Fall back to /tmp if log dir is not writable
        log_file = f'/tmp/etl_{tenant_id}_{timestamp}.log'
        fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(fh)
    return log_file


# =============================================================================
# Connection
# =============================================================================

def get_conn():
    return pymssql.connect(
        server=MSSQL_SERVER,
        user=MSSQL_USER,
        password=MSSQL_PASSWORD,
        database=MSSQL_DATABASE
    )


# =============================================================================
# Alerts
# =============================================================================

def send_email_alert(subject: str, body: str) -> None:
    """Gửi email alert khi ETL thất bại."""
    if not SMTP_USER or not SMTP_PASS:
        logger.warning('SMTP not configured — skipping email alert')
        return
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = f'[DWH ALERT] {subject}'
        msg['From'] = ALERT_FROM
        msg['To'] = ALERT_TO
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.starttls()
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        logger.info(f'Alert email sent: {subject}')
    except Exception as e:
        logger.error(f'Failed to send email alert: {e}')


def send_slack_alert(message: str) -> None:
    """Gửi Slack alert khi ETL thất bại."""
    if not SLACK_WEBHOOK:
        return
    try:
        requests.post(
            SLACK_WEBHOOK,
            json={'text': f':rotating_light: {message}'},
            timeout=10
        )
    except Exception as e:
        logger.error(f'Failed to send Slack alert: {e}')


def alert(tenant_id: str, batch_date: str, error_msg: str) -> None:
    """Gửi alert qua email + Slack khi ETL lỗi."""
    subject = f'ETL FAILED: {tenant_id} @ {batch_date}'
    body = (
        f'DWH ETL Pipeline Failed\n'
        f'Tenant: {tenant_id}\n'
        f'Batch Date: {batch_date}\n'
        f'Error: {error_msg}\n'
        f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
    )
    send_email_alert(subject, body)
    send_slack_alert(f'{subject}\n{error_msg}')


# =============================================================================
# ETL Log  — uses actual DB schema:
#   LogID, TenantID, TableName, StepName, RowsProcessed,
#   RowsInserted, RowsUpdated, RowsRejected, DurationSec,
#   Status, ErrorMessage, CreatedAt
# =============================================================================

def write_etl_log(
    conn,
    tenant_id: str,
    table_name: str,
    step_name: str,
    status: str,
    rows_processed: int = None,
    rows_inserted: int = None,
    rows_rejected: int = None,
    duration_sec: float = None,
    error_msg: str = None
) -> None:
    """Ghi log vào bảng ETLLogs theo schema thực tế (không có BatchDate/SourceTable/RunStatus)."""
    if error_msg and len(error_msg) > 500:
        error_msg = error_msg[:497] + '...'
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO ETLLogs '
        '(TenantID, TableName, StepName, RowsProcessed, RowsInserted, '
        ' RowsUpdated, RowsRejected, DurationSec, Status, ErrorMessage, CreatedAt) '
        'VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s, %s, GETDATE())',
        (
            tenant_id,
            table_name,
            step_name,
            rows_processed if rows_processed is not None else 0,
            rows_inserted if rows_inserted is not None else 0,
            rows_rejected if rows_rejected is not None else 0,
            duration_sec,
            status,
            error_msg,
        )
    )
    conn.commit()
    logger.info(
        f'[ETL_LOG] {tenant_id} | {table_name}.{step_name} | {status} | '
        f'Processed={rows_processed} Inserted={rows_inserted} Rejected={rows_rejected}'
    )


# =============================================================================
# Stored Procedure runner
# =============================================================================

def run_sp(conn, sp_name: str, params: dict = None) -> None:
    """Gọi Stored Procedure trên SQL Server."""
    cursor = conn.cursor()
    if params:
        param_list = [params.get(k) for k in sorted(params.keys())]
        cursor.execute(
            f'EXEC {sp_name} {", ".join(["%s" for _ in param_list])}',
            param_list
        )
    else:
        cursor.execute(f'EXEC {sp_name}')
    conn.commit()
    logger.info(f'  [SP] Executed: {sp_name}')


def run_sql(conn, sql: str, params: list = None) -> None:
    """Execute raw SQL and commit."""
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    conn.commit()


# =============================================================================
# File type detection
# =============================================================================

def classify_file(filename: str) -> dict:
    """
    Phân loại file dựa trên tên file (case-insensitive).
    Returns dict: { 'type': str, 'sheet': str or None }
    Types: 'sales' | 'inventory' | 'customer' | 'product' | 'purchase' | 'supplier'
    Returns None if file is not a known type.
    """
    fn = filename.lower()
    if 'baocaodoanhthu' in fn:
        return {'type': 'sales', 'sheet': 'DanhSachHoaDon'}
    if 'quanlykho' in fn:
        return {'type': 'inventory', 'sheet': 'QuanLyKho'}
    if 'danhmuckhachhang' in fn:
        return {'type': 'customer', 'sheet': None}
    if 'danhmucsanpham' in fn:
        return {'type': 'product', 'sheet': None}
    if 'phieunhaphang' in fn:
        return {'type': 'purchase', 'sheet': None}
    if 'danhmucnhacungcap' in fn or 'nhacungcap' in fn or 'supplier' in fn:
        return {'type': 'supplier', 'sheet': None}
    return None


# =============================================================================
# Per-file-type processing helpers
# =============================================================================

def process_sales_file(conn, tenant_id: str, file_path: str, batch_date: date) -> dict:
    """Extract, transform, and load a sales Excel file into STG_SalesRaw."""
    wm = get_last_watermark(conn, tenant_id, 'Sales_Excel')
    df = extract_sales_from_excel(file_path, wm, tenant_id)
    result = {'rows_extracted': len(df), 'rows_inserted': 0, 'rows_rejected': 0}

    if df.empty:
        write_etl_log(conn, tenant_id, 'STG_SalesRaw', 'Extract', 'SUCCESS',
                      rows_processed=0, rows_inserted=0, rows_rejected=0, duration_sec=0)
        return result

    start = datetime.now()
    rows_extracted = len(df)
    stg_sales_cols = [
        'TenantID', 'SaleDate', 'ProductID', 'CustomerName',
        'StoreName', 'EmployeeName', 'PaymentMethod', 'Quantity',
        'UnitPrice', 'Discount', 'Revenue', 'LoadStatus',
        'ErrorMessage', 'CreatedAt'
    ]
    load_to_staging(conn, df, 'STG_SalesRaw', columns=stg_sales_cols)

    duration = (datetime.now() - start).total_seconds()
    write_etl_log(conn, tenant_id, 'STG_SalesRaw', 'Extract', 'SUCCESS',
                  rows_processed=rows_extracted,
                  rows_inserted=rows_extracted,
                  rows_rejected=0,
                  duration_sec=duration)
    result['rows_inserted'] = rows_extracted
    return result


def process_inventory_file(conn, tenant_id: str, file_path: str, batch_date: date) -> dict:
    """Extract and load an inventory Excel file into STG_InventoryRaw."""
    start = datetime.now()
    df = extract_inventory_from_excel(file_path, tenant_id)
    result = {'rows_extracted': len(df), 'rows_inserted': 0, 'rows_rejected': 0}

    if df.empty:
        write_etl_log(conn, tenant_id, 'STG_InventoryRaw', 'Extract', 'SUCCESS',
                      rows_processed=0, rows_inserted=0, rows_rejected=0, duration_sec=0)
        return result

    rows_extracted = len(df)
    stg_inv_cols = [
        'TenantID', 'CheckDate', 'ProductID', 'StoreName',
        'QuantityOnHand', 'LoadStatus', 'ErrorMessage', 'CreatedAt'
    ]
    load_to_staging(conn, df, 'STG_InventoryRaw', columns=stg_inv_cols)
    duration = (datetime.now() - start).total_seconds()

    write_etl_log(conn, tenant_id, 'STG_InventoryRaw', 'Extract', 'SUCCESS',
                  rows_processed=rows_extracted,
                  rows_inserted=rows_extracted,
                  rows_rejected=0,
                  duration_sec=duration)
    result['rows_inserted'] = rows_extracted
    return result


def process_csv_file(conn, tenant_id: str, file_path: str, file_type: str,
                     batch_date: date) -> dict:
    """Extract and load a CSV file into the appropriate staging table."""
    table_map = {
        'customer': ('STG_CustomerRaw',  ['CustomerID', 'CustomerName', 'Phone', 'Email',
                                           'City', 'Region', 'CustomerType', 'LoadStatus',
                                           'ErrorMessage', 'CreatedAt', 'TenantID']),
        'product':  ('STG_ProductRaw',   ['ProductID', 'ProductName', 'Category', 'SubCategory',
                                           'UnitPrice', 'SupplierID', 'LoadStatus',
                                           'ErrorMessage', 'CreatedAt', 'TenantID']),
        'purchase': ('STG_PurchaseRaw',   ['TenantID', 'PurchaseDate', 'ProductID', 'SupplierID',
                                           'Quantity', 'UnitCost', 'TotalCost', 'IsPaid',
                                           'LoadStatus', 'ErrorMessage', 'CreatedAt']),
    }
    table_info = table_map.get(file_type)
    if not table_info:
        return {'rows_extracted': 0, 'rows_inserted': 0, 'rows_rejected': 0}
    table_name, stg_cols = table_info

    start = datetime.now()
    df = extract_csv_file(file_path, tenant_id, file_type)
    result = {'rows_extracted': len(df), 'rows_inserted': 0, 'rows_rejected': 0}

    if df.empty:
        write_etl_log(conn, tenant_id, table_name, 'Extract', 'SUCCESS',
                      rows_processed=0, rows_inserted=0, rows_rejected=0, duration_sec=0)
        return result

    rows_extracted = len(df)
    load_to_staging(conn, df, table_name, columns=stg_cols)
    duration = (datetime.now() - start).total_seconds()

    write_etl_log(conn, tenant_id, table_name, 'Extract', 'SUCCESS',
                  rows_processed=rows_extracted,
                  rows_inserted=rows_extracted,
                  rows_rejected=0,
                  duration_sec=duration)
    result['rows_inserted'] = rows_extracted
    return result


def get_table_columns(conn, table_name: str) -> set:
    cursor = conn.cursor()
    cursor.execute(
        'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s',
        (table_name,)
    )
    return {row[0] for row in cursor.fetchall()}


def supplier_value(row, *columns, default=''):
    for column in columns:
        if column in row and pd.notna(row[column]):
            return str(row[column]).strip()
    return default


def process_supplier_file(conn, tenant_id: str, file_path: str, batch_date: date) -> dict:
    """Load supplier catalog directly into DimSupplier because there is no STG supplier table."""
    start = datetime.now()
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except Exception:
        df = pd.read_csv(file_path, encoding='utf-8')

    df.columns = df.columns.str.strip()
    if 'Mã NCC' not in df.columns or 'Tên NCC' not in df.columns:
        raise ValueError('Supplier CSV missing required columns: Mã NCC, Tên NCC')

    dim_columns = get_table_columns(conn, 'DimSupplier')
    supplier_key_col = 'SupplierID' if 'SupplierID' in dim_columns else 'SupplierCode'
    optional_columns = {
        'Country': lambda row: supplier_value(row, 'Quốc gia', 'Country', default=''),
        'Phone': lambda row: supplier_value(row, 'Số điện thoại', 'Phone'),
        'Email': lambda row: supplier_value(row, 'Email'),
        'PaymentTerm_Days': lambda row: int(float(supplier_value(row, 'Điều khoản TT (ngày)', 'PaymentTerm_Days', default='0') or 0)),
        'ContactName': lambda row: supplier_value(row, 'Người liên hệ', 'ContactName'),
        'ContactPerson': lambda row: supplier_value(row, 'Người liên hệ', 'ContactPerson'),
        'City': lambda row: supplier_value(row, 'Thành phố', 'Quốc gia', 'City'),
    }
    updatable_columns = [col for col in optional_columns if col in dim_columns]

    cursor = conn.cursor()
    inserted = 0
    for _, row in df.iterrows():
        supplier_code = supplier_value(row, 'Mã NCC').upper()
        supplier_name = supplier_value(row, 'Tên NCC')
        if not supplier_code or not supplier_name:
            continue

        insert_columns = [supplier_key_col, 'SupplierName', *updatable_columns]
        insert_values = [supplier_code, supplier_name, *[optional_columns[col](row) for col in updatable_columns]]
        update_assignments = ['target.SupplierName = source.SupplierName'] + [
            f'target.{col} = source.{col}' for col in updatable_columns
        ]
        source_columns = [f'%s AS {col}' for col in insert_columns]

        sql = f"""
            MERGE INTO DimSupplier AS target
            USING (SELECT {", ".join(source_columns)}) AS source
            ON target.{supplier_key_col} = source.{supplier_key_col}
            WHEN MATCHED THEN
                UPDATE SET {", ".join(update_assignments)}
            WHEN NOT MATCHED THEN
                INSERT ({", ".join(insert_columns)})
                VALUES ({", ".join(f"source.{col}" for col in insert_columns)});
        """
        cursor.execute(sql, insert_values)
        inserted += 1

    conn.commit()
    duration = (datetime.now() - start).total_seconds()
    write_etl_log(conn, tenant_id, 'DimSupplier', 'Extract', 'SUCCESS',
                  rows_processed=inserted,
                  rows_inserted=inserted,
                  rows_rejected=0,
                  duration_sec=duration)
    return {'rows_extracted': inserted, 'rows_inserted': inserted, 'rows_rejected': 0}


# =============================================================================
# Main ETL per tenant
# =============================================================================

def run_etl_for_tenant(tenant_id: str, data_dir: str, batch_date: date = None) -> bool:
    """
    Chạy ETL pipeline đầy đủ cho 1 tenant.

    Pipeline:
      PHASE 1: SCAN      — Tìm tất cả file mới trong thư mục 1_landing
      PHASE 2: EXTRACT   — Đọc từng file theo loại, load vào staging
      PHASE 3: TRANSFORM — Chuẩn hóa, làm sạch (Python) — Sales only
      PHASE 4: LOAD DIMS  — Nạp Dimension (SP)
      PHASE 5: LOAD FACTS — Transform và nạp Fact (SP)
      PHASE 6: REFRESH DM — Refresh Data Mart (SP)
      PHASE 7: UPDATE WM  — Cập nhật watermark + ghi ETLLogs

    Returns:
        True nếu thành công, False nếu thất bại
    """
    if batch_date is None:
        batch_date = date.today()

    batch_str = batch_date.strftime('%Y-%m-%d')
    stage_dirs = ensure_tenant_stage_dirs(data_dir)
    landing_dir = stage_dirs['landing']

    # Setup per-tenant log file inside the tenant's logs folder
    log_dir = stage_dirs['logs']
    log_file = setup_tenant_logging(tenant_id, log_dir)
    logger.info(f'ETL log file: {log_file}')

    logger.info(f'=' * 60)
    logger.info(f'ETL START: {tenant_id} | BatchDate={batch_str} | LandingDir={landing_dir}')
    logger.info(f'=' * 60)

    conn = None
    try:
        conn = get_conn()

        # ---- PHASE 1: SCAN files ----
        logger.info(f'[PHASE 1] SCAN — {tenant_id} @ {landing_dir}')
        xlsx_files = glob.glob(os.path.join(landing_dir, '*.xlsx')) + \
                     glob.glob(os.path.join(landing_dir, '*.xls'))
        csv_files  = glob.glob(os.path.join(landing_dir, '*.csv'))

        all_files = []
        failed_files = []
        unrecognized_files = []
        for f in xlsx_files + csv_files:
            info = classify_file(os.path.basename(f))
            if info:
                all_files.append({'path': f, **info})
            else:
                unrecognized_files.append(f)

        for f in unrecognized_files:
            fname = os.path.basename(f)
            failed_files.append(fname)
            logger.error(f'[{tenant_id}] Unrecognized source file moved to error: {fname}')
            write_etl_log(
                conn, tenant_id, 'SourceFile', 'Classify', 'FAILED',
                error_msg=f'Unrecognized source file: {fname}'
            )
            move_processed_file(f, stage_dirs['error'])

        if not all_files and not failed_files:
            logger.warning(f'[{tenant_id}] No recognizable data files found in {landing_dir}')
            return True

        logger.info(
            f'[{tenant_id}] Found {len(all_files)} files: '
            f'{[(os.path.basename(f["path"]), f["type"]) for f in all_files]}'
        )

        # Track overall results
        total_stats = {
            'sales':      {'extracted': 0, 'inserted': 0, 'rejected': 0},
            'inventory':  {'extracted': 0, 'inserted': 0, 'rejected': 0},
            'customer':   {'extracted': 0, 'inserted': 0},
            'product':    {'extracted': 0, 'inserted': 0},
            'purchase':   {'extracted': 0, 'inserted': 0},
            'supplier':   {'extracted': 0, 'inserted': 0},
        }

        # ---- PHASE 2: EXTRACT per file ----
        logger.info(f'[PHASE 2] EXTRACT — {tenant_id}')
        for file_info in all_files:
            fpath = file_info['path']
            ftype = file_info['type']
            fname = os.path.basename(fpath)
            logger.info(f'  Processing: {fname} (type={ftype})')

            try:
                if ftype == 'sales':
                    stats = process_sales_file(conn, tenant_id, fpath, batch_date)
                    total_stats['sales']['extracted'] += stats['rows_extracted']
                    total_stats['sales']['inserted']   += stats['rows_inserted']
                    total_stats['sales']['rejected']   += stats['rows_rejected']

                elif ftype == 'inventory':
                    stats = process_inventory_file(conn, tenant_id, fpath, batch_date)
                    total_stats['inventory']['extracted'] += stats['rows_extracted']
                    total_stats['inventory']['inserted']   += stats['rows_inserted']

                elif ftype in ('customer', 'product', 'purchase'):
                    stats = process_csv_file(conn, tenant_id, fpath, ftype, batch_date)
                    total_stats[ftype]['extracted'] += stats['rows_extracted']
                    total_stats[ftype]['inserted']   += stats['rows_inserted']

                elif ftype == 'supplier':
                    stats = process_supplier_file(conn, tenant_id, fpath, batch_date)
                    total_stats['supplier']['extracted'] += stats['rows_extracted']
                    total_stats['supplier']['inserted']   += stats['rows_inserted']

                archive_path = move_processed_file(fpath, stage_dirs['archive'])
                logger.info(f'  [{tenant_id}] Archived processed file: {fname} -> {archive_path}')

            except Exception as ex:
                failed_files.append(fname)
                logger.error(f'  [{tenant_id}] Failed to process {fname}: {ex}')
                log_table = 'DimSupplier' if ftype == 'supplier' else (
                    f'STG_{ftype.title()}Raw' if ftype != 'product' else 'STG_ProductRaw'
                )
                write_etl_log(
                    conn, tenant_id, log_table,
                    'Extract', 'FAILED', error_msg=str(ex)
                )
                try:
                    error_path = move_processed_file(fpath, stage_dirs['error'])
                    logger.info(f'  [{tenant_id}] Moved failed file to error: {fname} -> {error_path}')
                except Exception as move_ex:
                    logger.error(f'  [{tenant_id}] Could not move failed file {fname}: {move_ex}')
                # Continue with other files — don't abort the whole tenant

        # ---- PHASE 3: TRANSFORM (Python — already done per-file for Sales) ----
        logger.info(f'[PHASE 3] TRANSFORM — {tenant_id} (handled inline in Phase 2 for Sales)')

        # ---- PHASE 4: LOAD DIMENSIONS (via Python MERGE — avoids SP isolation issues) ----
        logger.info(f'[PHASE 4] LOAD DIMENSIONS — {tenant_id}')

        # Upsert DimProduct (SHARED — no TenantID needed)
        try:
            run_sql(conn, """
                MERGE INTO DimProduct AS target
                USING (
                    SELECT DISTINCT ProductID, ProductName, Category, SubCategory,
                           UnitPrice, SupplierID
                    FROM STG_ProductRaw
                    WHERE ProductID IS NOT NULL AND ProductID != ''
                ) AS source
                ON target.ProductID = source.ProductID
                WHEN MATCHED THEN
                    UPDATE SET
                        target.ProductName = source.ProductName,
                        target.Category = source.Category,
                        target.SubCategory = source.SubCategory,
                        target.UnitPrice = CAST(source.UnitPrice AS DECIMAL(18,2)),
                        target.SupplierID = source.SupplierID,
                        target.IsActive = 1
                WHEN NOT MATCHED THEN
                    INSERT (ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, IsActive)
                    VALUES (source.ProductID, source.ProductName, source.Category, source.SubCategory,
                            CAST(source.UnitPrice AS DECIMAL(18,2)), source.SupplierID, 1);
            """)
            logger.info('  [MERGE] DimProduct done')
        except Exception as e:
            logger.warning(f'  [MERGE] DimProduct failed: {e}')

        # Upsert DimCustomer (per TenantID)
        try:
            run_sql(conn, f"""
                MERGE INTO DimCustomer AS target
                USING (
                    SELECT DISTINCT CustomerID, CustomerName, Phone, Email,
                           City, Region, CustomerType, TenantID
                    FROM STG_CustomerRaw
                    WHERE TenantID = %s
                      AND CustomerID IS NOT NULL AND CustomerID != ''
                ) AS source
                ON target.CustomerID = source.CustomerID AND target.TenantID = source.TenantID
                WHEN MATCHED THEN
                    UPDATE SET
                        target.CustomerName = source.CustomerName,
                        target.Phone = source.Phone,
                        target.Email = source.Email,
                        target.City = source.City,
                        target.Region = source.Region,
                        target.CustomerType = source.CustomerType
                WHEN NOT MATCHED THEN
                    INSERT (CustomerID, CustomerName, Phone, Email, City, Region, CustomerType, TenantID)
                    VALUES (source.CustomerID, source.CustomerName, source.Phone, source.Email,
                            source.City, source.Region, source.CustomerType, source.TenantID);
            """, [tenant_id])
            logger.info('  [MERGE] DimCustomer done')
        except Exception as e:
            logger.warning(f'  [MERGE] DimCustomer failed: {e}')

        # Sync DimStore from tenant master instead of trusting StoreName in uploaded files.
        try:
            run_sql(conn, f"""
                UPDATE ds
                SET
                    ds.StoreName = t.TenantName,
                    ds.IsActive = t.IsActive
                FROM DimStore ds
                INNER JOIN Tenants t ON t.TenantID = ds.TenantID
                WHERE ds.TenantID = %s;

                IF NOT EXISTS (SELECT 1 FROM DimStore WHERE TenantID = %s)
                BEGIN
                    INSERT INTO DimStore (
                        TenantID, StoreName, City, Region, Address,
                        ManagerName, OpenDate, IsActive
                    )
                    SELECT
                        TenantID,
                        TenantName,
                        '',
                        '',
                        '',
                        NULL,
                        CAST(GETDATE() AS DATE),
                        IsActive
                    FROM Tenants
                    WHERE TenantID = %s;
                END
            """, [tenant_id, tenant_id, tenant_id])
            logger.info('  [MERGE] DimStore synced from Tenants done')
        except Exception as e:
            logger.warning(f'  [MERGE] DimStore failed: {e}')

        # ---- PHASE 5: LOAD FACTS (Python MERGE — matches actual DB schema) ----
        logger.info(f'[PHASE 5] LOAD FACTS — {tenant_id}')

        # -- 5A. FactSales: STG_SalesRaw → FactSales --
        try:
            run_sql(conn, f"""
                INSERT INTO FactSales (
                    TenantID, SaleDate, ProductID, CustomerID, StoreKey,
                    EmployeeID, PaymentMethod, Quantity, UnitPrice, Discount,
                    Revenue, Cost, CreatedAt
                )
                SELECT
                    s.TenantID,
                    TRY_CAST(s.SaleDate AS DATE),
                    s.ProductID,
                    NULLIF(s.CustomerName, '') COLLATE Vietnamese_CI_AS,
                    st.StoreKey,
                    NULLIF(s.EmployeeName, '') COLLATE Vietnamese_CI_AS,
                    CASE
                        WHEN LOWER(LTRIM(RTRIM(s.PaymentMethod))) IN ('cash','tm') THEN 'Cash'
                        WHEN LOWER(LTRIM(RTRIM(s.PaymentMethod))) IN ('transfer','ck') THEN 'Transfer'
                        WHEN LOWER(LTRIM(RTRIM(s.PaymentMethod))) IN ('card','credit') THEN 'Card'
                        ELSE 'Cash'
                    END,
                    TRY_CAST(s.Quantity AS INT),
                    TRY_CAST(s.UnitPrice AS DECIMAL(18,2)),
                    TRY_CAST(s.Discount AS DECIMAL(18,2)),
                    -- Revenue = Qty * UnitPrice - Discount
                    TRY_CAST(s.Quantity AS DECIMAL(18,2)) * TRY_CAST(s.UnitPrice AS DECIMAL(18,2))
                        - TRY_CAST(s.Discount AS DECIMAL(18,2)),
                    -- Cost = Qty * Product's UnitCostPrice from DimProduct
                    TRY_CAST(s.Quantity AS DECIMAL(18,2)) * ISNULL(p.UnitPrice, 0),
                    GETDATE()
                FROM STG_SalesRaw s
                INNER JOIN DimProduct p ON p.ProductID = s.ProductID AND p.IsActive = 1
                CROSS APPLY (
                    SELECT TOP 1 ds.StoreKey
                    FROM DimStore ds
                    WHERE ds.TenantID = s.TenantID
                    ORDER BY ds.StoreKey
                ) st
                WHERE s.TenantID = %s
                  AND s.ProductID IS NOT NULL AND s.ProductID != ''
                  AND s.SaleDate IS NOT NULL
                  AND TRY_CAST(s.Quantity AS INT) > 0
                  AND TRY_CAST(s.UnitPrice AS DECIMAL(18,2)) IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM FactSales f
                      WHERE f.TenantID = s.TenantID
                        AND f.ProductID = s.ProductID
                        AND f.StoreKey = st.StoreKey
                        AND TRY_CAST(f.SaleDate AS DATE) = TRY_CAST(s.SaleDate AS DATE)
                  );
            """, [tenant_id])
            logger.info('  [MERGE] FactSales done')
        except Exception as e:
            logger.warning(f'  [MERGE] FactSales failed: {e}')

        # -- 5B. FactInventory: STG_InventoryRaw → FactInventory --
        try:
            run_sql(conn, f"""
                INSERT INTO FactInventory (
                    TenantID, CheckDate, ProductID, StoreKey,
                    QuantityOnHand, ReorderLevel, LastRestocked, CreatedAt
                )
                SELECT
                    s.TenantID,
                    TRY_CAST(s.CheckDate AS DATE),
                    s.ProductID,
                    st.StoreKey,
                    TRY_CAST(s.QuantityOnHand AS INT),
                    10,
                    TRY_CAST(s.CheckDate AS DATE),
                    GETDATE()
                FROM STG_InventoryRaw s
                INNER JOIN DimProduct p ON p.ProductID = s.ProductID AND p.IsActive = 1
                CROSS APPLY (
                    SELECT TOP 1 ds.StoreKey
                    FROM DimStore ds
                    WHERE ds.TenantID = s.TenantID
                    ORDER BY ds.StoreKey
                ) st
                WHERE s.TenantID = %s
                  AND s.ProductID IS NOT NULL AND s.ProductID != ''
                  AND TRY_CAST(s.QuantityOnHand AS INT) IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM FactInventory f
                      WHERE f.TenantID = s.TenantID
                        AND f.ProductID = s.ProductID
                        AND f.StoreKey = st.StoreKey
                        AND CAST(f.CheckDate AS DATE) = TRY_CAST(s.CheckDate AS DATE)
                  );
            """, [tenant_id])
            logger.info('  [MERGE] FactInventory done')
        except Exception as e:
            logger.warning(f'  [MERGE] FactInventory failed: {e}')

        # -- 5C. FactPurchase: STG_PurchaseRaw → FactPurchase --
        try:
            run_sql(conn, f"""
                INSERT INTO FactPurchase (
                    TenantID, PurchaseDate, ProductID, SupplierID,
                    Quantity, UnitCost, TotalCost, IsPaid, CreatedAt
                )
                SELECT
                    s.TenantID,
                    TRY_CAST(s.PurchaseDate AS DATE),
                    s.ProductID,
                    NULLIF(s.SupplierID, '') COLLATE Vietnamese_CI_AS,
                    TRY_CAST(s.Quantity AS INT),
                    TRY_CAST(s.UnitCost AS DECIMAL(18,2)),
                    TRY_CAST(s.TotalCost AS DECIMAL(18,2)),
                    CASE WHEN s.IsPaid IN ('1','True','true','YES','yes') THEN 1 ELSE 0 END,
                    GETDATE()
                FROM STG_PurchaseRaw s
                INNER JOIN DimProduct p ON p.ProductID = s.ProductID AND p.IsActive = 1
                WHERE s.TenantID = %s
                  AND s.ProductID IS NOT NULL AND s.ProductID != ''
                  AND TRY_CAST(s.Quantity AS INT) > 0
                  AND TRY_CAST(s.UnitCost AS DECIMAL(18,2)) IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1 FROM FactPurchase f
                      WHERE f.TenantID = s.TenantID
                        AND f.ProductID = s.ProductID
                        AND CAST(f.PurchaseDate AS DATE) = TRY_CAST(s.PurchaseDate AS DATE)
                  );
            """, [tenant_id, tenant_id])
            logger.info('  [MERGE] FactPurchase done')
        except Exception as e:
            logger.warning(f'  [MERGE] FactPurchase failed: {e}')

        # ---- PHASE 6: REFRESH DATA MART (Python MERGE) ----
        logger.info(f'[PHASE 6] REFRESH DATA MART — {tenant_id}')

        # -- DM_SalesSummary --
        try:
            run_sql(conn, f"DELETE FROM DM_SalesSummary WHERE TenantID = %s;", [tenant_id])
            run_sql(conn, f"""
                INSERT INTO DM_SalesSummary (
                    TenantID, Year, Quarter, Month, ProductID, Category,
                    TotalRevenue, TotalCost, TotalProfit, OrderCount, AvgOrderVal, UpdatedAt
                )
                SELECT
                    f.TenantID,
                    YEAR(TRY_CAST(f.SaleDate AS DATE)),
                    DATEPART(QUARTER, TRY_CAST(f.SaleDate AS DATE)),
                    MONTH(TRY_CAST(f.SaleDate AS DATE)),
                    f.ProductID,
                    ISNULL(p.Category, N'Trống'),
                    SUM(TRY_CAST(f.Revenue AS DECIMAL(18,2))),
                    0,
                    SUM(TRY_CAST(f.Revenue AS DECIMAL(18,2))),
                    COUNT(*),
                    AVG(TRY_CAST(f.Revenue AS DECIMAL(18,2))),
                    GETDATE()
                FROM FactSales f
                INNER JOIN DimProduct p ON p.ProductID = f.ProductID
                WHERE f.TenantID = %s
                GROUP BY f.TenantID,
                         YEAR(TRY_CAST(f.SaleDate AS DATE)),
                         DATEPART(QUARTER, TRY_CAST(f.SaleDate AS DATE)),
                         MONTH(TRY_CAST(f.SaleDate AS DATE)),
                         f.ProductID, p.Category;
            """, [tenant_id])
            logger.info('  [MERGE] DM_SalesSummary done')
        except Exception as e:
            logger.warning(f'  [MERGE] DM_SalesSummary failed: {e}')

        # -- DM_CustomerRFM --
        try:
            run_sql(conn, f"DELETE FROM DM_CustomerRFM WHERE TenantID = %s;", [tenant_id])
            run_sql(conn, f"""
                ;WITH RFMBase AS (
                    SELECT
                        f.TenantID,
                        f.CustomerID AS CustomerCode,
                        MAX(f.CustomerID) AS CustomerName,
                        MAX(TRY_CAST(f.SaleDate AS DATE)) AS LastSaleDate,
                        COUNT(*) AS Frequency,
                        SUM(TRY_CAST(f.Revenue AS DECIMAL(18,2))) AS Monetary
                    FROM FactSales f
                    WHERE f.TenantID = %s
                      AND f.CustomerID IS NOT NULL AND f.CustomerID != ''
                    GROUP BY f.TenantID, f.CustomerID
                ),
                RFMAll AS (
                    SELECT
                        r.TenantID, r.CustomerCode, r.CustomerName,
                        r.LastSaleDate, r.Frequency, r.Monetary,
                        DATEDIFF(DAY, r.LastSaleDate, CAST(GETDATE() AS DATE)) AS Recency,
                        NTILE(5) OVER (PARTITION BY r.TenantID ORDER BY DATEDIFF(DAY, r.LastSaleDate, CAST(GETDATE() AS DATE)) DESC) AS R_Score,
                        NTILE(5) OVER (PARTITION BY r.TenantID ORDER BY r.Frequency) AS F_Score,
                        NTILE(5) OVER (PARTITION BY r.TenantID ORDER BY r.Monetary) AS M_Score
                    FROM RFMBase r
                )
                INSERT INTO DM_CustomerRFM (
                    TenantID, CustomerID, Recency, Frequency, Monetary, RFMScore, Segment, UpdatedAt
                )
                SELECT
                    r.TenantID, r.CustomerCode,
                    r.Recency, r.Frequency, r.Monetary,
                    CAST(r.R_Score AS VARCHAR) + CAST(r.F_Score AS VARCHAR) + CAST(r.M_Score AS VARCHAR),
                    CASE
                        WHEN r.R_Score + r.F_Score + r.M_Score >= 13 THEN N'Champions'
                        WHEN r.R_Score + r.F_Score + r.M_Score >= 10 THEN N'Loyal'
                        WHEN r.R_Score + r.F_Score + r.M_Score >= 7  THEN N'Potential'
                        WHEN r.R_Score + r.F_Score + r.M_Score >= 4  THEN N'At Risk'
                        ELSE N'Lost'
                    END,
                    GETDATE()
                FROM RFMAll r;
            """, [tenant_id])
            logger.info('  [MERGE] DM_CustomerRFM done')
        except Exception as e:
            logger.warning(f'  [MERGE] DM_CustomerRFM failed: {e}')

        # ---- PHASE 7: UPDATE WATERMARK + FINAL LOG ----
        logger.info(f'[PHASE 7] FINALIZE — {tenant_id}')
        for ftype in total_stats:
            if total_stats[ftype]['extracted'] > 0:
                wm_table = f'{tenant_id}_{ftype.title()}'
                update_watermark(conn, tenant_id, wm_table, 'SUCCESS')

        total_rows = sum(v['extracted'] for v in total_stats.values())
        final_status = 'FAILED' if failed_files else 'SUCCESS'
        final_error = f'Failed source files: {", ".join(failed_files)}' if failed_files else None
        write_etl_log(
            conn, tenant_id, 'ETL_AllFiles', 'PipelineComplete', final_status,
            rows_processed=total_rows,
            rows_inserted=sum(v['inserted'] for v in total_stats.values()),
            duration_sec=0,
            error_msg=final_error,
        )

        if failed_files:
            logger.error(f'[{tenant_id}] ETL COMPLETED WITH FILE ERRORS — {failed_files}')
            logger.error(f'ETL FAILED: {tenant_id} | {batch_str}')
        else:
            logger.info(f'[{tenant_id}] ETL SUCCESS — Stats: {total_stats}')
            logger.info(f'ETL SUCCESS: {tenant_id} | {batch_str}')
        conn.close()
        return not failed_files

    except Exception as ex:
        logger.error(f'ETL FAILED: {tenant_id} — {ex}', exc_info=True)
        if conn:
            try:
                update_watermark(conn, tenant_id, f'{tenant_id}_ALL', 'FAILED')
                write_etl_log(
                    conn, tenant_id, 'ETL_AllFiles', 'PipelineComplete', 'FAILED',
                    error_msg=str(ex)
                )
                conn.close()
            except Exception:
                pass

        alert(tenant_id, batch_str, str(ex))
        return False


# =============================================================================
# Tenant discovery
# =============================================================================

def get_active_tenants(conn) -> list:
    """Lấy danh sách tenant đang hoạt động từ SQL Server."""
    cursor = conn.cursor()
    cursor.execute(
        'SELECT TenantID, TenantName, FilePath FROM Tenants WHERE IsActive = 1'
    )
    return [
        {'tenant_id': row[0], 'name': row[1], 'file_path': row[2]}
        for row in cursor.fetchall()
    ]


# =============================================================================
# Run all tenants
# =============================================================================

def run_all_etl(batch_date: date = None) -> dict:
    """
    Chạy ETL cho tất cả tenant đang hoạt động.

    Returns:
        Dict với kết quả: {'STORE_HN': True, 'STORE_HCM': False, ...}
    """
    results = {}
    conn = get_conn()
    tenants = get_active_tenants(conn)
    conn.close()

    logger.info(f'Found {len(tenants)} active tenants: {[t["tenant_id"] for t in tenants]}')

    for tenant in tenants:
        tenant_id = tenant['tenant_id']
        # data_dir is at ./data/{tenant_id}/ relative to where ETL runs
        data_dir = tenant['file_path'] or f'./data/{tenant_id}/'
        success = run_etl_for_tenant(tenant_id, data_dir, batch_date)
        results[tenant_id] = success

    return results


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='DWH ETL Orchestrator — Multi-Tenant')
    parser.add_argument('--date', type=str, default=None,
                        help='Batch date (YYYY-MM-DD), default = today')
    parser.add_argument('--tenant', type=str, default=None,
                        help='Run ETL for specific tenant only')
    args = parser.parse_args()

    batch_date = date.fromisoformat(args.date) if args.date else date.today()

    if args.tenant:
        # Chạy cho 1 tenant
        conn = get_conn()
        tenants = get_active_tenants(conn)
        conn.close()

        tenant_info = next(
            (t for t in tenants if t['tenant_id'] == args.tenant), None
        )
        if not tenant_info:
            logger.error(f'Tenant not found: {args.tenant}')
            sys.exit(1)

        data_dir = tenant_info['file_path'] or f'./data/{args.tenant}/'
        stage_dirs = ensure_tenant_stage_dirs(data_dir)
        if not os.path.isdir(stage_dirs['landing']):
            logger.error(f'Landing directory not found: {stage_dirs["landing"]}')
            sys.exit(1)

        success = run_etl_for_tenant(args.tenant, data_dir, batch_date)
        sys.exit(0 if success else 1)
    else:
        results = run_all_etl(batch_date)
        success_count = sum(1 for v in results.values() if v is True)
        fail_count   = sum(1 for v in results.values() if v is False)
        logger.info(f'ETL Summary: {success_count} success, {fail_count} failed')
        sys.exit(0 if fail_count == 0 else 1)
