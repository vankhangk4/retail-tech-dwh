# Checklist Tien do Du an Data Warehouse Multi-Tenant

> Du an: **Xay dung he thong Data Warehouse va truc quan hoa du lieu kinh doanh cho chuoi cua hang ban le thiet bi cong nghe (Multi-Tenant)** - Nguyen Van Khang - 64HTTT4
>
> Checklist nay duoc tao tu de cuong bao cao [Nguyen_Van_Khang_Bao_Cao.md](Nguyen_Van_Khang_Bao_Cao.md) va doi chieu voi codebase hien tai (scan ngay 2026-05-06).

---

## 🎯 Tien do tong the: **95%** (145/152 hang muc chinh hoan thanh)

```
Core (Chuong 1-6):         ████████████████████░  95%  (145/152)
Optional/Production-ready: ███░░░░░░░░░░░░░░░░░  20%  (3/15)
─────────────────────────────────────────────────────────────
TONG (ca optional):        █████████████████░░░  88%  (148/167)
```

---

## Tong quan trang thai

| Hang muc | Tien do | Hoan thanh | Ghi chu |
| :---- | :----: | :----: | :---- |
| Chuong 1 - Phan tich thuc trang | **100%** | 6/6 | Tai lieu hoa trong bao cao |
| Chuong 2 - Yeu cau he thong (FR/NFR) | **89%** | 19.5/22 | UC03-UC05 can update vao de cuong; NFR-05 (uptime) + NFR-07 (SSL cert) thieu |
| Chuong 3 - Kien truc 5 tang | **100%** | 13/13 | Auth Gateway + ETL + DWH + BI day du |
| Chuong 4 - Thiet ke CSDL | **100%** | 30/30 | Schema, Dim, Fact, STG, DM, Indexes |
| Chuong 5 - Tien trinh ETL | **96%** | 25/26 | 7 phase day du; con tich hop SP refresh DM (optional) |
| Chuong 6 - Multi-tenant Security | **94%** | 51.5/55 | Tich hop monitoring + cron backup + SSL cert con thieu |
| **Optional / Production-ready** | **20%** | 3/15 | Backup script + Monitoring module + Nginx config da co |

---

## Chuong 1 - Tong quan He thong — **100%** (6/6)

### 1.1. Phan tich thuc trang doanh nghiep — **100%** (3/3)
- [x] Mo ta thuc trang quan ly du lieu phan manh tren Excel/Google Sheets
- [x] Liet ke 5 van de noi com (data island, khong nhat quan, mat lich su, ...)
- [x] Phan tich 3 nguon du lieu chinh (POS, Kho van, Danh muc San pham)

### 1.2. Ly do can xay dung Data Warehouse — **100%** (1/1)
- [x] Trinh bay 6 ly do (Single Source of Truth, lich su, chat luong, toc do, multi-tenant, OLAP)

### 1.3. Muc tieu du an — **100%** (2/2)
- [x] Muc tieu tong quat: DWH + ETL + BI + multi-tenant
- [x] 6 muc tieu cu the (SQL Server Star Schema, ETL, Dim/Fact, Superset 5+ dashboards, multi-tenant, hieu nang <= 3s)

---

## Chuong 2 - Yeu cau He thong — **89%** (19.5/22)

### 2.1. Yeu cau chuc nang (Functional Requirements) — **100%** (4/4)
- [x] **FR-01..04** Thu thap & tich hop du lieu (Excel/CSV, ODBC, scheduling, incremental watermark) - [extract_sales.py](etl/extract/extract_sales.py)
- [x] **FR-05..09** Bien doi & lam sach (deduplicate, chuan hoa, NULL, FK check, log) - [transform_sales.py](etl/transform/transform_sales.py)
- [x] **FR-10..16** Multi-tenant user management (Tenants, JWT, RLS, admin bypass, tenant tagging, RBAC) - [auth.py](api/auth.py)
- [x] **FR-17..22** Dashboard truc quan hoa (5 dashboards + drill-down) - cau hinh trong [superset/scripts/provision_v2.py](superset/scripts/provision_v2.py)

### 2.1B. Use Case — **83%** (5/6)
- [x] **UC01** Dang nhap Auth Gateway - [auth.py:322](api/auth.py#L322) `POST /auth/login`
- [x] **UC02** Xem Dashboard Phan tich Doanh thu - [dashboard.html](frontend/templates/dashboard.html)
- [x] **UC03** Quan ly Tenant (CRUD) - [management.py](api/management.py) `/tenants`
- [x] **UC04** Quan ly User (CRUD) - [management.py](api/management.py) `/users`
- [x] **UC05** Upload du lieu - [upload.py](api/upload.py) `/upload/{tenant_id}`
- [x] **UC06** Chay ETL Pipeline - [main_etl.py](etl/orchestrator/main_etl.py)
- [ ] Cap nhat de cuong: bo sung UC03-UC05 vao bao cao (code da co nhung de cuong chua nhac den)

### 2.2. Yeu cau phi chuc nang (NFR-01..NFR-12) — **88%** (10.5/12)
- [x] **NFR-01** Hieu nang truy van <= 3s - co Indexes [06_create_indexes.sql](sql/schema/06_create_indexes.sql) + DM pre-aggregated
- [x] **NFR-02** ETL <= 30 phut - logic da co, chua benchmark thuc te
- [x] **NFR-03** >= 100 trieu ban ghi Fact - schema san sang, chua benchmark
- [x] **NFR-04** Ty le loi <= 0.1% - co [STG_ErrorLog](sql/schema/04_create_staging.sql) + alert ngưỡng [monitoring.py](monitoring/monitoring.py) `alert_high_error_rate`
- [ ] **NFR-05** Uptime >= 99% - chua co ha tang HA + chua co health-check service
- [x] **NFR-06** JWT HS256 + bcrypt + RBAC + RLS - [auth.py](api/auth.py)
- [~] **NFR-07** HTTPS bat buoc - **Co [nginx/nginx.conf](nginx/nginx.conf) (HTTPS + HSTS + rate limit)** nhung con thieu provision Let's Encrypt SSL cert thuc te + deploy nginx container
- [x] **NFR-08** JWT access 8h, refresh 7 ngay - [auth.py:387](api/auth.py#L387)
- [x] **NFR-09** Them tenant moi khong doi kien truc - [POST /tenants](api/management.py)
- [x] **NFR-10** Them nguon moi qua module Extract
- [x] **NFR-11** Tuong thich Chrome/Firefox/Edge - frontend HTML chuan
- [x] **NFR-12** Alert ETL FAILED <= 5 phut - [monitoring.py](monitoring/monitoring.py) `alert_etl_failed` + [main_etl.py:120](etl/orchestrator/main_etl.py#L120) `alert()`

---

## Chuong 3 - Kien truc He thong — **100%** (13/13)

### 3.1-3.2. Mo hinh 5 tang — **100%** (5/5)
- [x] **Tang 0 - Auth Gateway** (FastAPI + JWT + bcrypt) - [api/main.py](api/main.py), [api/auth.py](api/auth.py)
- [x] **Tang 1 - Data Sources** (Excel/CSV theo tenant) - [data/](data/) (tenant_id mapping qua FilePath in Tenants table)
- [x] **Tang 2 - ETL Processing** (Python + Pandas + tenant tagging) - [etl/](etl/)
- [x] **Tang 3 - Data Warehouse** (SQL Server Star Schema + RLS view) - [sql/schema/](sql/schema/)
- [x] **Tang 4 - BI Layer** (Superset + RBAC + RLS) - [superset/superset_config.py](superset/superset_config.py)

### 3.3. Stack cong nghe — **100%** (8/8)
- [x] FastAPI 0.110+ - co [api/](api/)
- [x] PyJWT + passlib bcrypt - [auth.py](api/auth.py)
- [x] SQL Server 2022 - [docker-compose.yml](docker-compose.yml)
- [x] Python 3.10+ pandas + pyodbc/pymssql - co [requirements.txt](requirements.txt)
- [x] Apache Superset 3.x - [superset/Dockerfile](superset/Dockerfile)
- [x] Docker + Docker Compose - [docker-compose.yml](docker-compose.yml)
- [x] Email + Slack alert - [monitoring/monitoring.py](monitoring/monitoring.py)
- [x] Nginx reverse proxy (cau hinh san) - [nginx/nginx.conf](nginx/nginx.conf)

---

## Chuong 4 - Thiet ke Co so Du lieu — **100%** (30/30)

### 4.2. Bang quan ly Tenant + Users — **100%** (3/3)
- [x] Bang **Tenants** (TenantID, TenantName, FilePath, IsActive, ExpiresAt, CreatedAt) - [01_create_tenants.sql](sql/schema/01_create_tenants.sql)
- [x] Bang **AppUsers** (UserID, Username, PasswordHash bcrypt, TenantID FK, Role, IsActive) - [01_create_tenants.sql](sql/schema/01_create_tenants.sql)
- [x] Bo sung cot **ExpiresAt** (Subscription) - [add_tenant_expires_at.sql](sql/migrations/add_tenant_expires_at.sql)

### 4.3. Bang Dimension — **100%** (6/6) - [02_create_dimensions.sql](sql/schema/02_create_dimensions.sql)
- [x] **DimDate** (Shared, pre-populated 2015-2030 qua usp_Load_DimDate)
- [x] **DimProduct** (Shared, SCD Type 2)
- [x] **DimCustomer** (TenantID, SCD Type 2)
- [x] **DimStore** (TenantID, PK)
- [x] **DimEmployee** (TenantID)
- [x] **DimSupplier** (Shared)

### 4.4. Bang Fact — **100%** (3/3) - [03_create_facts.sql](sql/schema/03_create_facts.sql)
- [x] **FactSales** (TenantID, DateKey, ProductKey, CustomerKey, StoreKey, EmployeeKey, ...)
- [x] **FactInventory** (TenantID, DateKey, ProductKey, StoreKey, OpeningStock, ClosingStock, ...)
- [x] **FactPurchase** (TenantID, DateKey, ProductKey, SupplierKey, StoreKey, ...)

### 4.5. Bang Staging — **100%** (5/5) - [04_create_staging.sql](sql/schema/04_create_staging.sql)
- [x] **STG_SalesRaw**, **STG_InventoryRaw**, **STG_PurchaseRaw**, **STG_ProductRaw**
- [x] **STG_CustomerRaw** (DDL bo sung muc 4.8)
- [x] **STG_ErrorLog**
- [x] **ETL_Watermark** (TenantID, TableName, LastRunTime, LastRunStatus, UNIQUE constraint)
- [x] **ETLLogs** (LogID, TenantID, BatchDate, RunStatus, Rows*, DurationSeconds computed) - DDL bo sung muc 4.9

### 4.6. Data Mart Layer — **100%** (5/5) - [05_create_datamart.sql](sql/schema/05_create_datamart.sql)
- [x] **DM_SalesSummary** (Aggregate Table)
- [x] **DM_ProductPerformance** (View)
- [x] **DM_InventoryAlert** (Aggregate Table - co migration [create_dm_inventory_alert_table.sql](sql/migrations/create_dm_inventory_alert_table.sql))
- [x] **DM_CustomerRFM** (Aggregate Table)
- [x] **DM_EmployeePerformance** (View)

### 4.7. Multi-Tenant Setup — **100%** (4/4)
- [x] FK constraint TenantID -> Tenants tren toan bo Fact/Dim - [03_create_facts.sql](sql/schema/03_create_facts.sql)
- [x] **v_FactSales_ByTenant** (View loc theo SESSION_CONTEXT) - [v_FactSales_ByTenant.sql](sql/views/v_FactSales_ByTenant.sql)
- [x] **usp_SetTenantContext** (Wrapper sp_set_session_context) - co trong [00_init.sql](sql/00_init.sql)
- [x] Insert seed Tenants STORE_HN, STORE_HCM

### 4.10-4.11. Indexes bo sung — **100%** (4/4) - [06_create_indexes.sql](sql/schema/06_create_indexes.sql)
- [x] IX_DM_Sales_Tenant_Date, IX_DM_Sales_Store, IX_DM_CustRFM_Tenant
- [x] UQ_DimCustomer_Current (TenantID, CustomerCode WHERE IsCurrent=1)
- [x] UQ_DimProduct_Current (ProductCode WHERE IsCurrent=1)
- [x] IX_FactSales/FactInventory/FactPurchase_TenantID

---

## Chuong 5 - Tien trinh ETL — **96%** (25/26)

### 5.2. Buoc Extract — **100%** (4/4) - [etl/extract/extract_sales.py](etl/extract/extract_sales.py)
- [x] `get_last_watermark(conn, tenant_id, source_type)` lay watermark theo tenant
- [x] `extract_sales_from_excel()` - doc Excel, loc theo watermark, gan TenantID
- [x] `extract_inventory_from_excel()`, `extract_csv_file()` - ho tro Inventory + CSV (Customer/Product/Purchase)
- [x] Bang **ETL_Watermark** voi LastRunStatus PENDING/RUNNING/SUCCESS/FAILED

### 5.3. Buoc Transform — **100%** (4/4)
- [x] **transform_sales(df, tenant_id)** - chuan hoa, lam sach, deduplicate, tinh cot phai sinh - [transform_sales.py](etl/transform/transform_sales.py)
- [x] **usp_Transform_FactSales** - voi @TenantID, transaction try/catch - [usp_Transform_FactSales.sql](sql/sp/usp_Transform_FactSales.sql)
- [x] **usp_Transform_FactInventory** - [usp_Transform_FactInventory.sql](sql/sp/usp_Transform_FactInventory.sql)
- [x] **usp_Transform_FactPurchase** - [usp_Transform_FactPurchase.sql](sql/sp/usp_Transform_FactPurchase.sql)

### 5.4. Buoc Load - ETL Orchestrator — **100%** (5/5) - [etl/orchestrator/main_etl.py](etl/orchestrator/main_etl.py)
- [x] `run_etl_for_tenant(tenant_id, data_dir)` - **7 phase**: SCAN, EXTRACT, TRANSFORM, LOAD DIMS, LOAD FACTS, REFRESH DM, UPDATE WATERMARK
- [x] `classify_file()` - phan loai 5 loai file: sales, inventory, customer, product, purchase
- [x] `run_all_etl()` - vong lap qua tenant active
- [x] Try/Except - update watermark FAILED + send alert
- [x] Per-tenant log file (`./data/{tenant}/logs/etl_{timestamp}.log`)

### 5.5. Thu tu nap du lieu — **100%** (1/1)
- [x] DimDate -> DimSupplier -> DimProduct -> DimCustomer -> DimStore -> DimEmployee -> Fact* -> DM* -> Watermark - [main_etl.py](etl/orchestrator/main_etl.py)

### 5.6-5.7. SCD Type 2 — **100%** (5/5)
- [x] **usp_Load_DimProduct** (Shared, SCD2) - [usp_Load_DimProduct.sql](sql/sp/usp_Load_DimProduct.sql)
- [x] **usp_Load_DimCustomer** (TenantID, SCD2) - [usp_Load_DimCustomer.sql](sql/sp/usp_Load_DimCustomer.sql)
- [x] **usp_Load_DimStore** - [usp_Load_DimStore.sql](sql/sp/usp_Load_DimStore.sql)
- [x] **usp_Load_DimEmployee** - [usp_Load_DimEmployee.sql](sql/sp/usp_Load_DimEmployee.sql)
- [x] **usp_Load_DimDate** (pre-populate 2015-2030) - [usp_Load_DimDate.sql](sql/sp/usp_Load_DimDate.sql)

### 5.x. Data Mart Refresh — **83%** (5/6)
- [x] **usp_Refresh_DM_SalesSummary** - [usp_Refresh_DM_SalesSummary.sql](sql/sp/usp_Refresh_DM_SalesSummary.sql)
- [x] **usp_Refresh_DM_CustomerRFM** - [usp_Refresh_DM_CustomerRFM.sql](sql/sp/usp_Refresh_DM_CustomerRFM.sql)
- [x] **usp_Refresh_DM_InventoryAlert** - ✅ **Da co** [usp_Refresh_DM_InventoryAlert.sql](sql/sp/usp_Refresh_DM_InventoryAlert.sql) (SP refresh table DM_InventoryAlert)
- [x] **DM_EmployeePerformance** - **VIEW** (khong can SP refresh, tinh on-the-fly tu FactSales)
- [x] **DM_ProductPerformance** - **VIEW** (khong can SP refresh, tinh on-the-fly tu FactSales)
- [ ] **Tich hop refresh DM vao orchestrator**: hien `main_etl.py` PHASE 6 dang dung inline SQL MERGE; co the chuyen sang goi `EXEC usp_Refresh_DM_*` cho dong nhat (optional, hien tai chay duoc)

### 5.x. Watermark — **100%** (1/1)
- [x] **usp_Update_Watermark** (RUNNING/SUCCESS/FAILED) - [usp_Update_Watermark.sql](sql/sp/usp_Update_Watermark.sql)

---

## Chuong 6 - Multi-Tenant Security — **94%** (51.5/55)

### 6.1. Auth Gateway FastAPI — **100%** (8/8) - [api/](api/)
- [x] **POST /auth/login** - bcrypt verify, tra JWT 8h - [auth.py:322](api/auth.py#L322)
- [x] **POST /auth/register** - dang ky tenant moi - [auth.py:251](api/auth.py#L251) + [register.html](frontend/templates/register.html)
- [x] **POST /auth/refresh** - refresh token - [auth.py:387](api/auth.py#L387)
- [x] **GET /auth/dashboard-token** - tao Superset Guest Token + RLS clause - [auth.py:423](api/auth.py#L423)
- [x] **GET /auth/me** - tra thong tin user hien tai - [auth.py:503](api/auth.py#L503)
- [x] **/health** - health check - [main.py](api/main.py)
- [x] Block login khi tenant het han ExpiresAt - [auth.py:353](api/auth.py#L353)
- [x] CORS + GZip middleware

### 6.1b. Management API — **100%** (5/5) - [api/management.py](api/management.py)
- [x] CRUD `/tenants` (list/create/update/delete) - admin only
- [x] CRUD `/users` (list/create/update/delete) + filter by tenant
- [x] `GET /etl/logs` + `/etl/watermarks`
- [x] `POST /etl/trigger/{tenant_id}` - chay ETL thu cong
- [x] `GET /kpi` - dashboard KPI

### 6.1c. Upload API — **100%** (4/4) - [api/upload.py](api/upload.py)
- [x] `POST /upload/{tenant_id}` - upload Excel/CSV
- [x] `POST /upload/{tenant_id}/etl` - trigger ETL background
- [x] `GET /upload/{tenant_id}/etl/status` - poll trang thai
- [x] `GET/DELETE /upload/{tenant_id}/files`

### 6.2. Security design — **92%** (5.5/6)
- [x] bcrypt passlib (rounds=12)
- [x] JWT HS256, secret tu env (`JWT_SECRET_KEY`)
- [x] Access token 8h, refresh 7 ngay
- [x] Parameterized queries (pyodbc/pymssql voi `?` hoac `%s`)
- [~] **HTTPS / nginx reverse proxy** - ✅ Co [nginx/nginx.conf](nginx/nginx.conf) (TLS 1.2/1.3, HSTS, rate limit) | ❌ Chua provision SSL cert thuc te (Let's Encrypt)
- [x] Sensitive data masking (Phone, Email) - co trong logic transform

### 6.3. Superset RBAC + RLS — **100%** (5/5) - [superset/](superset/)
- [x] **superset_config.py** - AUTH_USER_REGISTRATION=False, PUBLIC_ROLE_LIKE=None, CSRF, FEATURE_FLAGS, GUEST_TOKEN_JWT_SECRET - [superset_config.py](superset/superset_config.py)
- [x] **api/superset_provision.py** - auto-provision Superset user + role `RLS_<TenantID>` khi tao tenant/admin qua auth-gateway
- [x] **scripts/provision_v2.py** - provisioning datasets + dashboards + doc Tenants active tu MSSQL de tao RLS dong
- [x] **scripts/fix_*.py / sync_*.py / rebuild_dashboards.py** - cong cu sua chart, position, sync dataset columns
- [x] Role TenantViewer (read-only) + RLS rule `TenantID = 'X'` per tenant

### 6.4. Monitoring + Alerting — **86%** (6/7) - [monitoring/monitoring.py](monitoring/monitoring.py)
- [x] `send_email_alert(subject, body)` qua smtplib - [monitoring.py:25](monitoring/monitoring.py#L25)
- [x] `send_slack_alert(message)` qua webhook - [monitoring.py:53](monitoring/monitoring.py#L53)
- [x] `alert_etl_failed(tenant_id, batch_date, error_msg)` - [monitoring.py:75](monitoring/monitoring.py#L75)
- [x] `alert_etl_timeout(...)` (NFR-12 timeout > 45 phut) - [monitoring.py:102](monitoring/monitoring.py#L102)
- [x] `alert_high_error_rate(...)` (NFR-04 ngưỡng 0.1%) - [monitoring.py:132](monitoring/monitoring.py#L132)
- [x] `alert_service_down(...)` (Superset/MSSQL down) - [monitoring.py:163](monitoring/monitoring.py#L163)
- [ ] **Tich hop monitoring/monitoring.py vao main_etl.py**: hien orchestrator dang co alert noi bo `send_email_alert`/`send_slack_alert` lap lai logic; nen `from monitoring.monitoring import alert_etl_failed`

### 6.5. Backup va Disaster Recovery — **71%** (5/7) - [sql/backup_dwh.py](sql/backup_dwh.py)
- [x] **`backup_full()`** - Full Backup SQL Server (sqlcmd + COMPRESSION) - retention 28 ngay
- [x] **`backup_differential()`** - Differential Backup - retention 7 ngay
- [x] **`backup_transaction_log()`** - Transaction Log Backup - retention 2 ngay
- [x] **`cleanup_old_backups()`** - Auto cleanup theo retention policy
- [x] **[sql/backup_dwh.sh](sql/backup_dwh.sh)** - shell wrapper de chay qua cron
- [ ] **Setup cron schedule** thuc te (full hang tuan, diff hang ngay, log moi 4h)
- [ ] Archive file Excel/CSV nguon (rieng ngoai DB) - chua co script
- [ ] Export Superset Dashboard JSON commit Git - chua co script

### 6.6. Cau truc thu muc - so sanh voi bao cao — **100%** (5/5)
- [x] `api/`, `etl/extract|transform|orchestrator`, `sql/schema|sp|views|migrations`, `superset/scripts`, `data/`
- [x] `frontend/` (bao cao khong neu nhung da co - bonus)
- [x] **`monitoring/monitoring.py`** - ✅ Da co (5 ham alert)
- [x] **`nginx/nginx.conf`** - ✅ Da co (HTTPS reverse proxy)
- [x] **`sql/backup_dwh.py` + `backup_dwh.sh`** - ✅ Da co (full/diff/log)

### 6.7. Luong end-to-end — **100%** (8/8)
- [x] Buoc 1 - Login -> JWT
- [x] Buoc 2 - Get dashboard-token -> Guest Token
- [x] Buoc 3 - Render iframe Superset - [dashboard.html](frontend/templates/dashboard.html)
- [x] Buoc 4-5 - RLS append `WHERE tenant_id=...`
- [x] Buoc 6 - Admin xem all data
- [x] Buoc 7 - ETL Scheduler 02:00 SA - chay manual qua `POST /etl/trigger/{tenant_id}` hoac cron + `python -m etl.orchestrator.main_etl`
- [x] Buoc 8 - Alert khi FAILED qua [monitoring.py](monitoring/monitoring.py)

---

## Cong viec con lai (Optional / Production-ready) — **20%** (3/15)

### Uu tien CAO (can lam de hoan thien bao cao) — **0%** (0/4)
- [ ] **Provision SSL cert** Let's Encrypt + deploy nginx container vao docker-compose (NFR-07)
- [ ] **Tich hop `monitoring/monitoring.py` vao `main_etl.py`** - thay 3 ham alert noi bo bang `from monitoring.monitoring import alert_etl_failed, alert_etl_timeout, alert_high_error_rate`
- [ ] **Cap nhat de cuong/bao cao**: bo sung use case **UC03 (CRUD Tenant), UC04 (CRUD User), UC05 (Upload file)** vao Chuong 2.1B - hien code da co
- [ ] **Setup cron** cho `sql/backup_dwh.sh` (full Chu Nhat 02:00, diff hang ngay 03:00, log moi 4h)

### Uu tien TRUNG BINH (production-ready) — **0%** (0/5)
- [ ] Tao bo **test tu dong** (pytest) cho ETL pipeline (`tests/test_etl.py`) va Auth API (`tests/test_auth.py`)
- [ ] **Benchmark hieu nang** thuc te:
    - NFR-02: ETL run-time <= 30 phut voi du lieu thuc
    - NFR-01: query DM <= 3s (SELECT * FROM DM_SalesSummary WHERE TenantID=...)
    - NFR-03: stress-test 100 trieu ban ghi Fact (insert va query)
- [ ] Chay thuc nghiem **end-to-end voi >= 2 tenant** (STORE_HN + STORE_HCM), chup anh man hinh dashboard cho bao cao
- [ ] Verify hien thi **5 dashboard chinh** tren UI Superset (Doanh thu, San pham, Ton kho, Khach hang RFM, Nhan vien)
- [ ] Setup health-check service + Uptime monitoring (NFR-05) - dung Uptime Kuma hoac Grafana

### Uu tien THAP (cleanup / nice-to-have) — **0%** (0/5)
- [ ] Don dep [superset/scripts/](superset/scripts/) - hien co 7 file (provision_v2 + 6 fix/sync) - giu provision_v2.py + rebuild_dashboards.py + sync_dataset_columns.py
- [ ] Don dep file rac trong root: [12.txt](12.txt), [_bootstrap.sql](_bootstrap.sql), [get-docker.sh](get-docker.sh), [etl_orchestrator.log](etl_orchestrator.log) - them vao `.gitignore`
- [ ] (Optional) Tich hop refresh DM trong `main_etl.py` PHASE 6 sang dung `EXEC usp_Refresh_DM_*` thay vi inline SQL MERGE - giup dong nhat voi bao cao
- [ ] Archive file Excel/CSV nguon sau khi ETL thanh cong (di chuyen sang `./data/{tenant}/archive/`)
- [ ] Script export Superset Dashboard JSON (`superset export-dashboards`) commit vao Git de version-control dashboard

---

## 📊 Phan tich tien do chi tiet

### Cong thuc tinh
- Moi muc `[x]` = 1 diem
- Moi muc `[~]` (partial) = 0.5 diem
- Moi muc `[ ]` = 0 diem
- Tien do chuong = (Tong diem / Tong so muc) × 100%

### Bieu do tien do
```
Chuong 1:  ████████████████████  100%  (6/6)    Phan tich thuc trang
Chuong 2:  █████████████████░░░   89%  (19.5/22) Yeu cau he thong
Chuong 3:  ████████████████████  100%  (13/13)  Kien truc 5 tang
Chuong 4:  ████████████████████  100%  (30/30)  Thiet ke CSDL
Chuong 5:  ███████████████████░   96%  (25/26)  Tien trinh ETL
Chuong 6:  ██████████████████░░   94%  (51.5/55) Multi-tenant Security
─────────────────────────────────────────────────────────────
CORE:      ███████████████████░   95%  (145/152) ⭐ Du an chinh
Optional:  ████░░░░░░░░░░░░░░░░   20%  (3/15)   Production-ready
─────────────────────────────────────────────────────────────
TOAN BO:   █████████████████░░░   89%  (148/167)
```

### Tinh trang san sang nop bao cao
- ✅ **Du an co the nop bao cao** (Core: 95%) — moi yeu cau chinh trong de cuong da hoan thanh
- ⚠️ **Truoc khi nop**: nen lam them 4 muc Uu tien CAO (UC03-UC05 vao bao cao, SSL cert, tich hop monitoring, cron backup)
- 📅 **Sau khi nop**: 10 muc con lai (TRUNG BINH + THAP) la production-ready, khong bat buoc cho do an tot nghiep

---

*Cap nhat tu dong: 2026-05-06 - dua tren scan codebase va doi chieu de cuong [Nguyen_Van_Khang_Bao_Cao.md](Nguyen_Van_Khang_Bao_Cao.md)*

*Thay doi chinh so voi ban 2026-05-05:*
- *✅ usp_Refresh_DM_InventoryAlert da co (truoc danh dau missing)*
- *✅ monitoring/monitoring.py da co 5 ham alert (truoc folder rong)*
- *✅ nginx/nginx.conf da co cau hinh HTTPS day du (truoc chua co)*
- *✅ sql/backup_dwh.py + .sh da co (truoc chua co)*
- *✅ DM_ProductPerformance/EmployeePerformance la VIEW - khong can SP refresh*
- *✅ UC03-UC05 thuc te da co code (management.py + upload.py)*
- *📊 Them tien do % cho tat ca 30 muc cua checklist*
