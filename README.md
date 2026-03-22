# DATN - Data Warehouse & BI System

Xây dựng hệ thống Data Warehouse và trực quan hóa dữ liệu kinh doanh cho chuỗi cửa hàng bán lẻ thiết bị công nghệ.

**Sinh viên:** Nguyễn Văn Khang (MSSV: 2251162042) - Lớp 64HTTT4
**GVHD:** Đỗ Oanh Cường, Nguyễn Tu Trung

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
docker compose up -d

# Kiểm tra trạng thái
docker compose ps
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

# Kiểm tra database đã được tạo
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C \
    -Q "SELECT name FROM sys.databases"

# Kiểm tra DimDate (~5840 rows)
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C \
    -d DWH_RetailTech \
    -Q "SELECT COUNT(*) FROM DimDate"
```

## 5. Sinh dữ liệu mẫu

### 5.1. Cài Python dependencies
```bash
pip install -r etl/requirements.txt
```

### 5.2. Sinh mock data
```bash
cd data/samples
python generate_mock_data.py
```

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
cd /home/khang/Desktop/datn

# Chạy một lần
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
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C \
    -d DWH_RetailTech \
    -Q "SELECT COUNT(*) FROM FactSales"

docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C \
    -d DWH_RetailTech \
    -Q "SELECT * FROM ETL_RunLog ORDER BY LoadDatetime DESC"
```

## 7. Kết nối Superset

### 7.1. Truy cập Superset
```
http://localhost:8088
```
Login: `admin` / `admin` (hoặc credentials trong `.env`)

### 7.2. Thêm Database Connection
1. **Settings** → **Database Connections** → **+ Add Database**
2. Chọn: **Microsoft SQL Server**
3. SQLAlchemy URI:
   ```
   mssql+pyodbc://sa:${MSSQL_SA_PASSWORD}@mssql:1433/DWH_RetailTech?driver=ODBC+Driver+18+for+SQL+Server
   ```
   Thay `${MSSQL_SA_PASSWORD}` bằng giá trị trong `.env` hoặc dùng biến môi trường nếu Superset hỗ trợ.
4. **Test Connection** → **Save**

### 7.3. Tạo Datasets
1. **+ Add** → **Import Dataset**
2. Chọn database `DWH_RetailTech`
3. Chọn bảng: `FactSales`, `DimDate`, `DimProduct`, `DimStore`, ...

### 7.4. Tạo Charts
Dùng SQL templates trong `superset/dashboards/` làm reference để tạo charts trong Superset UI.

## 8. Reset hệ thống

### Reset toàn bộ (xóa dữ liệu + schema)
```bash
docker compose down -v
docker compose up -d
```
⚠️ Mất hết dữ liệu và schema. Init scripts chạy lại tự động.

### Reset chỉ dữ liệu (giữ schema)
```bash
# Xóa dữ liệu trong các bảng
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C \
    -d DWH_RetailTech \
    -Q "TRUNCATE TABLE FactSales; TRUNCATE TABLE FactInventory; TRUNCATE TABLE FactPurchase;"

# Chạy lại ETL
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
| Database | SQL Server 2022 | Docker, custom image có mssql-tools |
| ETL Engine | Python 3.10+ | pandas, pyodbc, sqlalchemy |
| Transform | T-SQL Stored Procedures | SCD Type 2 cho DimProduct |
| Scheduling | APScheduler | Chạy tự động hàng ngày |
| BI Platform | Apache Superset 3.1.1 | Docker |
| Cache | Redis 7 | Docker |
| Metadata DB | PostgreSQL 15 | Docker (cho Superset) |

---

Đồ án tốt nghiệp - Trường Đại học Thủy Lợi - 2025-2026
