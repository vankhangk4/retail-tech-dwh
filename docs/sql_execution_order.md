# Thứ tự chạy SQL Scripts cho DWH_RetailTech

## Tổng quan

Chạy các scripts SQL theo thứ tự số thứ tự để đảm bảo tính toàn vẹn ràng buộc (FK).

## Kết nối SQL Server trong Docker

SQL Server chạy trong container `datn_mssql`. Có 2 cách kết nối:

### Cách 1: Dùng `docker exec` (khuyến nghị - không cần cài gì thêm)
SQL Server container đã có sẵn `sqlcmd` bên trong:
```bash
# Cú pháp chung:
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 \
  -i /docker-entrypoint-initdb.d/sql/<duong_dan_file>.sql
```

### Cách 2: Cài `sqlcmd` trên máy host rồi kết nối qua port
```bash
# Linux (Ubuntu/Debian):
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list | \
  tee /etc/apt/sources.list.d/mssql-release.list
apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
export PATH="$PATH:/opt/mssql-tools/bin"

# Sau đó chạy:
sqlcmd -S localhost,1433 -U sa -P YourStrong@Passw0rd123 -i sql/01_init/init_database.sql
```

## Thứ tự chạy

### Giai đoạn 1: Khởi tạo Database
```bash
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 \
  -i /docker-entrypoint-initdb.d/sql/01_init/init_database.sql
```

### Giai đoạn 2: Tạo bảng (Layers)
```bash
# 2.1. Tạo Staging tables
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/02_staging/stg_tables.sql

# 2.2. Tạo System tables (Watermark, RunLog, ErrorLog)
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/03_system/system_tables.sql

# 2.3. Tạo Dimension tables
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/04_dim/dim_date.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/04_dim/dim_product.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/04_dim/dim_customer.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/04_dim/dim_store.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/04_dim/dim_employee.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/04_dim/dim_supplier.sql

# 2.4. Tạo Fact tables
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/05_fact/fact_sales.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/05_fact/fact_inventory.sql

docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/05_fact/fact_purchase.sql

# 2.5. Tạo Data Mart tables
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/06_datamart/dm_tables.sql

# 2.6. Tạo Indexes và Constraints
docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
  -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
  -i /docker-entrypoint-initdb.d/sql/07_indexes/create_indexes.sql
```

### Giai đoạn 3: Tạo Stored Procedures
```bash
for f in sql/08_stored_procedures/*.sql; do
  docker exec -i datn_mssql /opt/mssql-tools/bin/sqlcmd \
    -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech \
    -i /docker-entrypoint-initdb.d/"$f"
done
```

### Giai đoạn 4: Script chạy hàng loạt (khuyến nghị)
```bash
# Chạy script tự động
chmod +x run_sql.sh
./run_sql.sh
```
(Xem nội dung script bên dưới)

## Kiểm tra sau khi chạy

```sql
-- Kiểm tra số bảng đã tạo
SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo';

-- Kiểm tra DimDate đã được populate
SELECT COUNT(*) AS DimDateRows FROM DimDate;

-- Kiểm tra Watermark
SELECT * FROM ETL_Watermark;

-- Kiểm tra Stored Procedures
SELECT name FROM sys.procedures ORDER BY name;
```

## Thứ tự phụ thuộc (Dependency Order)

```
init_database (1)
    └── stg_tables (2)
    └── system_tables (3)
    └── dim_date (4)  ← Pre-populated
    └── dim_product (5)
    └── dim_customer (6)
    └── dim_store (7)
    └── dim_employee (8)
    └── dim_supplier (9)
    └── fact_sales (10)
    └── fact_inventory (11)
    └── fact_purchase (12)
    └── dm_tables (13)
    └── create_indexes (14) ← Tạo FK sau khi tất cả bảng tồn tại
    └── stored_procedures (15)
```
