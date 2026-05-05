# Checklist Tien do Du an Data Warehouse Multi-Tenant

> Du an: **Xay dung he thong Data Warehouse va truc quan hoa du lieu kinh doanh cho chuoi cua hang ban le thiet bi cong nghe (Multi-Tenant)** - Nguyen Van Khang - 64HTTT4
>
> Checklist nay duoc tao tu de cuong bao cao [Nguyen_Van_Khang_Bao_Cao.md](Nguyen_Van_Khang_Bao_Cao.md) va doi chieu voi codebase hien tai (scan ngay 2026-05-05).

---

## Tong quan trang thai

| Hang muc | Trang thai | Ghi chu |
| :---- | :---- | :---- |
| Chuong 1 - Phan tich thuc trang | Hoan thanh | Tai lieu hoa trong bao cao |
| Chuong 2 - Yeu cau he thong (FR/NFR) | Hoan thanh | 22 FR + 12 NFR da xac dinh |
| Chuong 3 - Kien truc 5 tang | Hoan thanh | Auth Gateway + ETL + DWH + BI |
| Chuong 4 - Thiet ke CSDL | Hoan thanh | Schema, Dim, Fact, STG, DM, Indexes |
| Chuong 5 - Tien trinh ETL | Hoan thanh | Extract/Transform/Load orchestrator |
| Chuong 6 - Multi-tenant Security | ~95% | Thieu Refresh DM Inventory/Employee + HTTPS/nginx |
| Khac (test, deploy production) | Chua co | Chua co bo test tu dong va cau hinh production |

---

## Chuong 1 - Tong quan He thong

### 1.1. Phan tich thuc trang doanh nghiep
- [x] Mo ta thuc trang quan ly du lieu phan manh tren Excel/Google Sheets
- [x] Liet ke 5 van de noi com (data island, khong nhat quan, mat lich su, ...)
- [x] Phan tich 3 nguon du lieu chinh (POS, Kho van, Danh muc San pham)

### 1.2. Ly do can xay dung Data Warehouse
- [x] Trinh bay 6 ly do (Single Source of Truth, lich su, chat luong, toc do, multi-tenant, OLAP)

### 1.3. Muc tieu du an
- [x] Muc tieu tong quat: DWH + ETL + BI + multi-tenant
- [x] 6 muc tieu cu the (SQL Server Star Schema, ETL, Dim/Fact, Superset 5+ dashboards, multi-tenant, hieu nang <= 3s)

---

## Chuong 2 - Yeu cau He thong

### 2.1. Yeu cau chuc nang (Functional Requirements)
- [x] **FR-01..04** Thu thap & tich hop du lieu (Excel/CSV, ODBC, scheduling, incremental watermark) - [extract_sales.py](etl/extract/extract_sales.py)
- [x] **FR-05..09** Bien doi & lam sach (deduplicate, chuan hoa, NULL, FK check, log) - [transform_sales.py](etl/transform/transform_sales.py)
- [x] **FR-10..16** Multi-tenant user management (Tenants, JWT, RLS, admin bypass, tenant tagging, RBAC) - [auth.py](api/auth.py)
- [x] **FR-17..22** Dashboard truc quan hoa (5 dashboards + drill-down) - cau hinh trong [superset/scripts/provision.py](superset/scripts/provision.py)

### 2.1B. Use Case
- [x] **UC01** Dang nhap Auth Gateway - [auth.py:322](api/auth.py#L322) `POST /auth/login`
- [x] **UC02** Xem Dashboard Phan tich Doanh thu - [dashboard.html](frontend/templates/dashboard.html)
- [x] **UC06** Chay ETL Pipeline - [main_etl.py](etl/orchestrator/main_etl.py)
- [ ] UC03..UC05 - de cuong neu them use case quan ly user/tenant, can ra soat lai voi GVHD

### 2.2. Yeu cau phi chuc nang (NFR-01..NFR-12)
- [x] **NFR-01** Hieu nang truy van <= 3s - co Indexes [06_create_indexes.sql](sql/schema/06_create_indexes.sql) + DM pre-aggregated
- [x] **NFR-02** ETL <= 30 phut - chua benchmark thuc te
- [x] **NFR-03** >= 100 trieu ban ghi Fact - chua benchmark
- [x] **NFR-04** Ty le loi <= 0.1% - co [STG_ErrorLog](sql/schema/04_create_staging.sql)
- [ ] **NFR-05** Uptime >= 99% - chua co ha tang HA
- [x] **NFR-06** JWT HS256 + bcrypt + RBAC + RLS - [auth.py](api/auth.py)
- [ ] **NFR-07** HTTPS bat buoc - **Chua cau hinh nginx/SSL cho production**
- [x] **NFR-08** JWT access 8h, refresh 7 ngay - [auth.py:387](api/auth.py#L387)
- [x] **NFR-09** Them tenant moi khong doi kien truc - [POST /tenants](api/management.py)
- [x] **NFR-10** Them nguon moi qua module Extract
- [x] **NFR-11** Tuong thich Chrome/Firefox/Edge - frontend HTML chuan
- [x] **NFR-12** Alert ETL FAILED <= 5 phut - [main_etl.py:120](etl/orchestrator/main_etl.py#L120) `alert()`

---

## Chuong 3 - Kien truc He thong

### 3.1-3.2. Mo hinh 5 tang
- [x] **Tang 0 - Auth Gateway** (FastAPI + JWT + bcrypt) - [api/main.py](api/main.py), [api/auth.py](api/auth.py)
- [x] **Tang 1 - Data Sources** (Excel/CSV theo tenant) - [data/STORE_HN/](data/STORE_HN/), [data/STORE_ND/](data/STORE_ND/)
- [x] **Tang 2 - ETL Processing** (Python + Pandas + tenant tagging) - [etl/](etl/)
- [x] **Tang 3 - Data Warehouse** (SQL Server Star Schema + RLS view) - [sql/schema/](sql/schema/)
- [x] **Tang 4 - BI Layer** (Superset + RBAC + RLS) - [superset/superset_config.py](superset/superset_config.py)

### 3.3. Stack cong nghe
- [x] FastAPI 0.110+ - co [api/](api/)
- [x] PyJWT + passlib bcrypt - [auth.py](api/auth.py)
- [x] SQL Server 2022 - [docker-compose.yml](docker-compose.yml)
- [x] Python 3.10+ pandas + pyodbc/pymssql - co [requirements.txt](requirements.txt)
- [x] Apache Superset 3.x - [superset/Dockerfile](superset/Dockerfile)
- [x] Docker + Docker Compose - [docker-compose.yml](docker-compose.yml)
- [x] Email + Slack alert - [main_etl.py:87](etl/orchestrator/main_etl.py#L87)

---

## Chuong 4 - Thiet ke Co so Du lieu

### 4.2. Bang quan ly Tenant + Users
- [x] Bang **Tenants** (TenantID, TenantName, FilePath, IsActive, ExpiresAt, CreatedAt) - [01_create_tenants.sql](sql/schema/01_create_tenants.sql)
- [x] Bang **AppUsers** (UserID, Username, PasswordHash bcrypt, TenantID FK, Role, IsActive) - [01_create_tenants.sql](sql/schema/01_create_tenants.sql)
- [x] Bo sung cot **ExpiresAt** (Subscription) - [add_tenant_expires_at.sql](sql/migrations/add_tenant_expires_at.sql)

### 4.3. Bang Dimension - [02_create_dimensions.sql](sql/schema/02_create_dimensions.sql)
- [x] **DimDate** (Shared, pre-populated 2015-2030 qua usp_Load_DimDate)
- [x] **DimProduct** (Shared, SCD Type 2)
- [x] **DimCustomer** (TenantID, SCD Type 2)
- [x] **DimStore** (TenantID, PK)
- [x] **DimEmployee** (TenantID)
- [x] **DimSupplier** (Shared)

### 4.4. Bang Fact - [03_create_facts.sql](sql/schema/03_create_facts.sql)
- [x] **FactSales** (TenantID, DateKey, ProductKey, CustomerKey, StoreKey, EmployeeKey, ...)
- [x] **FactInventory** (TenantID, DateKey, ProductKey, StoreKey, OpeningStock, ClosingStock, ...)
- [x] **FactPurchase** (TenantID, DateKey, ProductKey, SupplierKey, StoreKey, ...)

### 4.5. Bang Staging - [04_create_staging.sql](sql/schema/04_create_staging.sql)
- [x] **STG_SalesRaw**, **STG_InventoryRaw**, **STG_PurchaseRaw**, **STG_ProductRaw**
- [x] **STG_CustomerRaw** (DDL bo sung muc 4.8)
- [x] **STG_ErrorLog**
- [x] **ETL_Watermark** (TenantID, TableName, LastRunTime, LastRunStatus, UNIQUE constraint)
- [x] **ETLLogs** (LogID, TenantID, BatchDate, RunStatus, Rows*, DurationSeconds computed) - DDL bo sung muc 4.9

### 4.6. Data Mart Layer - [05_create_datamart.sql](sql/schema/05_create_datamart.sql)
- [x] **DM_SalesSummary** (Aggregate Table)
- [x] **DM_ProductPerformance** (View)
- [x] **DM_InventoryAlert** (View)
- [x] **DM_CustomerRFM** (Aggregate Table)
- [x] **DM_EmployeePerformance** (View)

### 4.7. Multi-Tenant Setup
- [x] FK constraint TenantID -> Tenants tren toan bo Fact/Dim - [03_create_facts.sql](sql/schema/03_create_facts.sql)
- [x] **v_FactSales_ByTenant** (View loc theo SESSION_CONTEXT) - [v_FactSales_ByTenant.sql](sql/views/v_FactSales_ByTenant.sql)
- [x] **usp_SetTenantContext** (Wrapper sp_set_session_context) - co trong [00_init.sql](sql/00_init.sql)
- [x] Insert seed Tenants STORE_HN, STORE_HCM

### 4.10-4.11. Indexes bo sung - [06_create_indexes.sql](sql/schema/06_create_indexes.sql)
- [x] IX_DM_Sales_Tenant_Date, IX_DM_Sales_Store, IX_DM_CustRFM_Tenant
- [x] UQ_DimCustomer_Current (TenantID, CustomerCode WHERE IsCurrent=1)
- [x] UQ_DimProduct_Current (ProductCode WHERE IsCurrent=1)
- [x] IX_FactSales/FactInventory/FactPurchase_TenantID

---

## Chuong 5 - Tien trinh ETL

### 5.2. Bước Extract - [etl/extract/extract_sales.py](etl/extract/extract_sales.py)
- [x] `get_last_watermark(conn, tenant_id, source_type)` lay watermark theo tenant
- [x] `extract_sales_from_excel()` - doc Excel, loc theo watermark, gan TenantID
- [x] Bang **ETL_Watermark** voi LastRunStatus PENDING/RUNNING/SUCCESS/FAILED

### 5.3. Buoc Transform
- [x] **transform_sales(df, tenant_id)** - chuan hoa, lam sach, deduplicate, tinh cot phai sinh - [transform_sales.py](etl/transform/transform_sales.py)
- [x] **usp_Transform_FactSales** - voi @TenantID, transaction try/catch - [usp_Transform_FactSales.sql](sql/sp/usp_Transform_FactSales.sql)
- [x] **usp_Transform_FactInventory** - [usp_Transform_FactInventory.sql](sql/sp/usp_Transform_FactInventory.sql)
- [x] **usp_Transform_FactPurchase** - [usp_Transform_FactPurchase.sql](sql/sp/usp_Transform_FactPurchase.sql)

### 5.4. Buoc Load - ETL Orchestrator - [etl/orchestrator/main_etl.py](etl/orchestrator/main_etl.py)
- [x] `run_etl_for_tenant(tenant_id, file_path)` - 5 phase: Extract, Load Dim, Load Fact, Refresh DM, Update Watermark
- [x] Vong lap qua tenant active
- [x] Try/Except - update watermark FAILED + send alert

### 5.5. Thu tu nap du lieu
- [x] DimDate -> DimSupplier -> DimProduct -> DimCustomer -> DimStore -> DimEmployee -> Fact* -> DM* -> Watermark - [main_etl.py](etl/orchestrator/main_etl.py)

### 5.6-5.7. SCD Type 2
- [x] **usp_Load_DimProduct** (Shared, SCD2) - [usp_Load_DimProduct.sql](sql/sp/usp_Load_DimProduct.sql)
- [x] **usp_Load_DimCustomer** (TenantID, SCD2) - [usp_Load_DimCustomer.sql](sql/sp/usp_Load_DimCustomer.sql)
- [x] **usp_Load_DimStore** - [usp_Load_DimStore.sql](sql/sp/usp_Load_DimStore.sql)
- [x] **usp_Load_DimEmployee** - [usp_Load_DimEmployee.sql](sql/sp/usp_Load_DimEmployee.sql)
- [x] **usp_Load_DimDate** (pre-populate 2015-2030) - [usp_Load_DimDate.sql](sql/sp/usp_Load_DimDate.sql)

### 5.x. Data Mart Refresh
- [x] **usp_Refresh_DM_SalesSummary** - [usp_Refresh_DM_SalesSummary.sql](sql/sp/usp_Refresh_DM_SalesSummary.sql)
- [x] **usp_Refresh_DM_CustomerRFM** - [usp_Refresh_DM_CustomerRFM.sql](sql/sp/usp_Refresh_DM_CustomerRFM.sql)
- [ ] **usp_Refresh_DM_InventoryAlert** - **chua co SP rieng** (dang la VIEW nen co the khong can, can xac nhan voi GVHD)
- [ ] **usp_Refresh_DM_EmployeePerformance** - **chua co SP rieng** (dang la VIEW)
- [ ] **usp_Refresh_DM_ProductPerformance** - **chua co SP rieng** (dang la VIEW)

### 5.x. Watermark
- [x] **usp_Update_Watermark** (RUNNING/SUCCESS/FAILED) - [usp_Update_Watermark.sql](sql/sp/usp_Update_Watermark.sql)

---

## Chuong 6 - Multi-Tenant Security

### 6.1. Auth Gateway FastAPI - [api/](api/)
- [x] **POST /auth/login** - bcrypt verify, tra JWT 8h - [auth.py:322](api/auth.py#L322)
- [x] **POST /auth/register** - dang ky tenant moi - [auth.py:251](api/auth.py#L251) + [register.html](frontend/templates/register.html)
- [x] **POST /auth/refresh** - refresh token - [auth.py:387](api/auth.py#L387)
- [x] **GET /auth/dashboard-token** - tao Superset Guest Token + RLS clause - [auth.py:423](api/auth.py#L423)
- [x] **GET /auth/me** - tra thong tin user hien tai - [auth.py:503](api/auth.py#L503)
- [x] **/health** - health check - [main.py](api/main.py)
- [x] Block login khi tenant het han ExpiresAt - [auth.py:353](api/auth.py#L353)
- [x] CORS + GZip middleware

### 6.1b. Management API - [api/management.py](api/management.py)
- [x] CRUD `/tenants` (list/create/update/delete) - admin only
- [x] CRUD `/users` (list/create/update/delete) + filter by tenant
- [x] `GET /etl/logs` + `/etl/watermarks`
- [x] `POST /etl/trigger/{tenant_id}` - chay ETL thu cong
- [x] `GET /kpi` - dashboard KPI

### 6.1c. Upload API - [api/upload.py](api/upload.py)
- [x] `POST /upload/{tenant_id}` - upload Excel/CSV
- [x] `POST /upload/{tenant_id}/etl` - trigger ETL background
- [x] `GET /upload/{tenant_id}/etl/status` - poll trang thai
- [x] `GET/DELETE /upload/{tenant_id}/files`

### 6.2. Security design
- [x] bcrypt passlib (rounds=12)
- [x] JWT HS256, secret tu env (`JWT_SECRET_KEY`)
- [x] Access token 8h, refresh 7 ngay
- [x] Parameterized queries (pyodbc/pymssql voi `?` hoac `%s`)
- [ ] **HTTPS / nginx reverse proxy** - chua co cau hinh nginx + SSL cert (chi de production)
- [x] Sensitive data masking (Phone, Email) - co trong logic transform

### 6.3. Superset RBAC + RLS - [superset/](superset/)
- [x] **superset_config.py** - AUTH_USER_REGISTRATION=False, PUBLIC_ROLE_LIKE=None, CSRF, FEATURE_FLAGS, GUEST_TOKEN_JWT_SECRET - [superset_config.py](superset/superset_config.py)
- [x] **scripts/create_users.py** - tao Superset users + role TenantViewer + RLS_<TenantID>
- [x] **scripts/provision.py** - provisioning datasets + dashboards
- [x] **scripts/provision_charts.py / v2.py / fix_*.py** - cong cu sua chart, position
- [x] Role TenantViewer (read-only) + RLS rule `tenant_id='X'` per tenant

### 6.4. Monitoring + Alerting
- [x] `send_email_alert(subject, body)` qua smtplib - [main_etl.py:87](etl/orchestrator/main_etl.py#L87)
- [x] `send_slack_alert(message)` qua webhook - [main_etl.py:106](etl/orchestrator/main_etl.py#L106)
- [x] `alert(tenant_id, batch_date, error_msg)` - [main_etl.py:120](etl/orchestrator/main_etl.py#L120)
- [ ] **Folder `monitoring/` rong** - logic alert nam o `etl/orchestrator/main_etl.py`, co the move sang `monitoring/monitoring.py` cho dung cau truc bao cao 6.6

### 6.5. Backup va Disaster Recovery
- [ ] Full Backup SQL Server hang tuan - **chua co script tu dong**
- [ ] Differential Backup hang ngay - chua co
- [ ] Transaction Log Backup moi 4h - chua co
- [ ] Archive file Excel/CSV nguon - chua co
- [ ] Export Superset Dashboard JSON commit Git - chua co script

### 6.6. Cau truc thu muc - so sanh voi bao cao
- [x] `api/`, `etl/extract|transform|orchestrator`, `sql/schema|sp|views`, `superset/scripts`, `data/STORE_HN|STORE_ND`
- [x] `frontend/` (bao cao khong neu nhung da co - bonus)
- [ ] `monitoring/monitoring.py` - **dang rong, can move alert logic vao day**

### 6.7. Luong end-to-end
- [x] Buoc 1 - Login -> JWT
- [x] Buoc 2 - Get dashboard-token -> Guest Token
- [x] Buoc 3 - Render iframe Superset - [dashboard.html](frontend/templates/dashboard.html)
- [x] Buoc 4-5 - RLS append `WHERE tenant_id=...`
- [x] Buoc 6 - Admin xem all data
- [x] Buoc 7 - ETL Scheduler 02:00 SA - co the chay manual qua API hoac cron
- [x] Buoc 8 - Alert khi FAILED

---

## Cong viec con lai (Optional / Production-ready)

- [ ] Move logic alert tu `etl/orchestrator/main_etl.py` sang `monitoring/monitoring.py` (theo cau truc bao cao 6.6)
- [ ] Bo sung 3 SP refresh DM con thieu: `usp_Refresh_DM_InventoryAlert`, `usp_Refresh_DM_EmployeePerformance`, `usp_Refresh_DM_ProductPerformance` (hien la VIEW - can xac dinh co can pre-aggregate khong)
- [ ] Cau hinh **nginx + Let's Encrypt SSL** cho NFR-07 (HTTPS bat buoc)
- [ ] Tao bo **test tu dong** (pytest) cho ETL pipeline va Auth API
- [ ] Tao **script backup tu dong** (full/diff/log) theo NFR muc 6.5
- [ ] **Benchmark hieu nang**: do thuc te ETL (NFR-02 <= 30 phut), query DM (<= 3s), uptime (NFR-05)
- [ ] Chay thuc nghiem **end-to-end voi >= 2 tenant** (STORE_HN + STORE_HCM/STORE_ND), chup anh man hinh dashboard
- [ ] Verify hien thi **5 dashboard chinh** (Doanh thu, San pham, Ton kho, Khach hang RFM, Nhan vien) tren UI Superset
- [ ] Don dep cac script `superset/scripts/check_*`, `debug_*`, `fix_*` - giu lai 1-2 script chinh thuc (provision_v2)
- [ ] Don dep cac file rac trong root: [12.txt](12.txt), [_bootstrap.sql](_bootstrap.sql), [get-docker.sh](get-docker.sh) - them vao .gitignore neu can
- [ ] Sua doi de cuong: bo sung use case UC03-UC05 (CRUD tenant, CRUD user, upload file) - hien thuc te da co code

---

*Cap nhat tu dong: 2026-05-05 - dua tren scan codebase va doi chieu de cuong [Nguyen_Van_Khang_Bao_Cao.md](Nguyen_Van_Khang_Bao_Cao.md)*


