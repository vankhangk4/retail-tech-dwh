#!/bin/bash
# ============================================================
# run_sql.sh - Chạy tất cả SQL scripts theo thứ tự
# Sử dụng mssql-tools container để kết nối vào SQL Server
# Usage: ./run_sql.sh
# ============================================================

set -e

# Load .env
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
source "${SCRIPT_DIR}/.env"
set +a

HOST="${MSSQL_HOST:-localhost}"
PORT="${MSSQL_PORT:-1433}"
PASSWORD="${MSSQL_SA_PASSWORD}"
DB="DWH_RetailTech"

# Pull mssql-tools container
echo "Pulling mssql-tools18 image..."
docker pull mcr.microsoft.com/mssql-tools18:2022-latest > /dev/null 2>&1

# Hàm chạy SQL file
run_sql() {
    local file="$1"
    local rel_path="${file#$SCRIPT_DIR/}"
    echo "  Running: $(basename "$file")"
    docker run --rm --network datn_datn_network \
        -v "${SCRIPT_DIR}:/scripts" \
        mcr.microsoft.com/mssql-tools18:2022-latest \
        /opt/mssql-tools18/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C -No \
        -d "${DB}" \
        -i "/scripts/${rel_path}" 2>/dev/null || {
        echo "  WARNING: $(basename "$file") skipped or failed"
    }
}

echo ""
echo "========================================"
echo "  Running SQL Scripts"
echo "========================================"

echo ""
echo ">>> [1] Init Database..."
docker run --rm --network datn_datn_network \
    -v "${SCRIPT_DIR}:/scripts" \
    mcr.microsoft.com/mssql-tools18:2022-latest \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${HOST}" -U sa -P "${PASSWORD}" -C -No \
    -i /scripts/sql/01_init/init_database.sql

echo ""
echo ">>> [2] Staging Tables..."
run_sql "${SCRIPT_DIR}/sql/02_staging/stg_tables.sql"

echo ""
echo ">>> [3] System Tables..."
run_sql "${SCRIPT_DIR}/sql/03_system/system_tables.sql"

echo ""
echo ">>> [4] Dimension Tables..."
for f in "${SCRIPT_DIR}"/sql/04_dim/*.sql; do
    run_sql "$f"
done

echo ""
echo ">>> [5] Fact Tables..."
for f in "${SCRIPT_DIR}"/sql/05_fact/*.sql; do
    run_sql "$f"
done

echo ""
echo ">>> [6] Data Mart Tables..."
run_sql "${SCRIPT_DIR}/sql/06_datamart/dm_tables.sql"

echo ""
echo ">>> [7] Indexes & Constraints..."
run_sql "${SCRIPT_DIR}/sql/07_indexes/create_indexes.sql"

echo ""
echo ">>> [8] Stored Procedures..."
for f in "${SCRIPT_DIR}"/sql/08_stored_procedures/*.sql; do
    run_sql "$f"
done

echo ""
echo "========================================"
echo "  All SQL Scripts Completed!"
echo "========================================"
echo ""
echo "Verification:"
docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools18:2022-latest \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${HOST}" -U sa -P "${PASSWORD}" -C -No \
    -d "${DB}" \
    -Q "SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'"

docker run --rm --network datn_datn_network \
    mcr.microsoft.com/mssql-tools18:2022-latest \
    /opt/mssql-tools18/bin/sqlcmd \
    -S "${HOST}" -U sa -P "${PASSWORD}" -C -No \
    -d "${DB}" \
    -Q "SELECT COUNT(*) AS DimDateRows FROM DimDate"

echo ""
echo "Done!"
