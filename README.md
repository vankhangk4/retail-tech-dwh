# Data Warehouse Multi-Tenant — Chuỗi Cửa hàng Bán lẻ Thiết bị Công nghệ

Đồ án tốt nghiệp — Nguyễn Văn Khang — 64HTTT4

## Tổng quan

Hệ thống Data Warehouse đa người dùng (Multi-Tenant) cho chuỗi cửa hàng bán lẻ thiết bị công nghệ, bao gồm:

- **ETL Pipeline** tự động (Extract → Transform → Load)
- **Auth Gateway** (FastAPI + JWT) — xác thực multi-tenant
- **Apache Superset** — Dashboard BI với Row Level Security
- **SQL Server** — Data Warehouse với Star Schema

## Cấu trúc dự án

```
dwh_project/
├── api/                  # Auth Gateway FastAPI
│   ├── main.py          # FastAPI app
│   ├── auth.py          # /login, /dashboard-token, /me
│   └── models.py        # Pydantic models
├── etl/
│   ├── extract/
│   │   └── extract_sales.py   # Đọc Excel, watermark, gắn TenantID
│   ├── transform/
│   │   └── transform_sales.py  # Chuẩn hóa, loại trùng, xử lý NULL
│   └── orchestrator/
│       └── main_etl.py        # ETL Orchestrator — vòng lặp tenant
├── sql/
│   ├── 00_run_all_schema.sql  # Chạy tất cả schema
│   ├── schema/                 # DDL bảng
│   │   ├── 01_create_tenants.sql
│   │   ├── 02_create_dimensions.sql
│   │   ├── 03_create_facts.sql
│   │   ├── 04_create_staging.sql
│   │   └── 05_create_datamart.sql
│   ├── sp/                    # Stored Procedures
│   │   ├── usp_Load_DimDate.sql
│   │   ├── usp_Load_DimProduct.sql
│   │   ├── usp_Load_DimCustomer.sql
│   │   ├── usp_Transform_FactSales.sql
│   │   ├── usp_Transform_FactInventory.sql
│   │   ├── usp_Transform_FactPurchase.sql
│   │   ├── usp_Refresh_DM_SalesSummary.sql
│   │   └── usp_Refresh_DM_CustomerRFM.sql
│   └── views/
│       └── v_FactSales_ByTenant.sql
├── superset/
│   ├── superset_config.py     # Cấu hình Superset (RLS, security)
│   ├── docker-compose.yml    # Superset standalone
│   └── scripts/
│       └── create_users.py   # Tạo users hàng loạt
├── data/
│   ├── STORE_HN/             # File Excel/CSV của Hà Nội
│   └── STORE_HCM/            # File Excel/CSV của HCM
├── monitoring/               # (Sắp tới)
├── docker-compose.yml        # Tổng hợp toàn bộ services
├── Dockerfile.api            # Auth Gateway Docker image
├── requirements.txt          # Python dependencies
└── .env                      # Biến môi trường (KHÔNG commit Git)
```

## Bắt đầu nhanh

### 1. Cài đặt biến môi trường

```bash
cp .env.example .env  # hoặc chỉnh sửa .env
# Chỉnh JWT_SECRET_KEY, MSSQL_SA_PASSWORD, SUPERSET_ADMIN_PWD
```

### 2. Khởi động toàn bộ hệ thống (Docker)

```bash
docker-compose up -d
```

### 3. Chạy SQL Schema

```bash
# Kết nối SQL Server → chạy sql/00_run_all_schema.sql
```

### 4. Khởi động Superset

```bash
cd superset/
cp ../.env .env
docker-compose up -d
```

### 5. Chạy ETL

```bash
pip install -r requirements.txt
python etl/orchestrator/main_etl.py
```

## Luồng hoạt động

```
1. User đăng nhập → POST /auth/login → JWT token (chứa tenant_id)
2. User xin dashboard token → GET /auth/dashboard-token → Superset Guest Token
3. Superset query → tự động append WHERE tenant_id='X' (RLS)
4. ETL Scheduler (02:00 SA) → Vòng lặp qua mỗi tenant → Load data
5. Nếu ETL lỗi → Email + Slack alert trong 5 phút
```

## Multi-Tenant

| Role | Xem dữ liệu | Quyền |
|------|-------------|-------|
| Admin | Toàn bộ mọi tenant | Toàn quyền |
| Tenant Viewer | Chỉ tenant của mình | Chỉ đọc Dashboard |

## Tài khoản mặc định

| Username | Password | Role | Tenant |
|---------|---------|------|--------|
| admin | Admin@1234 | admin | — |
| manager_hn | Pass@HN123 | viewer | STORE_HN |
| manager_hcm | Pass@HCM123 | viewer | STORE_HCM |

## API Endpoints

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | `/auth/login` | Đăng nhập → JWT |
| POST | `/auth/refresh` | Đổi refresh token |
| GET | `/auth/dashboard-token` | Lấy Superset Guest Token |
| GET | `/auth/me` | Thông tin user hiện tại |
| GET | `/health` | Health check |

## Yêu cầu

- Python 3.10+
- Docker + Docker Compose
- SQL Server 2019/2022
- ODBC Driver 17 for SQL Server
