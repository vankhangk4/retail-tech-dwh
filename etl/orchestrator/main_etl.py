# ============================================================
# FILE: etl/orchestrator/main_etl.py
# Mô tả: ETL Orchestrator — vòng lặp tenant, chạy đầy đủ pipeline
# ============================================================

import os
import sys
import logging
import glob
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

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()],
    force=True
)
logger = logging.getLogger(__name__)


def setup_tenant_logging(tenant_id: str, log_dir: str):
    """Add per-tenant rotating log file handler for this ETL run."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(log_dir, f'etl_{timestamp}.log')
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
            rows_processed,
            rows_inserted,
            rows_rejected,
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


# =============================================================================
# File type detection
# =============================================================================

def classify_file(filename: str) -> dict:
    """
    Phân loại file dựa trên tên file (case-insensitive).
    Returns dict: { 'type': str, 'sheet': str or None }
    Types: 'sales' | 'inventory' | 'customer' | 'product' | 'purchase'
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
    load_to_staging(conn, df, 'STG_SalesRaw')

    # Transform
    df = transform_sales(df, tenant_id)
    rows_rejected = rows_extracted - len(df)

    if not df.empty:
        load_to_staging(conn, df, 'STG_SalesRaw')

    duration = (datetime.now() - start).total_seconds()
    write_etl_log(conn, tenant_id, 'STG_SalesRaw', 'Extract', 'SUCCESS',
                  rows_processed=rows_extracted,
                  rows_inserted=len(df),
                  rows_rejected=rows_rejected,
                  duration_sec=duration)
    result['rows_inserted'] = len(df)
    result['rows_rejected'] = rows_rejected
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
    load_to_staging(conn, df, 'STG_InventoryRaw')
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
        'customer': 'STG_CustomerRaw',
        'product':  'STG_ProductRaw',
        'purchase': 'STG_PurchaseRaw',
    }
    table_name = table_map.get(file_type)
    if not table_name:
        return {'rows_extracted': 0, 'rows_inserted': 0, 'rows_rejected': 0}

    start = datetime.now()
    df = extract_csv_file(file_path, tenant_id, file_type)
    result = {'rows_extracted': len(df), 'rows_inserted': 0, 'rows_rejected': 0}

    if df.empty:
        write_etl_log(conn, tenant_id, table_name, 'Extract', 'SUCCESS',
                      rows_processed=0, rows_inserted=0, rows_rejected=0, duration_sec=0)
        return result

    rows_extracted = len(df)
    load_to_staging(conn, df, table_name)
    duration = (datetime.now() - start).total_seconds()

    write_etl_log(conn, tenant_id, table_name, 'Extract', 'SUCCESS',
                  rows_processed=rows_extracted,
                  rows_inserted=rows_extracted,
                  rows_rejected=0,
                  duration_sec=duration)
    result['rows_inserted'] = rows_extracted
    return result


# =============================================================================
# Main ETL per tenant
# =============================================================================

def run_etl_for_tenant(tenant_id: str, data_dir: str, batch_date: date = None) -> bool:
    """
    Chạy ETL pipeline đầy đủ cho 1 tenant.

    Pipeline:
      PHASE 1: SCAN      — Tìm tất cả file trong thư mục data
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

    # Setup per-tenant log file inside the tenant's logs folder
    log_dir = os.path.join(data_dir, 'logs')
    log_file = setup_tenant_logging(tenant_id, log_dir)
    logger.info(f'ETL log file: {log_file}')

    logger.info(f'=' * 60)
    logger.info(f'ETL START: {tenant_id} | BatchDate={batch_str} | Dir={data_dir}')
    logger.info(f'=' * 60)

    conn = None
    try:
        conn = get_conn()

        # ---- PHASE 1: SCAN files ----
        logger.info(f'[PHASE 1] SCAN — {tenant_id} @ {data_dir}')
        xlsx_files = glob.glob(os.path.join(data_dir, '*.xlsx')) + \
                     glob.glob(os.path.join(data_dir, '*.xls'))
        csv_files  = glob.glob(os.path.join(data_dir, '*.csv'))

        all_files = []
        for f in xlsx_files + csv_files:
            info = classify_file(os.path.basename(f))
            if info:
                all_files.append({'path': f, **info})

        if not all_files:
            logger.warning(f'[{tenant_id}] No recognizable data files found in {data_dir}')
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

            except Exception as ex:
                logger.error(f'  [{tenant_id}] Failed to process {fname}: {ex}')
                write_etl_log(
                    conn, tenant_id, f'STG_{ftype.title()}Raw' if ftype != 'product' else 'STG_ProductRaw',
                    'Extract', 'FAILED', error_msg=str(ex)
                )
                # Continue with other files — don't abort the whole tenant

        # ---- PHASE 3: TRANSFORM (Python — already done per-file for Sales) ----
        logger.info(f'[PHASE 3] TRANSFORM — {tenant_id} (handled inline in Phase 2 for Sales)')

        # ---- PHASE 4: LOAD DIMENSIONS ----
        logger.info(f'[PHASE 4] LOAD DIMENSIONS — {tenant_id}')
        run_sp(conn, 'usp_Load_DimProduct', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Load_DimCustomer', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Load_DimStore', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Load_DimEmployee', {'TenantID': tenant_id})
        if total_stats.get('product', {}).get('extracted', 0) > 0:
            run_sp(conn, 'usp_Load_DimProduct', {'TenantID': 'SHARED'})
        if total_stats.get('customer', {}).get('extracted', 0) > 0:
            run_sp(conn, 'usp_Load_DimSupplier', {'TenantID': tenant_id})   # Supplier only if new

        # ---- PHASE 5: LOAD FACTS ----
        logger.info(f'[PHASE 5] LOAD FACTS — {tenant_id}')
        run_sp(conn, 'usp_Transform_FactSales',
               {'BatchDate': batch_str, 'TenantID': tenant_id})
        if total_stats.get('inventory', {}).get('extracted', 0) > 0:
            run_sp(conn, 'usp_Transform_FactInventory',
                   {'BatchDate': batch_str, 'TenantID': tenant_id})
        if total_stats.get('purchase', {}).get('extracted', 0) > 0:
            run_sp(conn, 'usp_Transform_FactPurchase',
                   {'BatchDate': batch_str, 'TenantID': tenant_id})

        # ---- PHASE 6: REFRESH DATA MART ----
        logger.info(f'[PHASE 6] REFRESH DATA MART — {tenant_id}')
        run_sp(conn, 'usp_Refresh_DM_SalesSummary', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Refresh_DM_CustomerRFM', {'TenantID': tenant_id})

        # ---- PHASE 7: UPDATE WATERMARK + FINAL LOG ----
        logger.info(f'[PHASE 7] FINALIZE — {tenant_id}')
        for ftype in total_stats:
            if total_stats[ftype]['extracted'] > 0:
                wm_table = f'{tenant_id}_{ftype.title()}'
                update_watermark(conn, tenant_id, wm_table, 'SUCCESS')

        total_rows = sum(v['extracted'] for v in total_stats.values())
        write_etl_log(
            conn, tenant_id, 'ETL_AllFiles', 'PipelineComplete', 'SUCCESS',
            rows_processed=total_rows,
            rows_inserted=sum(v['inserted'] for v in total_stats.values()),
            duration_sec=0,
        )

        logger.info(f'[{tenant_id}] ETL SUCCESS — Stats: {total_stats}')
        logger.info(f'ETL SUCCESS: {tenant_id} | {batch_str}')
        conn.close()
        return True

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
        if not os.path.isdir(data_dir):
            logger.error(f'Data directory not found: {data_dir}')
            sys.exit(1)

        run_etl_for_tenant(args.tenant, data_dir, batch_date)
    else:
        results = run_all_etl(batch_date)
        success_count = sum(1 for v in results.values() if v is True)
        fail_count   = sum(1 for v in results.values() if v is False)
        logger.info(f'ETL Summary: {success_count} success, {fail_count} failed')
        sys.exit(0 if fail_count == 0 else 1)
