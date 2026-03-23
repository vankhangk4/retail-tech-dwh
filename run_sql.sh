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

HOST="${MSSQL_HOST:-datn_mssql}"
PORT="${MSSQL_PORT:-1433}"
PASSWORD="${MSSQL_SA_PASSWORD}"
DB="DWH_RetailTech"

# Tự động detect network của container MSSQL
NETWORK=$(docker network ls --format '{{.Name}}' | while read n; do
    if docker network inspect "$n" --format '{{range .Containers}}{{.Name}}{{end}}' 2>/dev/null | grep -q "datn_mssql"; then
        echo "$n"
    fi
done | head -1)

if [ -z "$NETWORK" ]; then
    echo "ERROR: Không tìm thấy network của container datn_mssql"
    echo "Đảm bảo docker compose đang chạy: docker compose up -d"
    exit 1
fi

echo "Detected network: $NETWORK"

# Pull mssql-tools container
echo "Pulling mssql-tools image..."
docker pull mcr.microsoft.com/mssql-tools:latest

# Hàm chạy SQL file (không silent - hiện lỗi)
run_sql() {
    local file="$1"
    local rel_path="${file#$SCRIPT_DIR/}"
    echo "  Running: $(basename "$file")"
    docker run --rm \
        --network "${NETWORK}" \
        -v "${SCRIPT_DIR}:/scripts" \
        mcr.microsoft.com/mssql-tools \
        /opt/mssql-tools/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C \
        -d "${DB}" \
        -i "/scripts/${rel_path}"
}

# Chờ SQL Server ready
echo ""
echo "Waiting for SQL Server to be ready..."
for i in {1..30}; do
    if docker run --rm --network "${NETWORK}" \
        mcr.microsoft.com/mssql-tools \
        /opt/mssql-tools/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C \
        -Q "SELECT 1" > /dev/null 2>&1; then
        echo "SQL Server is ready!"
        break
    fi
    echo "  Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "========================================"
echo "  Running SQL Scripts"
echo "========================================"

echo ""
echo ">>> [1] Init Database..."
docker run --rm \
    --network "${NETWORK}" \
    -v "${SCRIPT_DIR}:/scripts" \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${HOST}" -U sa -P "${PASSWORD}" -C \
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
# Watermark SPs phai chay truoc vi sp_Main_ETL goi cac SP nay
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_watermark.sql"
# Load dimension/fact SPs
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_dim_customer.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_dim_employee.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_dim_product.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_dim_store.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_dim_supplier.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_fact_inventory.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_fact_purchase.sql"
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_load_fact_sales.sql"
# Main orchestrator chay cuoi cung (phu thuoc tat ca SP tren)
run_sql "${SCRIPT_DIR}/sql/08_stored_procedures/sp_main_etl.sql"

echo ""
echo "========================================"
echo "  All SQL Scripts Completed!"
echo "========================================"
echo ""
echo "Verification:"
docker run --rm --network "${NETWORK}" \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${HOST}" -U sa -P "${PASSWORD}" -C \
    -d "${DB}" \
    -Q "SELECT COUNT(*) AS TableCount FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo'"

docker run --rm --network "${NETWORK}" \
    mcr.microsoft.com/mssql-tools \
    /opt/mssql-tools/bin/sqlcmd \
    -S "${HOST}" -U sa -P "${PASSWORD}" -C \
    -d "${DB}" \
    -Q "SELECT COUNT(*) AS DimDateRows FROM DimDate"

echo ""
echo "Done!"
