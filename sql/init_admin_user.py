#!/usr/bin/env python3
"""
sql/init_admin_user.py
Doc .env -> kiem tra/tao bang AppUsers -> insert/update superadmin voi bcrypt hash.

Docker: chay qua mssql-init container sau khi MSSQL healthy.
ADS:    chay tay sau khi 00_init.sql da chay xong.

Phu thuoc: pip install passlib[bcrypt] pymssql python-dotenv
"""

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

MSSQL_HOST     = os.environ.get('MSSQL_SERVER',     'localhost')
MSSQL_PORT     = int(os.environ.get('MSSQL_PORT',   '1433'))
MSSQL_USER     = os.environ.get('MSSQL_USER',       'sa')
MSSQL_PASSWORD = os.environ.get('MSSQL_PASSWORD',    '')
MSSQL_DATABASE = os.environ.get('MSSQL_DATABASE',    'DWH_MultiTenant')


def load_env(path: str) -> dict:
    env = {}
    if not os.path.exists(path):
        # Thu tai thu muc goc (docker) hoac thu muc sql (ADS)
        alt = os.path.join(SCRIPT_DIR, '..', '.env')
        if os.path.exists(alt):
            path = alt
        else:
            print(f"[WARN] .env not found at {path} or {alt}", file=sys.stderr)
            return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def ensure_table(cursor):
    """Tao bang AppUsers neu chua ton tai."""
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AppUsers')
    BEGIN
        CREATE TABLE AppUsers (
            UserID        INT IDENTITY(1,1) PRIMARY KEY,
            Username      VARCHAR(100) NOT NULL UNIQUE,
            PasswordHash  VARCHAR(255) NOT NULL,
            TenantID      VARCHAR(20)  NULL,
            Role          VARCHAR(20)  NOT NULL DEFAULT 'viewer',
            IsActive      BIT          NOT NULL DEFAULT 1,
            CreatedAt     DATETIME2    NOT NULL DEFAULT GETDATE(),
            CONSTRAINT CHK_AppUsers_Role CHECK (Role IN ('admin', 'viewer', 'superadmin'))
        );
        PRINT 'Created table: AppUsers';
    END
    """)
    print("[OK] Table AppUsers ready")


def upsert_user(cursor, username: str, password_hash: str, role: str):
    """Insert hoac update superadmin."""
    cursor.execute('SELECT UserID FROM AppUsers WHERE Username = %s', (username,))
    row = cursor.fetchone()
    if row:
        cursor.execute(
            'UPDATE AppUsers SET PasswordHash = %s, Role = %s, TenantID = NULL, IsActive = 1 '
            'WHERE Username = %s',
            (password_hash, role, username)
        )
        print(f"[OK] Updated: {username} | role={role}")
    else:
        cursor.execute(
            'INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive) '
            'VALUES (%s, %s, NULL, %s, 1)',
            (username, password_hash, role)
        )
        print(f"[OK] Created: {username} | role={role}")


def wait_for_mssql(max_retries=15, delay=5):
    """Cho MSSQL san sang truoc khi ket noi."""
    import time
    import pymssql
    for i in range(max_retries):
        try:
            conn = pymssql.connect(
                server=MSSQL_HOST,
                user=MSSQL_USER,
                password=MSSQL_PASSWORD,
                database=MSSQL_DATABASE,
                port=MSSQL_PORT,
                login_timeout=5,
            )
            conn.close()
            print(f"[OK] MSSQL san sang (lan {i+1})")
            return True
        except Exception as e:
            print(f"[WARN] Thu {i+1}/{max_retries}: {e}")
            time.sleep(delay)
    print("[ERROR] Khong ket noi duoc MSSQL sau {max_retries} lan")
    return False


def main():
    # Doc .env
    env = load_env(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))
    username = env.get('DEFAULT_ADMIN_USER', 'admin').strip()
    password = env.get('DEFAULT_ADMIN_PASS', '').strip()
    role     = env.get('DEFAULT_ADMIN_ROLE', 'superadmin').strip()

    if not username or not password:
        print("[SKIP] DEFAULT_ADMIN_USER or DEFAULT_ADMIN_PASS not set in .env")
        sys.exit(0)

    # Hash password
    try:
        from passlib.context import CryptContext
        pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
        password_hash = pwd_ctx.hash(password)
    except ImportError:
        print("[ERROR] pip install passlib[bcrypt]")
        sys.exit(1)

    print(f"[INFO] MSSQL   : {MSSQL_HOST}:{MSSQL_PORT}/{MSSQL_DATABASE}")
    print(f"[INFO] MSSQL_PW: {'*' * len(MSSQL_PASSWORD)} (MSSQL_PASSWORD={repr(MSSQL_PASSWORD)})")
    print(f"[INFO] User    : {username} | Role: {role}")

    # Cho MSSQL san sang
    if not wait_for_mssql():
        sys.exit(1)

    import pymssql
    conn = pymssql.connect(
        server=MSSQL_HOST,
        user=MSSQL_USER,
        password=MSSQL_PASSWORD,
        database=MSSQL_DATABASE,
        port=MSSQL_PORT,
    )
    cursor = conn.cursor()
    conn.commit()

    # Dam bao bang ton tai
    ensure_table(cursor)
    conn.commit()

    # Upsert superadmin
    upsert_user(cursor, username, password_hash, role)
    conn.commit()

    cursor.close()
    conn.close()
    print("[DONE] Superadmin ready — có thể đăng nhập ngay!")


if __name__ == '__main__':
    main()
