#!/bin/bash
# ============================================================
# sql_runner.sh - Chạy SQL scripts trong SQL Server
# Sử dụng mssql-tools container chính chủ của Microsoft
# Usage: ./sql_runner.sh "SELECT 1"
#        ./sql_runner.sh --file sql/01_init/init_database.sql
# ============================================================

set -e

# Load .env
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
set -a
source "${SCRIPT_DIR}/.env"
set +a

PASSWORD="${MSSQL_SA_PASSWORD}"
HOST="${MSSQL_HOST:-datn_mssql}"
PORT="${MSSQL_PORT:-1433}"
DB="${MSSQL_DB:-DWH_RetailTech}"

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

# Nếu có file SQL
if [ "$1" = "--file" ]; then
    SQL_FILE="$2"
    if [ ! -f "$SQL_FILE" ]; then
        echo "ERROR: File not found: $SQL_FILE"
        exit 1
    fi
    echo "Running SQL file: $SQL_FILE"
    docker run --rm --network "${NETWORK}" \
        -v "${SCRIPT_DIR}:/scripts" \
        mcr.microsoft.com/mssql-tools \
        /opt/mssql-tools/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C \
        -d "${DB}" \
        -i "/scripts/${SQL_FILE}"
else
    # Chạy query trực tiếp
    QUERY="$1"
    echo "Running query: $QUERY"
    docker run --rm --network "${NETWORK}" \
        mcr.microsoft.com/mssql-tools \
        /opt/mssql-tools/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C \
        -d "${DB}" \
        -Q "${QUERY}"
fi
