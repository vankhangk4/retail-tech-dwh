# Thứ tự chạy SQL Scripts cho DWH_RetailTech

## Tổng quan

Chạy scripts SQL theo thứ tự để tạo schema DWH.

## Cách hoạt động

- Init scripts nằm trong `./sql/`, được mount vào SQL Server container
- Chạy qua `mssql-tools` container (Microsoft official image)
- Tất cả cấu hình đọc từ `.env`

## Chạy tất cả SQL scripts (khuyến nghị)

```bash
chmod +x run_sql.sh
./run_sql.sh
```

## Chạy riêng từng file

### Tạo database
```bash
docker run --rm --network datn_datn_network \
    -v "$(pwd):/scripts" \
    mcr.microsoft.com/mssql-tools18 \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C -No \
    -i "/scripts/sql/01_init/init_database.sql"
```

### Tạo Staging tables
```bash
docker run --rm --network datn_datn_network \
    -v "$(pwd):/scripts" \
    mcr.microsoft.com/mssql-tools18 \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C -No \
    -d DWH_RetailTech \
    -i "/scripts/sql/02_staging/stg_tables.sql"
```

### Tạo các bảng còn lại
```bash
for f in sql/04_dim/*.sql sql/05_fact/*.sql sql/06_datamart/*.sql sql/07_indexes/*.sql sql/08_stored_procedures/*.sql; do
  docker run --rm --network datn_datn_network \
      -v "$(pwd):/scripts" \
      mcr.microsoft.com/mssql-tools18 \
      /opt/mssql-tools18/bin/sqlcmd \
      -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C -No \
      -d DWH_RetailTech \
      -i "/scripts/$f"
done
```

## Kiểm tra sau khi chạy

```bash
# Kiểm tra databases
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools18 \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C -No \
    -Q "SELECT name FROM sys.databases"

# Kiểm tra số bảng
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools18 \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C -No \
    -d DWH_RetailTech \
    -Q "SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'"

# Kiểm tra DimDate
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools18 \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${MSSQL_HOST}" -U sa -P "${MSSQL_SA_PASSWORD}" -C -No \
    -d DWH_RetailTech \
    -Q "SELECT COUNT(*) AS DimDateRows FROM DimDate"
```

## Thứ tự phụ thuộc

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
