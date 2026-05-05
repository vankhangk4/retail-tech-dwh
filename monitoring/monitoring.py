# ============================================================
# FILE: monitoring/monitoring.py
# Mô tả: Centralized alerting module cho ETL Pipeline
# ============================================================

import os
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from datetime import datetime

logger = logging.getLogger(__name__)

# ---- Configuration ----
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
ALERT_FROM = os.environ.get('ALERT_FROM_EMAIL', 'etl@company.com')
ALERT_TO = os.environ.get('ALERT_TO_EMAIL', 'admin@company.com')
SLACK_WEBHOOK = os.environ.get('SLACK_WEBHOOK_URL', '')


def send_email_alert(subject: str, body: str) -> None:
    """
    Gửi email alert khi ETL thất bại hoặc cảnh báo.

    Args:
        subject: Tiêu đề email
        body: Nội dung email
    """
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
    """
    Gửi Slack alert qua Webhook khi ETL thất bại.

    Args:
        message: Nội dung tin nhắn Slack
    """
    if not SLACK_WEBHOOK:
        logger.debug('Slack webhook not configured')
        return

    try:
        requests.post(
            SLACK_WEBHOOK,
            json={'text': f':rotating_light: {message}'},
            timeout=10
        )
        logger.info(f'Slack alert sent')
    except Exception as e:
        logger.error(f'Failed to send Slack alert: {e}')


def alert_etl_failed(tenant_id: str, batch_date: str, error_msg: str) -> None:
    """
    Gửi alert email + Slack khi ETL pipeline thất bại.

    Args:
        tenant_id: Mã tenant
        batch_date: Ngày batch (YYYY-MM-DD)
        error_msg: Thông báo lỗi chi tiết
    """
    subject = f'ETL FAILED: {tenant_id} @ {batch_date}'
    body = (
        f'DWH ETL Pipeline Failed\n'
        f'================================\n'
        f'Tenant: {tenant_id}\n'
        f'Batch Date: {batch_date}\n'
        f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'================================\n'
        f'Error Message:\n{error_msg}\n'
        f'\n'
        f'Action: Check ETL logs in {tenant_id}/logs/ directory\n'
        f'Watermark will be preserved for retry on next run.'
    )

    send_email_alert(subject, body)
    send_slack_alert(f'{subject}\n{error_msg[:200]}')


def alert_etl_timeout(tenant_id: str, batch_date: str, duration_minutes: int) -> None:
    """
    Cảnh báo khi ETL chạy quá lâu (> 45 phút theo NFR-12).

    Args:
        tenant_id: Mã tenant
        batch_date: Ngày batch
        duration_minutes: Thời gian chạy (phút)
    """
    subject = f'ETL TIMEOUT WARNING: {tenant_id} @ {batch_date}'
    body = (
        f'DWH ETL Pipeline is taking longer than expected\n'
        f'================================\n'
        f'Tenant: {tenant_id}\n'
        f'Batch Date: {batch_date}\n'
        f'Duration: {duration_minutes} minutes (threshold: 45 min)\n'
        f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'================================\n'
        f'Possible causes:\n'
        f'  - Large volume of data in source files\n'
        f'  - Database performance issues\n'
        f'  - Network latency\n'
        f'\n'
        f'Action: Monitor logs and check database health'
    )

    send_email_alert(subject, body)
    send_slack_alert(f'⏱️ {subject}')


def alert_high_error_rate(tenant_id: str, batch_date: str,
                          total_rows: int, error_rows: int, error_pct: float) -> None:
    """
    Cảnh báo khi tỷ lệ lỗi vượt ngưỡng (> 0.1% theo NFR-04).

    Args:
        tenant_id: Mã tenant
        batch_date: Ngày batch
        total_rows: Tổng số bản ghi
        error_rows: Số bản ghi lỗi
        error_pct: Tỷ lệ lỗi (%)
    """
    subject = f'ETL HIGH ERROR RATE: {tenant_id} @ {batch_date} ({error_pct:.2f}%)'
    body = (
        f'DWH ETL Pipeline has high error rate\n'
        f'================================\n'
        f'Tenant: {tenant_id}\n'
        f'Batch Date: {batch_date}\n'
        f'Total Rows: {total_rows:,}\n'
        f'Error Rows: {error_rows:,}\n'
        f'Error Rate: {error_pct:.2f}% (threshold: 0.1%)\n'
        f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
        f'================================\n'
        f'Action: Review STG_ErrorLog table for details\n'
        f'  SELECT * FROM STG_ErrorLog WHERE TenantID = \'{tenant_id}\''
    )

    send_email_alert(subject, body)
    send_slack_alert(f'⚠️ {subject}')


def alert_service_down(service_name: str, status_code: int = None, error: str = None) -> None:
    """
    Cảnh báo khi service không hoạt động (Superset, SQL Server, etc).

    Args:
        service_name: Tên service (e.g., 'Superset', 'SQL Server')
        status_code: HTTP status code (nếu có)
        error: Thông báo lỗi
    """
    subject = f'SERVICE DOWN: {service_name}'
    body = (
        f'Critical Service is Unreachable\n'
        f'================================\n'
        f'Service: {service_name}\n'
        f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    )

    if status_code:
        body += f'Status Code: {status_code}\n'

    if error:
        body += f'Error: {error}\n'

    body += (
        f'================================\n'
        f'Action: Check service health and connectivity\n'
        f'Impact: ETL pipeline may be blocked\n'
    )

    send_email_alert(subject, body)
    send_slack_alert(f'🔴 {subject} - CRITICAL')


if __name__ == '__main__':
    # Test alerts (requires proper SMTP/Slack config)
    print('Monitoring module loaded successfully')
    print(f'SMTP configured: {bool(SMTP_USER and SMTP_PASS)}')
    print(f'Slack webhook configured: {bool(SLACK_WEBHOOK)}')
