#!/bin/bash
# ============================================================
# run_sql.sh - Chạy tất cả SQL scripts theo thứ tự
# Usage: ./run_sql.sh
# ============================================================

set -e

CONTAINER="datn_mssql"
PASSWORD="YourStrong@Passw0rd123"
SQLCMD="/opt/mssql-tools18/bin/sqlcmd"

# Kiểm tra container đang chạy
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "ERROR: Container '${CONTAINER}' is not running."
    echo "Run: docker compose up -d"
    exit 1
fi

# Hàm chạy 1 file SQL
run_sql() {
    local file="$1"
    local dir=$(dirname "$file")
    local basename=$(basename "$file")
    echo "  Running: $basname"
    docker exec -i "${CONTAINER}" ${SQLCMD} \
        -S localhost -U sa -P "${PASSWORD}" -d DWH_RetailTech \
        -i "/docker-entrypoint-initdb.d/${file}" > /dev/null 2>&1
}

cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "  Running SQL Scripts"
echo "========================================"

echo ""
echo ">>> [1] Init Database..."
docker exec -i "${CONTAINER}" ${SQLCMD} \
    -S localhost -U sa -P "${PASSWORD}" \
    -i /docker-entrypoint-initdb.d/sql/01_init/init_database.sql

echo ""
echo ">>> [2] Staging Tables..."
run_sql "sql/02_staging/stg_tables.sql"

echo ""
echo ">>> [3] System Tables..."
run_sql "sql/03_system/system_tables.sql"

echo ""
echo ">>> [4] Dimension Tables..."
for f in sql/04_dim/*.sql; do
    echo "  $(basename $f)"
    docker exec -i "${CONTAINER}" ${SQLCMD} \
        -S localhost -U sa -P "${PASSWORD}" -d DWH_RetailTech \
        -i "/docker-entrypoint-initdb.d/$f" > /dev/null 2>&1 || true
done

echo ""
echo ">>> [5] Fact Tables..."
for f in sql/05_fact/*.sql; do
    echo "  $(basename $f)"
    docker exec -i "${CONTAINER}" ${SQLCMD} \
        -S localhost -U sa -P "${PASSWORD}" -d DWH_RetailTech \
        -i "/docker-entrypoint-initdb.d/$f" > /dev/null 2>&1 || true
done

echo ""
echo ">>> [6] Data Mart Tables..."
run_sql "sql/06_datamart/dm_tables.sql"

echo ""
echo ">>> [7] Indexes & Constraints..."
run_sql "sql/07_indexes/create_indexes.sql"

echo ""
echo ">>> [8] Stored Procedures..."
for f in sql/08_stored_procedures/*.sql; do
    echo "  $(basename $f)"
    docker exec -i "${CONTAINER}" ${SQLCMD} \
        -S localhost -U sa -P "${PASSWORD}" -d DWH_RetailTech \
        -i "/docker-entrypoint-initdb.d/$f" > /dev/null 2>&1 || true
done

echo ""
echo "========================================"
echo "  All SQL Scripts Completed!"
echo "========================================"
echo ""
echo "Verification:"
docker exec -i "${CONTAINER}" ${SQLCMD} \
    -S localhost -U sa -P "${PASSWORD}" -d DWH_RetailTech \
    -Q "SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'"

docker exec -i "${CONTAINER}" ${SQLCMD} \
    -S localhost -U sa -P "${PASSWORD}" -d DWH_RetailTech \
    -Q "SELECT COUNT(*) AS DimDateRows FROM DimDate"

echo ""
echo "Done!"
