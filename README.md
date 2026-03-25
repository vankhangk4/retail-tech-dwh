# 🛍️ Retail Tech DWH SaaS Platform

> Hệ thống Data Warehouse SaaS (Multi-tenant) cho ngành bán lẻ, tích hợp ETL + BI Dashboard nhúng Superset với cơ chế bảo mật Row-Level Security (RLS).

---

## 📌 1) Giới thiệu dự án (Overview)

Retail Tech DWH là nền tảng phân tích dữ liệu bán lẻ theo mô hình SaaS, cho phép nhiều doanh nghiệp (tenant) dùng chung một hệ thống nhưng vẫn **cô lập dữ liệu tuyệt đối**.

### Mục tiêu chính
- Tập trung dữ liệu từ file nguồn (Excel/CSV) vào Data Warehouse.
- Chuẩn hóa pipeline ETL để nạp dữ liệu định kỳ.
- Cung cấp dashboard trực quan (Superset) cho từng tenant.
- Đảm bảo multi-tenant isolation bằng **Guest Token + RLS**.

### Refactor kiến trúc mới (đã hoàn thành)
Hệ thống đã chuyển từ mô hình cũ:
- ❌ Mỗi tenant một database + clone dashboard riêng

sang mô hình mới:
- ✅ **1 Shared Database** (phân tách bằng cột `TenantId`)
- ✅ **1 Shared Superset Dashboard**
- ✅ **Guest Token + RLS clause** để lọc dữ liệu theo tenant

---

## 🧭 2) Kiến trúc hệ thống (System Architecture & Flow)

### 2.1 Kiến trúc tổng quan

```text
Data Sources (Excel/CSV theo tenant)
            │
            ▼
      Python ETL Pipeline
            │
            ▼
   SQL Server Shared DWH
 (Dim/Fact/Datamart + TenantId)
            │
            ▼
       FastAPI Backend
   (Auth + ETL API + Embed API)
            │
            ▼
   Superset (1 shared dashboard)
            │
            ▼
      React Frontend (iframe)
```

### 2.2 Cơ chế RLS mới (core)

1. Dữ liệu của tất cả tenant lưu trong **1 DB dùng chung** (`SHARED_DWH_DB`, mặc định `DWH_RetailTech`).
2. Các bảng chính (Dim/Fact/Datamart) có cột `TenantId`.
3. Khi user bấm **Mở Dashboard**, Frontend gọi backend endpoint:
   - `GET /api/embed/superset-token`
4. Backend tạo Guest Token từ Superset API, kèm RLS clause:
   - `TenantId = '<tenant_id>'`
5. Superset nhận token, tự động áp điều kiện RLS vào query khi render dashboard.
6. Kết quả: cùng 1 dashboard, mỗi tenant chỉ thấy dữ liệu của tenant mình.

### 2.3 Embed an toàn
- Backend không lộ Superset admin credential ra frontend.
- Guest Token ngắn hạn, phát theo từng user request.
- Hỗ trợ SuperAdmin impersonation qua `X-Impersonate-Tenant`.

---

## 🧰 3) Công nghệ sử dụng (Tech Stack)

### Backend
- **FastAPI** (Python)
- **SQLAlchemy**
- **JWT Auth** (`python-jose`)
- **Passlib/Bcrypt**
- **HTTPX** (gọi Superset API)

### Frontend
- **React 18**
- **Vite**
- **Axios**

### Data & BI
- **Microsoft SQL Server 2022** (Shared DWH)
- **Apache Superset 3.1.1**
- **Redis** (cache Superset)
- **PostgreSQL** (Superset metadata + Master metadata)
- **Python ETL** (pandas, pyodbc, APScheduler)

### DevOps
- **Docker / Docker Compose**

---

## 📁 4) Cấu trúc thư mục (Folder Structure)

```text
retail_tech_dwh/
├── backend/                  # FastAPI API (auth, tenants, users, upload, etl, embed, stats)
├── frontend/                 # React portal cho SuperAdmin/TenantAdmin/User
├── etl/                      # ETL pipeline (extract/load + orchestrator)
├── sql/                      # SQL schema + procedures (staging/dim/fact/datamart)
├── superset/                 # Superset config + Dockerfile + dashboard assets
├── data/                     # Dữ liệu sources/samples
├── run_sql.sh                # Chạy toàn bộ SQL scripts theo thứ tự
├── sql_runner.sh             # Chạy query/file SQL ad-hoc
└── docker-compose.yml        # Orchestration toàn stack
```

---

## 🚀 5) Hướng dẫn cài đặt và chạy dự án (Getting Started)

## 5.1 Clone source

```bash
git clone <YOUR_REPO_URL>
cd retail_tech_dwh
```

## 5.2 Tạo file môi trường `.env`

Dự án cần file `.env` tại root để:
- Docker Compose inject biến môi trường
- script `run_sql.sh`, `sql_runner.sh` hoạt động

Bạn có thể tạo nhanh từ file mẫu backend:

```bash
cp backend/.env.example .env
```

Sau đó chỉnh lại các giá trị quan trọng (đặc biệt là secret/password) cho môi trường của bạn.

### Biến môi trường quan trọng cần có

```env
# SQL Server
MSSQL_SA_PASSWORD=your_strong_password
MSSQL_PORT=1433
MSSQL_HOST=datn_mssql

# Master metadata DB
MASTER_DB_USER=postgres
MASTER_DB_PASSWORD=your_master_password
MASTER_DB_NAME=DWH_Master

# Auth
JWT_SECRET_KEY=your_jwt_secret
DEFAULT_ADMIN_PASSWORD=your_superadmin_password

# Superset
SUPERSET_ADMIN_USER=admin
SUPERSET_ADMIN_PASSWORD=your_superset_admin_password
SUPERSET_ADMIN_EMAIL=admin@example.com
SUPERSET_SECRET_KEY=your_superset_secret
SUPERSET_PORT=8088

# Shared dashboard ID (BẮT BUỘC cho mô hình mới)
SUPERSET_SHARED_DASHBOARD_ID=1

# Shared DWH DB name (khuyến nghị giữ mặc định)
SHARED_DWH_DB=DWH_RetailTech
```

> ✅ **Lưu ý quan trọng:** `SUPERSET_SHARED_DASHBOARD_ID` phải trỏ đúng dashboard đã bật Embedded trong Superset.

## 5.3 Build và chạy Docker Compose

```bash
docker compose up -d --build
```

Kiểm tra nhanh:

```bash
docker compose ps
docker compose logs -f backend
```

## 5.4 Khởi tạo database ban đầu (chạy SQL scripts)

Sau khi stack đã lên, chạy:

```bash
chmod +x run_sql.sh
./run_sql.sh
```

Script này sẽ chạy tuần tự:
- `sql/01_init` → `sql/08_stored_procedures`
- Tạo staging, dim, fact, datamart và SP ETL.

Kiểm tra nhanh DB:

```bash
./sql_runner.sh "SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='dbo'"
./sql_runner.sh "SELECT COUNT(*) AS DimDateRows FROM DimDate"
```

---

## 🧪 6) Hướng dẫn sử dụng (Usage)

## 6.1 Truy cập hệ thống

- Frontend: `http://localhost:3000`
- Backend API docs: `http://localhost:8000/docs`
- Superset: `http://localhost:8088`

## 6.2 Tạo tenant mới

Bạn có thể tạo tenant bằng UI (SuperAdmin) hoặc API.

### API tạo tenant
Endpoint:
- `POST /api/admin/tenants`

Ví dụ body:

```json
{
  "TenantId": "techstore_hcm",
  "TenantName": "Tech Store HCM",
  "Plan": "trial"
}
```

> Với kiến trúc mới, tạo tenant **không tạo DB vật lý mới**; chỉ tạo metadata tenant trong master DB.

## 6.3 Upload dữ liệu theo tenant

Endpoint upload:
- `POST /api/upload`

File được lưu theo thư mục tenant:
- `/app/uploads/<tenant_id>/...`

## 6.4 Chạy ETL để nạp dữ liệu

### Cách khuyến nghị (trong container backend)

```bash
docker compose exec backend python -m etl.main_etl --tenant techstore_hcm --full
```

### Chạy local (nếu đã cài đủ dependencies)

```bash
python -m etl.main_etl --tenant techstore_hcm --full
```

Theo dõi trạng thái bằng API:
- `POST /api/etl/run`
- `GET /api/etl/status/{run_id}`
- `GET /api/etl/history`
- `GET /api/etl/logs/{run_id}`

## 6.5 Xem báo cáo Dashboard

1. User đăng nhập portal.
2. Vào trang Reports và bấm **Mở Dashboard**.
3. Frontend gọi `GET /api/embed/superset-token`.
4. Backend trả về:
   - `token`
   - `dashboard_id` (shared)
   - `superset_url`
5. Frontend embed iframe Superset bằng guest token.

Kết quả: cùng dashboard, dữ liệu tự lọc theo `TenantId` nhờ RLS.

---

## 🔐 7) Ghi chú bảo mật & vận hành

- Không commit `.env` chứa secret thật.
- Bắt buộc thay mật khẩu mặc định trước khi public demo/production.
- Trong production, siết `CORS`, giới hạn `allow_origins`, và cấu hình HTTPS/reverse proxy.

---

## 🧱 8) Lệnh hữu ích

```bash
# Xem logs backend
docker compose logs -f backend

# Xem logs Superset
docker compose logs -f superset

# Chạy query nhanh SQL
./sql_runner.sh "SELECT TOP 10 * FROM FactSales"

# Reset toàn bộ dữ liệu volume
docker compose down -v
docker compose up -d --build
```

---

## 👨‍💻 9) Thông tin học thuật (Đồ án/Portfolio)


Điểm nhấn kiến trúc:
- Multi-tenant SaaS chuẩn hóa
- Shared infrastructure tối ưu chi phí
- Isolation bằng RLS token-based trên Superset embed
