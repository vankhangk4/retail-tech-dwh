# Monitoring & Alerting — DWH Multi-Tenant

Hệ thống giám sát tự động cho ETL Pipeline, Database Health, và Service Availability.

## 📁 Cấu trúc thư mục

```
monitoring/
├── monitoring.py              # Centralized alerting module
├── health_check.sh           # Service health check script
├── backup_dwh.sh             # Database backup script (also in sql/)
└── README.md                 # This file
```

## 🔔 Alert Functions

### 1. ETL Failure Alert
**Khi:** ETL pipeline thất bại\
**Gửi:** Email + Slack\
**Nội dung:** Tenant ID, batch date, error message, log location

```python
from monitoring.monitoring import alert_etl_failed

alert_etl_failed(
    tenant_id='STORE_HN',
    batch_date='2026-05-05',
    error_msg='Database connection timeout'
)
```

### 2. ETL Timeout Warning
**Khi:** ETL chạy > 45 phút (NFR-12)\
**Gửi:** Email + Slack\
**Nội dung:** Thời gian chạy, nguyên nhân có thể

```python
from monitoring.monitoring import alert_etl_timeout

alert_etl_timeout(
    tenant_id='STORE_HN',
    batch_date='2026-05-05',
    duration_minutes=50
)
```

### 3. High Error Rate Alert
**Khi:** Tỷ lệ lỗi > 0.1% (NFR-04)\
**Gửi:** Email + Slack\
**Nội dung:** Tổng bản ghi, bản ghi lỗi, tỷ lệ %

```python
from monitoring.monitoring import alert_high_error_rate

alert_high_error_rate(
    tenant_id='STORE_HN',
    batch_date='2026-05-05',
    total_rows=100000,
    error_rows=200,
    error_pct=0.2
)
```

### 4. Service Down Alert
**Khi:** Superset, SQL Server hoặc API không hoạt động\
**Gửi:** Email + Slack (CRITICAL)\
**Nội dung:** Service name, status code, error

```python
from monitoring.monitoring import alert_service_down

alert_service_down(
    service_name='Superset',
    status_code=503,
    error='Connection timeout'
)
```

## ⚙️ Configuration

### Email Setup (Gmail SMTP)

```bash
# 1. Enable 2FA on Google Account
#    https://myaccount.google.com/security

# 2. Generate App Password (16 characters)
#    https://myaccount.google.com/apppasswords

# 3. Update .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-16-char-app-password
ALERT_FROM_EMAIL=dwh-alerts@company.com
ALERT_TO_EMAIL=admin@company.com
```

### Slack Setup

```bash
# 1. Go to https://api.slack.com/messaging/webhooks
# 2. Create new Incoming Webhook
# 3. Copy webhook URL
# 4. Update .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

## 🔄 Integration Points

### ETL Orchestrator
```python
# etl/orchestrator/main_etl.py
from monitoring.monitoring import alert_etl_failed, alert_etl_timeout, alert_high_error_rate

try:
    # ETL logic
    run_etl_for_tenant(tenant_id, data_dir, batch_date)
except Exception as ex:
    alert_etl_failed(tenant_id, batch_str, str(ex))
    
# Check error rate
error_pct = (total_errors / total_rows) * 100
if error_pct > 0.1:
    alert_high_error_rate(tenant_id, batch_date, total_rows, total_errors, error_pct)
```

### Health Check
```python
# monitoring/health_check.py
import requests
from monitoring.monitoring import alert_service_down

services = {
    'API': 'https://dwh.company.com/api/health',
    'Superset': 'https://dwh.company.com/superset/',
    'Database': 'localhost:1433'
}

for service_name, url in services.items():
    try:
        response = requests.get(url, timeout=10)
        if response.status_code not in [200, 302]:
            alert_service_down(service_name, response.status_code)
    except Exception as e:
        alert_service_down(service_name, error=str(e))
```

## 📅 Scheduled Tasks

### Using Cron

```bash
# Health check every 5 minutes
*/5 * * * * /home/user/dwh_project/monitoring/health_check.sh

# Backup every day
0 0 * * * /home/user/dwh_project/sql/backup_dwh.sh

# Log cleanup every week (keep 30 days)
0 2 * * 0 find /data/dwh/logs -name '*.log' -mtime +30 -delete
```

### Using APScheduler

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import subprocess

scheduler = BackgroundScheduler()

# Health check every 5 minutes
scheduler.add_job(
    lambda: subprocess.run(['bash', 'monitoring/health_check.sh']),
    CronTrigger(minute='*/5')
)

# Backup on Sunday at midnight
scheduler.add_job(
    lambda: subprocess.run(['bash', 'sql/backup_dwh.sh']),
    CronTrigger(day_of_week=6, hour=0, minute=0)
)

scheduler.start()
```

## 📊 Monitoring Dashboard

### View ETL Logs via API

```bash
# Get all ETL logs
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://dwh.company.com/api/management/etl/logs

# Filter by tenant
curl -H "Authorization: Bearer $JWT_TOKEN" \
  "https://dwh.company.com/api/management/etl/logs?tenant_id=STORE_HN"

# Filter by status
curl -H "Authorization: Bearer $JWT_TOKEN" \
  "https://dwh.company.com/api/management/etl/logs?status=FAILED"
```

### View Watermarks

```bash
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://dwh.company.com/api/management/etl/watermarks
```

### Direct Database Query

```sql
-- Last 10 ETL runs
SELECT TOP 10 
  TenantID, 
  SourceTable, 
  RunStatus, 
  RowsExtracted, 
  RowsInserted, 
  DurationSeconds,
  CreatedAt
FROM ETLLogs
ORDER BY CreatedAt DESC;

-- Failed runs
SELECT * 
FROM ETLLogs 
WHERE RunStatus = 'FAILED' 
ORDER BY CreatedAt DESC;

-- Error details
SELECT * 
FROM STG_ErrorLog 
WHERE TenantID = 'STORE_HN' 
ORDER BY LoadDatetime DESC;
```

## 🚨 Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| ETL Duration | > 45 min | Warn via email/Slack |
| Error Rate | > 0.1% | Alert via email/Slack |
| Service Down | HTTP != 200/302 | CRITICAL alert |
| Database Size | > 200 GB | Alert (may need to archive) |
| Backup Age | > 28 days | Alert (check retention) |
| SSL Certificate | < 30 days to expiry | Remind to renew |

## 🔧 Troubleshooting

### Email alerts not sending
```bash
# Check SMTP configuration
docker-compose exec api python3 << 'EOF'
import os, smtplib
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
print('✓ SMTP login successful')
EOF
```

### Slack webhook not responding
```bash
# Test webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-type: application/json' \
  -d '{"text":"Test message"}'
```

### Service health check failing
```bash
# Manual health check
curl -v https://dwh.company.com/api/health
curl -v https://dwh.company.com/superset/

# Check Docker logs
docker-compose logs api
docker-compose logs superset
```

## 📚 References

- [Python smtplib](https://docs.python.org/3/library/smtplib.html)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [Cron Format](https://crontab.guru/)
