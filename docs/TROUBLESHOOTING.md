# Hướng dẫn xử lý sự cố — DWH Multi-Tenant System

**Cập nhật:** 2026-05-08

---

## Mục lục

1. [Khởi động hệ thống](#1-khởi-động-hệ-thống)
2. [Lỗi Authentication](#2-lỗi-authentication)
3. [Lỗi ETL Pipeline](#3-lỗi-etl-pipeline)
4. [Lỗi Superset / Dashboard](#4-lỗi-superset--dashboard)
5. [Lỗi Database / SQL Server](#5-lỗi-database--sql-server)
6. [Lỗi Tenant / RLS](#6-lỗi-tenant--rls)
7. [Monitoring & Alerts](#7-monitoring--alerts)
8. [Câu lệnh debug thường dùng](#8-câu-lệnh-debug-thường-dùng)

---

## 1. Khởi động hệ thống

### Kiểm tra tất cả services đang chạy

```bash
docker-compose ps
```

Kết quả mong đợi:
```
NAME          STATUS    PORTS
mssql         Up        0.0.0.0:1433->1433/tcp
api           Up        0.0.0.0:8000->8000/tcp
frontend      Up        0.0.0.0:5000->5000/tcp
superset      Up        0.0.0.0:8088->8088/tcp
redis         Up        6379/tcp
```

### Service không khởi động được

```bash
# Xem logs của service cụ thể
docker-compose logs api --tail=50
docker-compose logs mssql --tail=50
docker-compose logs superset --tail=50

# Restart một service
docker-compose restart api

# Rebuild và restart
docker-compose up --build api
```

### Lỗi port đã bị dùng

```bash
# Tìm process dùng port 8000
lsof -i :8000
# Hoặc trên Windows:
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>
```

---

## 2. Lỗi Authentication

### HTTP 401 — Sai tài khoản hoặc mật khẩu

**Nguyên nhân:** Username/password không đúng, hoặc user chưa tồn tại trong DB.

**Kiểm tra:**
```sql
SELECT UserID, Username, IsActive, Role, TenantID
FROM AppUsers WHERE Username = 'tên_user_của_bạn';
```

**Khắc phục:**
- Kiểm tra lại username (case-sensitive)
- Reset password qua API:
```bash
curl -X PUT http://localhost:8000/api/admin/users/reset-password \
  -H "Authorization: Bearer <superadmin_token>" \
  -d '{"user_id": 5, "new_password": "NewPass123!"}'
```

### HTTP 401 — Token đã hết hạn

**Nguyên nhân:** Access token hết hạn sau 8 giờ.

**Khắc phục:** Dùng refresh token để lấy access token mới:
```bash
curl -X POST http://localhost:8000/api/refresh \
  -d "refresh_token=<refresh_token_của_bạn>"
```

### HTTP 403 — Tài khoản bị khoá

```sql
UPDATE AppUsers SET IsActive = 1 WHERE Username = 'tên_user';
```

### HTTP 403 — Tenant hết hạn

```sql
-- Kiểm tra ngày hết hạn
SELECT TenantID, ExpiresAt FROM Tenants WHERE TenantID = 'STORE_HN';

-- Gia hạn
UPDATE Tenants
SET ExpiresAt = DATEADD(YEAR, 1, GETDATE())
WHERE TenantID = 'STORE_HN';
```

### HTTP 500 — Fatal error khi đăng nhập Superset

**Nguyên nhân:** Thiếu field `"provider": "db"` trong body.

**Đúng:**
```bash
curl -X POST http://localhost:8088/api/v1/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin","provider":"db"}'
```

---

## 3. Lỗi ETL Pipeline

### ETL không chạy được

**Kiểm tra logs:**
```bash
docker-compose logs api --tail=100 | grep ETL
```

**Kiểm tra ETLLogs:**
```sql
SELECT TOP 10 * FROM ETLLogs
ORDER BY StartTime DESC;
```

### ETL bị FAILED

**Tìm nguyên nhân:**
```sql
-- Xem lỗi chi tiết
SELECT TenantID, ProcessType, RowsError, ErrorMessage, StartTime
FROM ETLLogs
WHERE RunStatus = 'FAILED'
ORDER BY StartTime DESC;

-- Xem từng dòng lỗi
SELECT * FROM STG_ErrorLog
WHERE CreatedAt > DATEADD(HOUR, -1, GETDATE())
ORDER BY CreatedAt DESC;
```

**Nguyên nhân phổ biến:**
| Lỗi | Nguyên nhân | Khắc phục |
|-----|-------------|-----------|
| FK violation | MaSP/MaKH không tồn tại trong Dim table | Thêm dữ liệu Dim trước khi load Fact |
| Duplicate key | Business key trùng | ETL tự dedup, kiểm tra STG_ErrorLog |
| NULL required field | Cột bắt buộc bị null | Kiểm tra file nguồn, thêm default value |
| Date parse error | Format ngày sai | Đảm bảo format DD/MM/YYYY |
| File not found | Đường dẫn file sai | Kiểm tra FilePath trong Tenants table |

### ETL bị stuck / RUNNING mãi không xong

```sql
-- Reset watermark bị stuck
UPDATE ETL_Watermark
SET Status = 'FAILED'
WHERE Status = 'RUNNING'
  AND TenantID = 'STORE_HN';
```

### Trigger ETL thủ công

```bash
curl -X POST http://localhost:8000/api/etl/trigger/STORE_HN \
  -H "Authorization: Bearer <admin_token>"
```

### ETL chạy xong nhưng data chưa xuất hiện trên Dashboard

**Vấn đề:** Data Mart chưa được refresh.

**Khắc phục:** Gọi stored procedure refresh thủ công:
```sql
EXEC usp_Refresh_DM_SalesSummary;
EXEC usp_Refresh_DM_CustomerRFM;
EXEC usp_Refresh_DM_InventoryAlert;
```

---

## 4. Lỗi Superset / Dashboard

### HTTP 403 khi gọi Superset API

**Nguyên nhân:** Superset chưa được khởi tạo đúng.

**Khắc phục:**
```bash
docker-compose exec superset superset init
docker-compose restart superset
```

### Dashboard trắng / không load được

**Kiểm tra guest token:**
```bash
curl http://localhost:8000/api/dashboard-token \
  -H "Authorization: Bearer <access_token>" \
  -G -d "dashboard_id=1"
```

Nếu trả về 502 → Superset chưa khởi động hoặc không kết nối được.

**Kiểm tra Superset health:**
```bash
curl http://localhost:8088/health
# Mong đợi: "OK"
```

### Dataset không có data / query fail

**Kiểm tra kết nối Superset → SQL Server:**
1. Vào Superset admin `http://localhost:8088`
2. Settings → Database Connections → Test connection

**Sync dataset columns:**
```bash
docker-compose exec superset python /app/scripts/sync_dataset_columns.py
```

### Charts bị lỗi cấu hình

```bash
# Chạy các fix scripts
docker-compose exec superset python /app/scripts/fix_chart_params.py
docker-compose exec superset python /app/scripts/fix_chart_metrics.py
docker-compose exec superset python /app/scripts/fix_positions.py
```

### RLS không hoạt động (tenant thấy data của tenant khác)

**Kiểm tra RLS rules:**
```bash
curl http://localhost:8088/api/v1/rowlevelsecurity/ \
  -H "Authorization: Bearer <superset_admin_token>"
```

**Re-provision RLS:**
```bash
docker-compose exec superset python /app/scripts/provision_v2.py
```

---

## 5. Lỗi Database / SQL Server

### Không kết nối được SQL Server

**Kiểm tra container:**
```bash
docker-compose logs mssql --tail=20
docker exec -it mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASSWORD" -Q "SELECT 1"
```

**Kiểm tra từ máy host:**
```bash
telnet localhost 1433
```

### Database không tồn tại

```bash
# Chạy lại init script
docker-compose run --rm mssql-init
```

### Schema outdated / thiếu bảng

```bash
# Chạy migration
docker exec -i mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASSWORD" \
  -i /sql/migrations/add_tenant_expires_at.sql
```

### Performance chậm

**Kiểm tra indexes:**
```sql
-- Kiểm tra index fragmentation
SELECT 
    OBJECT_NAME(i.object_id) AS TableName,
    i.name AS IndexName,
    ps.avg_fragmentation_in_percent
FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
JOIN sys.indexes i ON ps.object_id = i.object_id AND ps.index_id = i.index_id
WHERE ps.avg_fragmentation_in_percent > 30
ORDER BY ps.avg_fragmentation_in_percent DESC;

-- Rebuild indexes bị phân mảnh
ALTER INDEX ALL ON FactSales REBUILD;
```

---

## 6. Lỗi Tenant / RLS

### Thêm tenant mới nhưng không thấy data trên Superset

**Vấn đề:** RLS rule chưa được tạo cho tenant mới.

**Khắc phục:**
```bash
# Re-provision toàn bộ tenants
curl -X POST http://localhost:8000/api/superset/provision-all \
  -H "Authorization: Bearer <superadmin_token>"
```

### Tenant A thấy được data của Tenant B (RLS bị bypass)

**Kiểm tra ngay:**
```sql
-- Kiểm tra FactSales có đúng TenantID không
SELECT TenantID, COUNT(*) AS Rows
FROM FactSales
GROUP BY TenantID;

-- Kiểm tra RLS view
SELECT TOP 5 * FROM v_FactSales_ByTenant;
```

**Kiểm tra Superset RLS:**
1. Vào Superset → Security → Row Level Security
2. Kiểm tra mỗi dataset đều có clause `TenantID = 'X'` cho từng tenant

### Tenant bị khoá do hết hạn

```sql
-- Gia hạn 1 năm
UPDATE Tenants
SET ExpiresAt = DATEADD(YEAR, 1, GETDATE()), IsActive = 1
WHERE TenantID = 'STORE_HN';
```

---

## 7. Monitoring & Alerts

### Không nhận được email alert khi ETL fail

**Kiểm tra SMTP config trong `.env`:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASS=your_app_password
ALERT_EMAIL=admin@company.com
```

**Test alert thủ công:**
```python
from monitoring.monitoring import send_email_alert
send_email_alert(
    subject='Test Alert',
    body='Đây là email test từ hệ thống DWH.'
)
```

### Không nhận được Slack alert

**Kiểm tra SLACK_WEBHOOK_URL trong `.env`:**
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
```

**Test Slack:**
```python
from monitoring.monitoring import send_slack_alert
send_slack_alert('Test message từ DWH system')
```

---

## 8. Câu lệnh debug thường dùng

### Xem logs realtime

```bash
# Tất cả services
docker-compose logs -f

# Chỉ API
docker-compose logs -f api

# Chỉ ETL (trong container API)
docker-compose exec api tail -f /app/logs/etl_$(date +%Y%m%d).log
```

### Reset toàn bộ (chú ý: xóa data)

```bash
# Dừng và xóa volumes
docker-compose down -v

# Rebuild từ đầu
docker-compose up --build
```

### Backup & Restore

```bash
# Backup thủ công
docker-compose exec mssql python /sql/backup_dwh.py --type full

# Xem danh sách backup
ls -la /backup/

# Restore (thay <backup_file> bằng tên file .bak)
docker exec -i mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASSWORD" \
  -Q "RESTORE DATABASE DWH_MultiTenant FROM DISK='/backup/<backup_file>.bak' WITH REPLACE"
```

### Kiểm tra health tất cả services

```bash
curl http://localhost:8000/health    # API
curl http://localhost:8088/health    # Superset
curl http://localhost:5000/health    # Frontend (nếu có)
```

### Xem ETL watermark

```sql
SELECT TenantID, TableName, LastProcessedAt, Status
FROM ETL_Watermark
ORDER BY TenantID, TableName;
```

### Force refresh Data Mart

```sql
EXEC usp_Refresh_DM_SalesSummary;
EXEC usp_Refresh_DM_CustomerRFM;
EXEC usp_Refresh_DM_InventoryAlert;
SELECT * FROM DM_SalesSummary ORDER BY SalesYear DESC, SalesMonth DESC;
```
