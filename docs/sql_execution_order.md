# Thứ tự chạy SQL Scripts cho DWH_RetailTech

## Tổng quan

Chạy các scripts SQL theo thứ tự số thứ tự để đảm bảo tính toàn vẹn ràng buộc (FK).

## Thứ tự chạy

### Giai đoạn 1: Khởi tạo Database
```bash
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -i sql/01_init/init_database.sql
```

### Giai đoạn 2: Tạo bảng (Layers)
```bash
# 2.1. Tạo Staging tables
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/02_staging/stg_tables.sql

# 2.2. Tạo System tables (Watermark, RunLog, ErrorLog)
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/03_system/system_tables.sql

# 2.3. Tạo Dimension tables
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/04_dim/dim_date.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/04_dim/dim_product.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/04_dim/dim_customer.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/04_dim/dim_store.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/04_dim/dim_employee.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/04_dim/dim_supplier.sql

# 2.4. Tạo Fact tables
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/05_fact/fact_sales.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/05_fact/fact_inventory.sql
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/05_fact/fact_purchase.sql

# 2.5. Tạo Data Mart tables
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/06_datamart/dm_tables.sql

# 2.6. Tạo Indexes và Constraints
sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i sql/07_indexes/create_indexes.sql
```

### Giai đoạn 3: Tạo Stored Procedures
```bash
# Chạy tất cả SP files
for f in sql/08_stored_procedures/*.sql; do
    sqlcmd -S localhost -U sa -P YourStrong@Passw0rd123 -d DWH_RetailTech -i "$f"
done
```

### Giai đoạn 4: (Tùy chọn) Script chạy hàng loạt
```bash
./run_all_sql.sh
```

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
