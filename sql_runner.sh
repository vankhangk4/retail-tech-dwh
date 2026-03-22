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
HOST="${MSSQL_HOST:-localhost}"
PORT="${MSSQL_PORT:-1433}"

TOOLS_CONTAINER="datn_mssql_tools"

# Nếu có file SQL
if [ "$1" = "--file" ]; then
    SQL_FILE="$2"
    if [ ! -f "$SQL_FILE" ]; then
        echo "ERROR: File not found: $SQL_FILE"
        exit 1
    fi
    echo "Running SQL file: $SQL_FILE"
    docker run --rm --network datn_datn_network \
        -v "${SCRIPT_DIR}:/scripts" \
        mcr.microsoft.com/mssql-tools18 \
        /opt/mssql-tools18/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C -No \
        -i "/scripts/${SQL_FILE}"
else
    # Chạy query trực tiếp
    QUERY="$1"
    echo "Running query: $QUERY"
    docker run --rm --network datn_datn_network \
        mcr.microsoft.com/mssql-tools18 \
        /opt/mssql-tools18/bin/sqlcmd \
        -S "${HOST}" -U sa -P "${PASSWORD}" -C -No \
        -Q "${QUERY}"
fi
