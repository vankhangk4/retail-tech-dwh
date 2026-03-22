#!/bin/bash
# ============================================================
# init_superset.sh
# Initialize Superset: create admin, connect DB, create datasets
# ============================================================

set -e

SUPERSET_HOST="${SUPERSET_HOST:-localhost}"
SUPERSET_PORT="${SUPERSET_PORT:-8088}"
ADMIN_USER="${SUPERSET_ADMIN_USER:-admin}"
ADMIN_PASS="${SUPERSET_ADMIN_PASS:-admin}"

echo "Waiting for Superset to be ready..."
until curl -s "http://${SUPERSET_HOST}:${SUPERSET_PORT}/health" > /dev/null 2>&1; do
    echo "  Waiting..."
    sleep 5
done

echo "Superset is ready!"

# Create admin user
echo "Creating admin user..."
docker exec datn_superset \
    superset fab create-admin \
    --username "${ADMIN_USER}" \
    --password "${ADMIN_PASS}" \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --role Admin 2>/dev/null || true

# Initialize
echo "Initializing Superset..."
docker exec datn_superset superset init

echo ""
echo "========================================"
echo "  Superset initialized successfully!"
echo "  URL: http://${SUPERSET_HOST}:${SUPERSET_PORT}"
echo "  Login: ${ADMIN_USER} / ${ADMIN_PASS}"
echo "========================================"
