# DATN - Data Warehouse & BI System

Xây dựng hệ thống Data Warehouse và trực quan hóa dữ liệu kinh doanh cho chuỗi cửa hàng bán lẻ thiết bị công nghệ.

**Sinh viên:** Nguyễn Văn Khang (MSSV: 2251162042) - Lớp 64HTTT4
**GVHD:** Đỗ Oanh Cường

---

## Mục lục

1. [Kiến trúc hệ thống](#1-kiến-trúc-hệ-thống)
2. [Yêu cầu](#2-yêu-cầu)
3. [Cấu hình](#3-cấu-hình)
4. [Khởi động](#4-khởi-động)
5. [Sinh dữ liệu mẫu](#5-sinh-dữ-liệu-mẫu)
6. [Chạy ETL Pipeline](#6-chạy-etl-pipeline)
7. [Kết nối Superset](#7-kết-nối-superset)
8. [Reset hệ thống](#8-reset-hệ-thống)
9. [Cấu trúc thư mục](#9-cấu-trúc-thư-mục)
10. [Nâng cấp SaaS Platform](#10-nâng-cấp-multi-tenant-saas-platform)
    - [10.6. Superset Multi-tenant](#106-superset-multi-tenant)

---

## 1. Kiến trúc hệ thống

```
┌──────────────────────────────────────────────────────────────┐
│                 Data Sources (Excel/CSV)                      │
│  BaoCaoDoanhThu | QuanLyKho | DanhMucSanPham | ...        │
└────────────────────────┬───────────────────────────────────┘
                         │ EXTRACT (Python)
                         ▼
┌──────────────────────────────────────────────────────────────┐
│       SQL Server Container (mssql-tools container để chạy SQL) │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   STAGING    │→ │    CORE      │→ │  DATA MART   │     │
│  │   (STG_*)    │  │  (Dim/Fact)  │  │   (DM_*)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────────┬───────────────────────────────────┘
                         │ QUERY
                         ▼
┌──────────────────────────────────────────────────────────────┐
│              Superset (Docker) + Redis + PostgreSQL          │
│  FR-10 Doanh thu | FR-11 Sản phẩm | FR-12 Tồn kho         │
│  FR-13 Khách hàng | FR-14 Nhân viên                        │
└──────────────────────────────────────────────────────────────┘
```

## 2. Yêu cầu

- Docker & Docker Compose v2
- Python 3.10+
- ~10GB disk space

## 3. Cấu hình

Tất cả cấu hình nằm trong file `.env` — **chỉ cần sửa ở đây**.

```bash
# .env


```

> **Quan trọng:** Không hardcode password ở bất kỳ đâu khác. Mọi scripts đều đọc từ `.env`.

## 4. Khởi động

### 4.1. Khởi động Docker
```bash
curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### 4.2. Chạy SQL scripts (tạo schema)
```bash
chmod +x run_sql.sh
./run_sql.sh
```

> **Ghi chú:** Init scripts chạy **tự động** khi Docker khởi tạo lần đầu. `run_sql.sh` dùng `mssql-tools` container để kết nối vào SQL Server.

### 4.3. Kiểm tra
```bash
# Xem logs
docker compose logs mssql

# Kiểm tra database đã được tạo (script tự detect network)
./sql_runner.sh "SELECT name FROM sys.databases"

# Kiểm tra DimDate (~5840 rows)
./sql_runner.sh "SELECT COUNT(*) FROM DimDate"
```

## 5. Sinh dữ liệu mẫu

### 5.1. Cài Python dependencies
```bash
pip install -r etl/requirements.txt
```

### 5.2. Sinh mock data (sạch)
```bash
cd data/samples

# Sinh dữ liệu mới mỗi lần (ngẫu nhiên)
python generate_mock_data.py --fresh

# Sinh với seed cố định (để reproduce)
python generate_mock_data.py --seed 42
```

### 5.2b. Sinh mock data (bẩn - để test ETL)
```bash
# Sinh dữ liệu chưa làm sạch
python generate_dirty_data.py --fresh
```

Dữ liệu bẩn bao gồm:
- Trailing/leading spaces
- Duplicate rows
- NULL values
- Inconsistent date formats (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY)
- Missing foreign key references
- Inconsistent case (ch006 vs CH006)
- Empty string values

Script sinh:
- 5 cửa hàng, 50 sản phẩm, 30 khách hàng, 20 nhân viên, 10 nhà cung cấp
- ~10,000 hóa đơn bán hàng (12 tháng 2025)
- ~91,250 bản ghi tồn kho (365 ngày × 5 cửa hàng × 50 sản phẩm)

### 5.3. Copy vào thư mục nguồn
```bash
mkdir -p ../sources
cp *.xlsx *.csv ../sources/
```

## 6. Chạy ETL Pipeline

```bash
cd /home/khang/Desktop/retail-tech-dwh

# Chạy một lần (load incremental theo watermark)
python -m etl.main_etl

# Chạy với ngày cụ thể
python -m etl.main_etl --date 2025-03-22

# Full load (bỏ qua watermark)
python -m etl.main_etl --full

# Chạy lập lịch hàng ngày lúc 02:00
python -m etl.main_etl --schedule
```

### Kiểm tra log
```bash
tail -f logs/etl_$(date +%Y%m%d).log
```

### Kiểm tra dữ liệu sau ETL
```bash
./sql_runner.sh "SELECT COUNT(*) FROM FactSales"
./sql_runner.sh "SELECT * FROM ETL_RunLog ORDER BY LoadDatetime DESC"
```

## 7. Kết nối Superset

### 7.1. Truy cập Superset
```
http://localhost:8088
```
Login với credentials trong `.env` (`SUPERSET_ADMIN_USER` / `SUPERSET_ADMIN_PASSWORD`).

### 7.2. Thêm Database Connection
1. **Settings** → **Database Connections** → **+ Database**
2. Chọn: **Microsoft SQL Server**
3. Điền thông tin:

| Trường | Giá trị |
|---------|---------|
| Database Name | `DWH_RetailTech` |
| SQLAlchemy URI | `mssql+pyodbc://sa:{PASSWORD}@datn_mssql:1433/DWH_RetailTech?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes` |

   - Thay `{PASSWORD}` bằng giá trị `MSSQL_SA_PASSWORD` trong `.env`
   - Host `datn_mssql` dùng trong Docker network
4. **Test Connection** → **Connect**

> **Lưu ý:** Superset container đã được cài sẵn ODBC Driver 18 for SQL Server trong Dockerfile.

### 7.3. Tạo Datasets
1. **+ Add** → **Dataset**
2. Chọn database `DWH_RetailTech`
3. Chọn bảng: `FactSales`, `DimDate`, `DimProduct`, `DimStore`, ...

### 7.4. Tạo Charts
Dùng SQL templates trong `superset/dashboards/` làm reference để tạo charts trong Superset UI.

### 7.5. Chia sẻ Dashboard (nhúng vào portal)

Sau khi tạo dashboard, bật **Embedded** để nhúng vào portal:

1. Mở Dashboard → Edit → **Public** → **Enable embedded**
2. Copy **Embedded SDK** code
3. Dashboard sẽ được nhúng qua guest token từ backend

> Trong môi trường multi-tenant, mỗi tenant sẽ thấy dashboard với dữ liệu từ database của tenant đó. Xem chi tiết ở **[10.6 Superset Multi-tenant](#106-superset-multi-tenant)**.

## 8. Reset hệ thống

### Reset toàn bộ (xóa dữ liệu + schema)
```bash
docker compose down -v
docker compose up -d
```
⚠️ Mất hết dữ liệu và schema. Init scripts chạy lại tự động.

### Reset chỉ dữ liệu (giữ schema)
```bash
./sql_runner.sh "TRUNCATE TABLE FactSales; TRUNCATE TABLE FactInventory; TRUNCATE TABLE FactPurchase;"
python -m etl.main_etl --full
```

## 9. Cấu trúc thư mục

```
datn/
├── docker-compose.yml           # Docker Compose (SQL Server, Superset, Redis, Postgres)
├── .env                        # ⚠️ Cấu hình DUY NHẤT - tất cả passwords ở đây
├── run_sql.sh                  # Script chạy tất cả SQL scripts
├── README.md                   # File này
│
├── sql/                        # === DATABASE ===
│   ├── 01_init/               # Tạo database
│   ├── 02_staging/            # Bảng Staging (7 bảng)
│   ├── 03_system/            # System tables (Watermark, RunLog, ErrorLog)
│   ├── 04_dim/                # Dimension tables (6 bảng)
│   ├── 05_fact/               # Fact tables (3 bảng)
│   ├── 06_datamart/           # Data Mart tables (2 bảng)
│   ├── 07_indexes/            # Indexes + FK constraints
│   └── 08_stored_procedures/ # Stored Procedures + Orchestrator
│
├── etl/                        # === ETL PIPELINE ===
│   ├── config.py               # Cấu hình (đọc từ .env)
│   ├── logger.py              # Logging (rotate theo ngày)
│   ├── main_etl.py            # Orchestrator chính
│   ├── requirements.txt        # Python dependencies
│   ├── extract/               # 7 modules đọc Excel/CSV
│   ├── transform/              # Clean, normalize, validate
│   └── load/                  # Bulk insert vào Staging
│
├── data/                       # === DATA ===
│   ├── sources/                # File nguồn thực tế
│   └── samples/               # Mock data generator + output
│
├── superset/                   # === BI ===
│   ├── docker-compose.superset.yml
│   ├── init_superset.sh
│   ├── connections/           # SQLAlchemy URI template
│   └── dashboards/           # 5 dashboard configs (FR-10 → FR-14)
│
└── docs/
    └── sql_execution_order.md  # Chi tiết thứ tự chạy SQL
```

## Công nghệ sử dụng

| Thành phần | Công nghệ | Ghi chú |
|---|---|---|
| Database | SQL Server 2022 | Docker, per-tenant databases |
| ETL Engine | Python 3.10+ | pandas, pyodbc, sqlalchemy |
| Transform | T-SQL Stored Procedures | SCD Type 2 cho DimProduct |
| Scheduling | APScheduler | Chạy tự động hàng ngày |
| BI Platform | Apache Superset 3.1.1 | Docker, embedded, ODBC Driver 18 |
| Cache | Redis 7 | Docker |
| Metadata DB | PostgreSQL 15 | Docker (cho Superset) |
| Backend API | FastAPI | Python, JWT auth, multi-tenant |
| Frontend | React + Vite | TailwindCSS, Lucide Icons, Responsive |

---

## 10. Nâng cấp: Multi-tenant SaaS Platform

### 10.1. Tổng quan

Nâng cấp hệ thống từ single-tenant → **SaaS Multi-tenant**:
- **Admin Portal**: Quản lý tenants, users, upload, ETL
- **User Portal**: Xem dashboard, upload file
- **Per-tenant isolation**: Mỗi tenant = 1 database riêng
- **Superset embedded**: BI charts nhúng trong React

### 10.2. Kiến trúc

```
                    INTERNET
                       │
         ┌─────────────┴─────────────┐
         │                             │
    Admin Portal                  User Portal
    (React, :3000/admin)      (React, :3000/user)
         │                             │
         └──────────────┬────────────┘
                        │
                  FastAPI Backend
                   (:8000/api)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   TenantDB_001    TenantDB_002    TenantDB_003
   (SQL Server)    (SQL Server)    (SQL Server)
        │               │               │
        ▼               ▼               ▼
   Superset      Superset       Superset
```

### 10.3. User Roles

| Role | Quyền |
|------|--------|
| SuperAdmin | Quản lý tenants, tạo user, upload file, chạy ETL, xem log |
| TenantAdmin | Quản lý user trong tenant, upload file, chạy ETL |
| User | Upload file, xem dashboard (Superset embed) |

### 10.4. API Endpoints

```bash
# Auth
POST /api/auth/login     # Login → JWT token
POST /api/auth/logout    # Logout
GET  /api/auth/me        # Current user

# SuperAdmin
GET    /api/admin/tenants           # List tenants
POST   /api/admin/tenants           # Tạo tenant + DB
DELETE /api/admin/tenants/{id}     # Xóa tenant
GET    /api/admin/users             # List all users
POST   /api/admin/users            # Tạo user
DELETE /api/admin/users/{id}       # Xóa user

# Tenant Admin
GET    /api/tenant/users           # Users trong tenant
POST   /api/tenant/users           # Tạo user trong tenant
DELETE /api/tenant/users/{id}     # Xóa user

# Upload & ETL
POST /api/upload                   # Upload file
GET  /api/upload                   # List files
POST /api/etl/run                 # Trigger ETL
GET  /api/etl/status             # ETL status
GET  /api/etl/history             # ETL history

# Embed & Stats
GET /api/embed/guest-token        # Superset guest token
GET /api/stats                    # KPIs tổng quan
```

### 10.5. Database Design

```sql
-- DWH_Master (metadata)
CREATE TABLE Tenants (
    TenantId     VARCHAR(50) PRIMARY KEY,
    TenantName  NVARCHAR(200) NOT NULL,
    DatabaseName VARCHAR(100) NOT NULL UNIQUE,
    Plan        VARCHAR(20) DEFAULT 'trial',
    IsActive    BIT DEFAULT 1,
    CreatedAt   DATETIME2 DEFAULT GETDATE()
);

CREATE TABLE Users (
    UserId       INT IDENTITY PRIMARY KEY,
    TenantId    VARCHAR(50) NOT NULL,
    Username    VARCHAR(100) NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role        VARCHAR(20) NOT NULL, -- SuperAdmin, TenantAdmin, User
    IsActive    BIT DEFAULT 1,
    CreatedAt   DATETIME2 DEFAULT GETDATE()
);

-- DWH_TenantXXX (per tenant - giống schema hiện tại)
-- STG_*, Dim*, Fact*, DM_* per tenant.
```

### 10.6. Superset Multi-tenant

#### Kiến trúc chung

```
┌──────────────────────────────────────────────────────┐
│           1 Superset Instance (duy nhất)             │
│                                                      │
│  Dashboard #1 ──┬── TenantA → sees DWH_TenantA data  │
│                └── TenantB → sees DWH_TenantB data    │
│                                                      │
│  Một chart/dashboard — mỗi tenant thấy dữ liệu khác │
└──────────────────────────────────────────────────────┘
```

**Điểm mấu chốt:**
- **1 Superset** duy nhất, chia sẻ cho tất cả tenants
- **Mỗi tenant có database riêng** trong Superset (DWH_TenantA, DWH_TenantB, ...)
- **Guest token chỉ định database** → tenant chỉ truy vấn đúng database của mình
- **Cô lập dữ liệu tuyệt đối** — không cần RLS clause vì mỗi tenant đã có DB riêng

#### Ai làm gì

| Ai | Nhiệm vụ |
|----|-----------|
| **SuperAdmin** | Thêm database connections, tạo datasets, charts, dashboards trong Superset UI |
| **Backend** | Tự động đăng ký database vào Superset khi tenant cần |
| **Tenant User** | Nhấn "Mở Dashboard" trong portal — thấy dữ liệu tenant mình |

#### Bước 1: SuperAdmin cấu hình Superset (thủ công, làm 1 lần)

Superset admin đăng nhập tại `http://localhost:8088` (`SUPERSET_ADMIN_USER` / `SUPERSET_ADMIN_PASSWORD` trong `.env`):

```
1. Thêm Database Connections
   Settings → Database → + Database
   → Thêm DWH_RetailTech (và các DWH_{tenant_id} khi tạo tenant mới)
   → Database: Microsoft SQL Server
   → SQLAlchemy URI:
     mssql+pyodbc://sa:{PASSWORD}@datn_mssql:1433/DWH_TenantA
     ?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes

2. Tạo Datasets
   + Add → Dataset → Chọn database → Chọn bảng (FactSales, DimProduct, ...)

3. Tạo Charts
   + New → Chart → Chọn dataset → Tạo chart

4. Tạo Dashboard
   Dashboards → + Dashboard → Thêm charts đã tạo

5. Chia sẻ Dashboard
   Dashboard → Edit → Public → Enable embedded
```

#### Bước 2: Tenant User truy cập Dashboard (tự động)

```
Tenant User đăng nhập portal
  → Trang Reports → Nhấn "Mở Dashboard"
    → Backend gọi /api/embed/superset-token
      → Backend đăng ký DWH_{tenant_id} vào Superset (nếu chưa có)
      → Tạo guest_token chỉ định đúng database của tenant
      → Trả về token
    → Frontend embed iframe với guest_token
      → Superset chỉ truy vấn DWH_{tenant_id} của user đó
      → User chỉ thấy dữ liệu doanh nghiệp mình
```

#### Backend auto-provisioning

Backend tự động thực hiện khi tenant user cần truy cập Superset:

```python
# services/superset_admin.py
ensure_tenant_superset_setup(tenant_id):
  1. register_tenant_database(tenant_id, db_name)
     → Đăng ký DWH_{tenant_id} vào Superset
     → Lấy database_id

  2. create_or_get_tenant_user(tenant_id)
     → Tạo Superset user: tenant_{tenant_id}

  3. create_or_get_tenant_role(tenant_id)
     → Tạo Superset role: Tenant_{tenant_id}

  4. assign_user_to_role(username, role_id)
     → Gán user vào role
```

Auto-provisioning kích hoạt khi:
- SuperAdmin tạo TenantAdmin hoặc User
- TenantAdmin tạo User
- User đầu tiên truy cập trang Reports

#### Guest token cơ chế

```json
// Token cho TenantA → chỉ truy vấn DWH_TenantA
{
  "user": { "username": "tenant_TenantA" },
  "resources": [{ "type": "database", "id": 3 }]
}

// Token cho TenantB → chỉ truy vấn DWH_TenantB
{
  "user": { "username": "tenant_TenantB" },
  "resources": [{ "type": "database", "id": 4 }]
}
```

Superset chỉ query vào **đúng database** mà token chỉ định — không cần RLS clause vì data đã cô lập ở database level.

#### Cấu hình `.env`

```bash
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=YourSupersetAdminPassword
SUPERSET_URL=http://datn_superset:8088
```

> **Lưu ý:** Superset credentials phải khớp với user được tạo lúc container khởi động (`SUPERSET_ADMIN_USER`, `SUPERSET_ADMIN_PASSWORD` trong `docker-compose.yml`).

### 10.7. Cấu trúc thư mục

```
backend/                  # FastAPI (Port 8000)
├── main.py              # FastAPI app
├── auth.py             # JWT authentication
├── models/
│   ├── master.py      # Tenants, Users tables
│   └── database.py    # Multi-DB connection manager
├── api/
│   ├── tenants.py     # /api/admin/tenants/*
│   ├── users.py       # /api/admin/users/*, /api/tenant/users/*
│   ├── upload.py      # /api/upload/*
│   ├── etl.py         # /api/etl/*
│   └── embed.py       # /api/embed/*
└── services/
    ├── db_service.py       # Tạo DB per tenant
    └── etl_service.py     # Chạy ETL subprocess

frontend/                 # React + Vite (Port 3000)
├── src/pages/
│   ├── Login.tsx
│   ├── admin/
│   │   ├── Tenants.tsx    # Quản lý tenants
│   │   ├── Users.tsx     # Quản lý users
│   │   └── ETLRuns.tsx    # Lịch sử ETL
│   └── user/
│       ├── Dashboard.tsx  # KPIs dashboard
│       ├── Upload.tsx     # Upload file
│       └── Reports.tsx    # Superset embed
└── Dockerfile
```

### 10.8. Khởi động SaaS Platform

```bash
# Build & start tất cả
docker compose -f docker-compose.saas.yml up -d

# Tạo SuperAdmin đầu tiên
docker compose exec backend python -m app.init_superadmin
```

Xem chi tiết đầy đủ tại: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

Đồ án tốt nghiệp - Trường Đại học Thủy Lợi - 2025-2026
