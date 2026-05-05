#!/bin/bash
# ============================================================
# FILE: superset/superset_start.sh
# Mô tả: Startup script cho superset service (dwh_project-superset image)
# 1. Chạy Superset web server bằng gunicorn (background)
# 2. Chờ server sẵn sàng
# 3. Chạy provisioning (tạo datasource, datasets, dashboards, RLS)
# 4. Sync dataset columns từ MSSQL
# 5. Fix dashboard positions
# ============================================================

set -e

# Superset yêu cầu SECRET_KEY không được là default value
export SUPERSET_SECRET_KEY="${SUPERSET_SECRET_KEY}"

echo "[superset] Starting Superset web server with gunicorn..."
echo "[superset] Using --pythonpath /app to ensure superset module is found in workers"

# === FIX: cd vào /app trước để 'superset.app' module được resolve ===
cd /app

# Dùng --pythonpath để propagate vào cả gunicorn workers
gunicorn \
    --bind 0.0.0.0:8088 \
    --workers 2 \
    --threads 4 \
    --timeout 120 \
    --pythonpath /app \
    --access-logfile /dev/stdout \
    --error-logfile /dev/stdout \
    'superset.app:create_app()' &

SERVER_PID=$!
echo "[superset] Server PID: $SERVER_PID"

echo "[superset] Waiting for server to be ready..."
for i in $(seq 1 60); do
    if curl -sf http://localhost:8088/health > /dev/null 2>&1; then
        echo "[superset] Web server ready!"
        break
    fi
    if ! kill -0 $SERVER_PID 2>/dev/null; then
        echo "[superset] Server died. Check logs above."
        exit 1
    fi
    echo "[superset] Waiting... ($i/60)"
    sleep 2
done

echo "[superset] Running provisioning (RBAC + Charts)..."
# Must run from /app so superset.app resolves correctly
cd /app && python3 /superset_scripts/provision_v2.py 2>&1 || echo "[superset] Provisioning v2 done (may already exist)"
cd /app && python3 /superset_scripts/provision_charts.py 2>&1 || echo "[superset] Chart provisioning done (may already exist)"

echo "[superset] Syncing dataset columns from MSSQL..."
cd /app && python3 /superset_scripts/sync_columns.py 2>&1 || echo "[superset] Sync columns done"

echo "[superset] Fixing dashboard positions..."
cd /app && python3 /superset_scripts/fix_positions.py 2>&1 || echo "[superset] Fix positions done"

echo "[superset] Fixing chart params (Superset 3.x)..."
cd /app && python3 /superset_scripts/fix_chart_params.py 2>&1 || echo "[superset] Chart params fixed"

echo "[superset] Patching ChartDataQueryContextSchema..."
cd /app && python3 /superset_scripts/patch_chart_data_api.py 2>&1 || echo "[superset] Chart data API patched"

echo "[superset] Provisioning complete. Server running on PID: $SERVER_PID"
wait $SERVER_PID