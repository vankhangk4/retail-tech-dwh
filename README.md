# DATN - Data Warehouse & BI System
# Xây dựng hệ thống Data Warehouse và trực quan hóa dữ liệu kinh doanh
# cho chuỗi cửa hàng bán lẻ thiết bị công nghệ

Sinh viên: **Nguyễn Văn Khang** (MSSV: 2251162042)
Lớp: 64HTTT4
GVHD: Đỗ Oanh Cường, Nguyễn Tu Trung

---

## Mục lục

1. [Kiến trúc hệ thống](#1-kiến-trúc-hệ-thống)
2. [Yêu cầu](#2-yêu-cầu)
3. [Cài đặt](#3-cài-đặt)
4. [Chạy ETL Pipeline](#4-chạy-etl-pipeline)
5. [Kết nối Superset](#5-kết-nối-superset)
6. [Cấu trúc thư mục](#6-cấu-trúc-thư-mục)

---

## 1. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Data Sources (Excel/CSV)                          │
│   BaoCaoDoanhThu | QuanLyKho | DanhMucSanPham | DanhSachKhachHang  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ EXTRACT (Python)
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGING Layer (SQL Server)                        │
│     STG_SalesRaw | STG_InventoryRaw | STG_ProductRaw | ...          │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ TRANSFORM (SP + Python)
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CORE DWH (SQL Server)                             │
│   DimDate | DimProduct(SCD2) | DimCustomer | DimStore | DimEmployee│
│   FactSales | FactInventory | FactPurchase                          │
│   DM_SalesDailySummary | DM_InventoryAlert                          │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ QUERY
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BI Layer (Apache Superset)                         │
│   FR-10: Dashboard Doanh thu | FR-11: Dashboard Sản phẩm            │
│   FR-12: Dashboard Tồn kho | FR-13: Dashboard Khách hàng           │
│   FR-14: Dashboard Nhân viên                                         │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Yêu cầu

- Python 3.10+
- Docker & Docker Compose
- ODBC Driver 17 for SQL Server

### Cài đặt Python dependencies
```bash
cd /home/khang/Desktop/datn
pip install -r etl/requirements.txt
```

### Cài đặt ODBC Driver (Linux)
```bash
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### Cài đặt ODBC Driver (macOS)
```bash
brew install microsoft/mssql-release/msodbcsql17
```

## 3. Cài đặt

### Bước 1: Khởi động SQL Server
```bash
docker compose up -d mssql

# Chờ SQL Server khởi động (~30s)
docker compose ps
```

### Bước 2: Chạy SQL Scripts
```bash
# Chạy theo thứ tự
for f in sql/01_init/*.sql sql/02_staging/*.sql sql/03_system/*.sql \
         sql/04_dim/*.sql sql/05_fact/*.sql sql/06_datamart/*.sql \
         sql/07_indexes/*.sql sql/08_stored_procedures/*.sql; do
    sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i "$f"
done
```

Hoặc xem chi tiết trong `docs/sql_execution_order.md`.

### Bước 3: Tạo dữ liệu mẫu
```bash
cd data/samples
pip install -r ../../etl/requirements.txt
python generate_mock_data.py

# Copy vào thư mục sources
mkdir -p ../../data/sources
cp *.xlsx *.csv ../../data/sources/
```

### Bước 4: Chạy ETL Pipeline
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

### Bước 5: Khởi động Superset
```bash
docker compose -f superset/docker-compose.superset.yml up -d

# Chờ Superset khởi động (~2-3 phút)
./superset/init_superset.sh
```

Truy cập: http://localhost:8088
Login: `admin` / `admin`

## 4. Chạy ETL Pipeline

### Cấu hình
Chỉnh sửa `.env` để cập nhật:
```
MSSQL_PASSWORD=YourStrong@Passw0rd123
MSSQL_HOST=localhost
```

### Kiểm tra log
```bash
tail -f logs/etl_$(date +%Y%m%d).log
```

### Kiểm tra dữ liệu sau ETL
```sql
SELECT COUNT(*) FROM FactSales;
SELECT COUNT(*) FROM FactInventory;
SELECT COUNT(*) FROM DimProduct;
SELECT * FROM ETL_RunLog ORDER BY LoadDatetime DESC;
```

## 5. Kết nối Superset

### Thêm Database Connection
1. Settings → Database Connections → + Add Database
2. Chọn: Microsoft SQL Server
3. SQLAlchemy URI:
   ```
   mssql+pyodbc://sa:YourStrong@Passw0rd123@mssql:1433/DWH_RetailTech?driver=ODBC+Driver+17+for+SQL+Server
   ```
4. Test Connection → Save

### Tạo Datasets
1. + Add → Import Dataset
2. Chọn database `DWH_RetailTech`
3. Chọn bảng: `FactSales`, `DimDate`, `DimProduct`, `DimStore`, ...

### Tạo Charts
Import dashboard configs từ `superset/dashboards/`:

```bash
# Import dashboard qua CLI
docker exec -it datn_superset superset import_dashboards \
    -f /docker/superset/dashboards/dashboard_01_revenue.py
```

Hoặc tạo thủ công trong Superset UI.

## 6. Cấu trúc thư mục

```
datn/
├── docker-compose.yml           # SQL Server + Superset (full stack)
├── .env                         # Environment variables
├── README.md                    # File này
│
├── sql/                         # === DATABASE ===
│   ├── 01_init/                # Tạo database
│   ├── 02_staging/             # Bảng Staging (7 bảng)
│   ├── 03_system/              # System tables (Watermark, RunLog, ErrorLog)
│   ├── 04_dim/                 # Dimension tables (6 bảng)
│   ├── 05_fact/                # Fact tables (3 bảng)
│   ├── 06_datamart/            # Data Mart tables (2 bảng)
│   ├── 07_indexes/             # Indexes + FK constraints
│   └── 08_stored_procedures/   # Stored Procedures
│
├── etl/                         # === ETL PIPELINE ===
│   ├── config.py               # Cấu hình kết nối
│   ├── logger.py               # Logging setup
│   ├── main_etl.py             # Orchestrator
│   ├── requirements.txt        # Python dependencies
│   ├── extract/                # Extract modules (7 files)
│   ├── transform/              # Transform modules (4 files)
│   └── load/                   # Load to staging
│
├── data/                       # === DATA ===
│   ├── sources/                # File nguồn thực tế
│   └── samples/                # Dữ liệu mẫu + generator
│
├── superset/                   # === BI ===
│   ├── docker-compose.superset.yml
│   ├── init_superset.sh
│   ├── connections/
│   └── dashboards/            # 5 dashboard configs (FR-10 → FR-14)
│
└── docs/
    └── sql_execution_order.md  # Hướng dẫn chạy SQL
```

## Công nghệ sử dụng

| Thành phần | Công nghệ | Phiên bản |
|---|---|---|
| Database | SQL Server | 2022 |
| ETL Engine | Python | 3.10+ |
| Libraries | pandas, pyodbc, sqlalchemy | Latest |
| Transform | T-SQL Stored Procedures | SQL Server 2022 |
| Scheduling | APScheduler | 3.10+ |
| BI Platform | Apache Superset | 3.1.1 |
| Container | Docker Compose | Latest |

## License

Đồ án tốt nghiệp - Trường Đại học Thủy Lợi - 2025-2026
