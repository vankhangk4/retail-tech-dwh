# ============================================================
# FILE: etl/orchestrator/main_etl.py
# Mô tả: ETL Orchestrator — vòng lặp tenant, chạy đầy đủ pipeline
# ============================================================

import os
import sys
import logging
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
    load_to_staging,
)
from etl.transform.transform_sales import transform_sales, get_transform_stats

# ---- Configuration ----
MSSQL_SERVER = os.environ.get('MSSQL_SERVER', 'localhost')
MSSQL_USER = os.environ.get('MSSQL_USER', 'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD', '')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant')


def get_conn():
    return pymssql.connect(
        server=MSSQL_SERVER,
        user=MSSQL_USER,
        password=MSSQL_PASSWORD,
        database=MSSQL_DATABASE
    )

SMTP_HOST    = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT    = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER    = os.environ.get('SMTP_USER', '')
SMTP_PASS    = os.environ.get('SMTP_PASS', '')
ALERT_FROM   = os.environ.get('ALERT_FROM_EMAIL', 'etl@company.com')
ALERT_TO     = os.environ.get('ALERT_TO_EMAIL', 'admin@company.com')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK_URL', '')

# ---- Logging ----
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('etl_orchestrator.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)


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


def write_etl_log(
    conn,
    tenant_id: str,
    batch_date: date,
    source_table: str,
    status: str,
    rows_extracted: int = None,
    rows_inserted: int = None,
    rows_rejected: int = None,
    error_msg: str = None
) -> None:
    """Ghi log vào bảng ETLLogs."""
    cursor = conn.cursor()
    end_time = datetime.now() if status in ('SUCCESS', 'FAILED') else None

    cursor.execute(
        'INSERT INTO ETLLogs (TenantID, BatchDate, SourceTable, RunStatus, '
        'RowsExtracted, RowsInserted, RowsRejected, StartTime, EndTime, ErrorMessage) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, GETDATE(), ?, ?)',
        (tenant_id, batch_date, source_table, status,
         rows_extracted, rows_inserted, rows_rejected, end_time, error_msg)
    )
    conn.commit()
    logger.info(
        f'[ETL_LOG] {tenant_id} | {source_table} | {status} | '
        f'Extracted={rows_extracted} Inserted={rows_inserted} Rejected={rows_rejected}'
    )


def run_sp(conn, sp_name: str, params: dict = None) -> None:
    """Gọi Stored Procedure trên SQL Server."""
    cursor = conn.cursor()
    if params:
        param_list = [params.get(k) for k in sorted(params.keys())]
        cursor.execute(f'EXEC {sp_name} {", ".join(["?" for _ in param_list])}', param_list)
    else:
        cursor.execute(f'EXEC {sp_name}')
    conn.commit()
    logger.info(f'  [SP] Executed: {sp_name}')


def run_etl_for_tenant(tenant_id: str, file_path: str, batch_date: date = None) -> bool:
    """
    Chạy ETL pipeline đầy đủ cho 1 tenant.

    Pipeline:
      PHASE 1: EXTRACT    — Đọc Excel, gắn TenantID, load vào STG_SalesRaw
      PHASE 2: TRANSFORM  — Chuẩn hóa, làm sạch (Python)
      PHASE 3: LOAD DIMS  — Nạp Dimension (SP)
      PHASE 4: LOAD FACTS — Transform và nạp Fact (SP)
      PHASE 5: REFRESH DM — Refresh Data Mart (SP)
      PHASE 6: UPDATE WM  — Cập nhật watermark + ghi ETLLogs

    Returns:
        True nếu thành công, False nếu thất bại
    """
    if batch_date is None:
        batch_date = date.today()

    batch_str = batch_date.strftime('%Y-%m-%d')
    table_name = f'{tenant_id}_Sales_Excel'

    logger.info(f'=' * 60)
    logger.info(f'ETL START: {tenant_id} | BatchDate={batch_str}')
    logger.info(f'=' * 60)

    conn = None
    try:
        conn = get_conn()

        # ---- PHASE 1: EXTRACT ----
        logger.info(f'[PHASE 1] EXTRACT — {tenant_id}')
        update_watermark(conn, tenant_id, table_name, 'RUNNING')

        wm = get_last_watermark(conn, tenant_id, table_name)
        df = extract_sales_from_excel(file_path, wm, tenant_id)

        if df.empty:
            logger.warning(f'[{tenant_id}] No new data to process')
            update_watermark(conn, tenant_id, table_name, 'SUCCESS')
            write_etl_log(conn, tenant_id, batch_date, 'STG_SalesRaw', 'SUCCESS', 0, 0, 0)
            return True

        rows_extracted = len(df)

        # Truncate và load vào Staging
        load_to_staging(conn, df, 'STG_SalesRaw')
        logger.info(f'[PHASE 1] EXTRACT complete: {rows_extracted} rows')

        # ---- PHASE 2: TRANSFORM (Python) ----
        logger.info(f'[PHASE 2] TRANSFORM — {tenant_id}')
        df = transform_sales(df, tenant_id)
        rows_transformed = len(df)
        rows_rejected = rows_extracted - rows_transformed
        logger.info(f'[PHASE 2] TRANSFORM complete: {rows_transformed} rows, {rows_rejected} rejected')

        # Reload transformed data vào Staging
        if not df.empty:
            load_to_staging(conn, df, 'STG_SalesRaw')

        # ---- PHASE 3: LOAD DIMENSIONS ----
        logger.info(f'[PHASE 3] LOAD DIMENSIONS — {tenant_id}')
        run_sp(conn, 'usp_Load_DimProduct', {'TenantID': tenant_id})  # Shared
        run_sp(conn, 'usp_Load_DimCustomer', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Load_DimStore', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Load_DimEmployee', {'TenantID': tenant_id})

        # ---- PHASE 4: LOAD FACTS ----
        logger.info(f'[PHASE 4] LOAD FACTS — {tenant_id}')
        run_sp(conn, 'usp_Transform_FactSales',
               {'BatchDate': batch_str, 'TenantID': tenant_id})
        run_sp(conn, 'usp_Transform_FactInventory',
               {'BatchDate': batch_str, 'TenantID': tenant_id})
        run_sp(conn, 'usp_Transform_FactPurchase',
               {'BatchDate': batch_str, 'TenantID': tenant_id})

        # ---- PHASE 5: REFRESH DATA MART ----
        logger.info(f'[PHASE 5] REFRESH DATA MART — {tenant_id}')
        run_sp(conn, 'usp_Refresh_DM_SalesSummary', {'TenantID': tenant_id})
        run_sp(conn, 'usp_Refresh_DM_CustomerRFM', {'TenantID': tenant_id})

        # ---- PHASE 6: UPDATE WATERMARK + LOG ----
        logger.info(f'[PHASE 6] FINALIZE — {tenant_id}')
        update_watermark(conn, tenant_id, table_name, 'SUCCESS')
        write_etl_log(
            conn, tenant_id, batch_date, 'FactSales', 'SUCCESS',
            rows_extracted, rows_transformed, rows_rejected
        )

        logger.info(f'ETL SUCCESS: {tenant_id} | {batch_str}')
        conn.close()
        return True

    except Exception as ex:
        logger.error(f'ETL FAILED: {tenant_id} — {ex}', exc_info=True)
        if conn:
            try:
                update_watermark(conn, tenant_id, table_name, 'FAILED')
                write_etl_log(
                    conn, tenant_id, batch_date, 'FactSales', 'FAILED',
                    error_msg=str(ex)
                )
                conn.close()
            except Exception:
                pass

        # Alert ngay lập tức
        alert(tenant_id, batch_str, str(ex))
        return False


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


def run_all_etl(batch_date: date = None) -> dict:
    """
    Chạy ETL cho tất cả tenant đang hoạt động.

    Args:
        batch_date: Ngày cần xử lý (mặc định = hôm nay)

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
        file_path = tenant['file_path'] or f'./data/{tenant_id}/'

        # Tìm file Excel trong thư mục
        import glob
        excel_files = (
            glob.glob(os.path.join(file_path, '*.xlsx')) +
            glob.glob(os.path.join(file_path, '*.xls')) +
            glob.glob(os.path.join(file_path, '*.csv'))
        )

        if not excel_files:
            logger.warning(f'[{tenant_id}] No data files found in {file_path}')
            results[tenant_id] = None
            continue

        # Chạy ETL với file đầu tiên tìm được (có thể mở rộng để xử lý nhiều file)
        success = run_etl_for_tenant(tenant_id, excel_files[0], batch_date)
        results[tenant_id] = success

    return results


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

        file_path = tenant_info['file_path'] or f'./data/{args.tenant}/'
        import glob
        files = glob.glob(os.path.join(file_path, '*.xlsx')) + \
                glob.glob(os.path.join(file_path, '*.xls'))
        if not files:
            logger.error(f'No files found for tenant {args.tenant}')
            sys.exit(1)

        run_etl_for_tenant(args.tenant, files[0], batch_date)
    else:
        # Chạy cho tất cả tenant
        results = run_all_etl(batch_date)
        success_count = sum(1 for v in results.values() if v is True)
        fail_count   = sum(1 for v in results.values() if v is False)
        logger.info(f'ETL Summary: {success_count} success, {fail_count} failed')
        sys.exit(0 if fail_count == 0 else 1)
