# Hướng dẫn Triển khai Production - DWH Multi-Tenant

> Tài liệu này hướng dẫn triển khai hệ thống DWH trên môi trường production với HTTPS, backup, monitoring

## 📋 Tổng quan

Hệ thống bao gồm:
- **Nginx**: Reverse proxy + HTTPS (port 443)
- **SQL Server**: Database (port 1433)
- **API**: FastAPI Auth Gateway (port 8000)
- **Superset**: BI Dashboard (port 8088)
- **Frontend**: Flask web UI (port 5000)

## 🚀 Bước 1: Chuẩn bị máy chủ

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create directories
sudo mkdir -p /backups/dwh /data/sql /data/superset
sudo chmod 755 /backups/dwh /data/sql /data/superset
```

## 🔐 Bước 2: Cấu hình SSL với Let's Encrypt

```bash
cd /home/user/dwh_project

# Tạo thư mục certbot
mkdir -p nginx/certbot/{conf,www}

# Lấy chứng chỉ SSL (lần đầu)
docker-compose -f nginx/docker-compose.yml run --rm certbot certonly \
  --webroot \
  -w /var/www/certbot \
  -d dwh.company.com \
  --email admin@company.com \
  --agree-tos \
  --no-eff-email

# Xác nhận chứng chỉ tạo thành công
ls -la nginx/certbot/conf/live/dwh.company.com/
```

## 🐳 Bước 3: Khởi động hệ thống

```bash
# Cập nhật .env với cấu hình production
vi .env

# Khởi động tất cả service
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps
docker-compose logs -f

# Kiểm tra HTTPS
curl -I https://dwh.company.com/health
```

## 💾 Bước 4: Cấu hình Backup tự động

### Option A: Shell script + cron

```bash
# Copy backup script
chmod +x sql/backup_dwh.sh

# Thêm vào crontab
crontab -e

# Thêm các dòng sau:
# Sunday 00:00 - Full backup
0 0 * * 0 /home/user/dwh_project/sql/backup_dwh.sh

# Weekdays 00:30 - Differential backup
30 0 * * 1-5 /home/user/dwh_project/sql/backup_dwh.sh

# Every 4 hours - Transaction log backup
0 */4 * * * /home/user/dwh_project/sql/backup_dwh.sh
```

### Option B: Python + APScheduler

```bash
# Install APScheduler
pip install APScheduler

# Tạo daemon script (scheduler.py)
cat > sql/scheduler_backup.py << 'EOF'
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def run_backup(backup_type):
    subprocess.run(['python3', 'sql/backup_dwh.py', backup_type])

# Sunday 00:00 - Full
scheduler.add_job(run_backup, 'cron', day_of_week=6, hour=0, minute=0, args=['full'])

# Monday & Thursday 00:30 - Differential
scheduler.add_job(run_backup, 'cron', day_of_week='0,3', hour=0, minute=30, args=['differential'])

# Every 4 hours - Log
scheduler.add_job(run_backup, 'cron', hour='*/4', minute=0, args=['log'])

scheduler.start()
logger.info('Backup scheduler started')

try:
    while True: pass
except KeyboardInterrupt:
    scheduler.shutdown()
EOF

# Chạy scheduler trong background hoặc systemd service
python3 sql/scheduler_backup.py &
```

## 📊 Bước 5: Cấu hình Monitoring & Alerting

### Email Alert (SMTP Gmail)

```bash
# Cập nhật .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password  # Use 16-char app password, not regular password
ALERT_FROM_EMAIL=dwh-alerts@company.com
ALERT_TO_EMAIL=admin@company.com
```

### Slack Alert

```bash
# Tạo Webhook URL từ Slack
# https://api.slack.com/messaging/webhooks

# Cập nhật .env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Health check script

```bash
cat > monitoring/health_check.sh << 'EOF'
#!/bin/bash

SERVICES=(
  "https://dwh.company.com/health"
  "https://dwh.company.com/api/health"
  "https://dwh.company.com/superset"
)

for service in "${SERVICES[@]}"; do
  if curl -s -o /dev/null -w "%{http_code}" "$service" | grep -q "200\|302"; then
    echo "✓ $service is UP"
  else
    echo "✗ $service is DOWN"
    # Send alert
  fi
done
EOF

chmod +x monitoring/health_check.sh

# Chạy mỗi 5 phút
*/5 * * * * /home/user/dwh_project/monitoring/health_check.sh
```

## 📈 Bước 6: Kiểm tra Hệ thống

```bash
# Kiểm tra database
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "SELECT name FROM sys.databases;" -C -b

# Kiểm tra ETL logs
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "SELECT TOP 10 * FROM ETLLogs ORDER BY CreatedAt DESC;" -C -b

# Kiểm tra tenant
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "SELECT TenantID, TenantName, IsActive FROM Tenants;" -C -b

# Kiểm tra API
curl -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' \
  https://dwh.company.com/api/auth/login

# Kiểm tra Superset
curl -s https://dwh.company.com/superset/ | head -20
```

## 🔄 Bước 7: Backup Recovery (Disaster Recovery)

### Restore Full Backup

```bash
# 1. Copy backup file vào container
docker cp /backups/dwh/dwh_full_20260505_000000.bak dwh_mssql:/var/opt/mssql/backup/

# 2. Restore từ backup
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "RESTORE DATABASE DWH_MultiTenant FROM DISK = '/var/opt/mssql/backup/dwh_full_20260505_000000.bak' WITH REPLACE;"

# 3. Kiểm tra recovery
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "RESTORE HEADERONLY FROM DISK = '/var/opt/mssql/backup/dwh_full_20260505_000000.bak';"
```

## 🛡️ Bước 8: Security Hardening

```bash
# 1. Thay đổi mật khẩu mặc định
docker-compose exec api python3 -c "
from passlib.context import CryptContext
import os
pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
new_pass = pwd_ctx.hash('your-strong-password')
print(f'Password hash: {new_pass}')
"

# 2. Cập nhật .env với mật khẩu mạnh
MSSQL_SA_PASSWORD=YourStrongPassword123!@#
JWT_SECRET_KEY=your-256-bit-random-secret-key-min-32-chars
SUPERSET_ADMIN_PWD=YourStrongPassword123!@#

# 3. Firewall rules
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# 4. SSH key authentication (disable password login)
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

## 📝 Maintenance Tasks

### Hàng ngày
- ✓ Xem ETL logs qua API: `GET /api/management/etl/logs`
- ✓ Kiểm tra watermark: `GET /api/management/etl/watermarks`
- ✓ Monitor disk space: `df -h`

### Hàng tuần
- ✓ Review backup files: `ls -lh /backups/dwh/`
- ✓ Test restore procedure
- ✓ Check SSL certificate expiry: `ssl-cert-check -d dwh.company.com`

### Hàng tháng
- ✓ Update system packages: `sudo apt update && apt upgrade`
- ✓ Update Docker images: `docker-compose pull && docker-compose up -d`
- ✓ Analyze database: `DBCC DBREINDEX ()`
- ✓ Review monitoring logs

## 🚨 Troubleshooting

### ETL Failed
```bash
# Check logs
docker-compose logs api | tail -50
docker-compose logs mssql | tail -50

# Check watermark status
SELECT * FROM ETL_Watermark WHERE LastRunStatus = 'FAILED';

# Retry ETL
POST /api/management/etl/trigger/STORE_HN
```

### SSL Certificate Issues
```bash
# Check certificate validity
docker-compose -f nginx/docker-compose.yml run --rm certbot \
  --webroot -w /var/www/certbot \
  --agree-tos \
  -d dwh.company.com

# Manual renewal
docker-compose -f nginx/docker-compose.yml run --rm certbot \
  renew --force-renewal
```

### Database Connection Issues
```bash
# Test connectivity
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "SELECT 1;"

# Check database size
docker-compose exec mssql sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD \
  -Q "EXEC sp_spaceused;"
```

## 📞 Support

- Email: admin@company.com
- Slack: #dwh-support
- GitHub Issues: https://github.com/your-org/dwh_project/issues
