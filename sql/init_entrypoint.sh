#!/bin/bash
# ============================================================
# FILE: sql/init_entrypoint.sh
# Chay sau khi /docker-entrypoint-initdb.d/*.sql hoan tat.
# Noi chay: /docker-entrypoint-initdb.d/  (MSSQL Docker)
# ============================================================

set -e

echo "[init_entrypoint] MSSQL init SQL da chay xong."

# Chay Python script de insert superadmin voi bcrypt hash
if [ -f /app/sql/init_admin_user.py ]; then
    echo "[init_entrypoint] Dang khoi tao superadmin..."
    cd /app
    pip install --quiet passlib pymssql python-dotenv 2>/dev/null || true
    python3 sql/init_admin_user.py || echo "[WARN] Superadmin init skipped (db chua san sang)"
elif [ -f /docker-entrypoint-initdb.d/init_admin_user.py ]; then
    echo "[init_entrypoint] Dang khoi tao superadmin..."
    pip install --quiet passlib pymssql python-dotenv 2>/dev/null || true
    python3 /docker-entrypoint-initdb.d/init_admin_user.py || echo "[WARN] Superadmin init skipped"
else
    echo "[init_entrypoint] init_admin_user.py not found — skipping."
fi

echo "[init_entrypoint] Hoan tat."
