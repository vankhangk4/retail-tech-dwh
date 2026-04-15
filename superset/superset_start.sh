#!/bin/bash
# ============================================================
# FILE: superset/superset_start.sh
# Mô tả: Startup script cho superset service (dwh_project-superset image)
# 1. Chạy Superset web server bằng gunicorn (background)
# 2. Chờ server sẵn sàng
# 3. Chạy provisioning (tạo datasource, datasets, dashboards, RLS)
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

echo "[superset] Running provisioning..."
PYTHONPATH=/app/superset_scripts python /superset_scripts/provision.py 2>&1 || echo "[superset] Provisioning done (may already exist)"

echo "[superset] Provisioning complete. Server running on PID: $SERVER_PID"
wait $SERVER_PID