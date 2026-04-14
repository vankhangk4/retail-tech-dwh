#!/bin/bash
# ============================================================
# FILE: superset/superset_init.sh
# Mô tả: Startup script cho superset service
# Chạy provisioning sau khi Superset web server đã sẵn sàng
# ============================================================

set -e

echo "[superset] Starting Superset..."

# Đợi Superset web server sẵn sàng
echo "[superset] Waiting for Superset web server..."
for i in $(seq 1 30); do
    if curl -sf http://localhost:8088/health > /dev/null 2>&1; then
        echo "[superset] Web server ready"
        break
    fi
    echo "[superset] Waiting... ($i/30)"
    sleep 2
done

# Chạy provisioning (tạo datasource, datasets, dashboards, RLS)
echo "[superset] Running Superset provisioning..."
python /app/provision.py 2>&1 || echo "[superset] Provisioning skipped (may already exist)"

# Chạy Superset
echo "[superset] Starting web server..."
exec superset run --with-threads --reload --host 0.0.0.0 --port 8088
