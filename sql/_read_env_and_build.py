#!/usr/bin/env python3
"""
sql/_read_env_and_build.py

Doc gia tri tu .env -> tao file 00_init.sql + _vars.sql
de chay trong Azure Data Studio.

Usage:
    # 1. Chinh sua .env (thay doi DEFAULT_ADMIN_USER/PASS/ROLE)
    # 2. Chay script nay:
    python sql/_read_env_and_build.py
    # 3. Mo _bootstrap.sql trong ADS -> Ctrl+Shift+E

Script nay doc .env -> tao 2 file:
    sql/_bootstrap.sql   — tap hop (vars + init)
    sql/_vars.sql        — chi chua :setvar (de ban nhin & chinh sua)
"""

import re
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR   = os.path.dirname(SCRIPT_DIR)   # /home/khang/Desktop/dwh/dwh_project
ENV_FILE   = os.path.join(ROOT_DIR, '.env')
INIT_SQL   = os.path.join(SCRIPT_DIR, '00_init.sql')
VARS_FILE  = os.path.join(SCRIPT_DIR, '_vars.sql')
BOOT_FILE  = os.path.join(ROOT_DIR, '_bootstrap.sql')


def load_env(path: str) -> dict:
    """Doc .env tra ve dict."""
    env = {}
    if not os.path.exists(path):
        print(f"[WARN] {path} not found", file=sys.stderr)
        return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def escape_sql_var(val: str) -> str:
    """Escape gia tri cho SQLCMD :setvar."""
    return val.replace('"', '""')


def main():
    env = load_env(ENV_FILE)

    user     = env.get("DEFAULT_ADMIN_USER", "admin")
    password = env.get("DEFAULT_ADMIN_PASS", "changeme")
    role     = env.get("DEFAULT_ADMIN_ROLE", "superadmin")

    user_esc     = escape_sql_var(user)
    password_esc = escape_sql_var(password)
    role_esc     = escape_sql_var(role)

    # ---- Tao _vars.sql ----
    vars_sql = f"""-- ============================================================
-- FILE: sql/_vars.sql
-- Tu dong tao boi sql/_read_env_and_build.py
-- Doc gia tri tu .env -> truyen vao 00_init.sql qua SQLCMD variables
-- ============================================================
--   DEFAULT_ADMIN_USER  = {user}
--   DEFAULT_ADMIN_PASS  = {'*' * len(password)}
--   DEFAULT_ADMIN_ROLE  = {role}
-- ============================================================
-- Chinh sua gia tri o day neu can, hoac doi truc tiep trong .env
-- roi chay lai: python sql/_read_env_and_build.py
-- ============================================================

:setvar DEFAULT_ADMIN_USER  "{user_esc}"
:setvar DEFAULT_ADMIN_PASS  "{password_esc}"
:setvar DEFAULT_ADMIN_ROLE  "{role_esc}"
"""

    with open(VARS_FILE, "w", encoding="utf-8") as f:
        f.write(vars_sql)

    # ---- Tao _bootstrap.sql (noi dung day du) ----
    bootstrap_sql = f"""-- ============================================================
-- FILE: _bootstrap.sql  (AUTO-GENERATED)
-- Mo trong Azure Data Studio -> Ctrl+Shift+E de chay
-- ============================================================
-- Tu dong tao boi sql/_read_env_and_build.py
-- Chi can chay file nay, khong can chay 00_init.sql truc tiep
-- ============================================================

:setvar DEFAULT_ADMIN_USER  "{user_esc}"
:setvar DEFAULT_ADMIN_PASS  "{password_esc}"
:setvar DEFAULT_ADMIN_ROLE  "{role_esc}"

:r ./sql/00_init.sql
"""

    with open(BOOT_FILE, "w", encoding="utf-8") as f:
        f.write(bootstrap_sql)

    print(f"[OK] Da tao 2 file:")
    print(f"     sql/_vars.sql      <- :setvar directives (xem/chinh sua)")
    print(f"     _bootstrap.sql     <- file chay trong ADS")
    print()
    print(f"  DEFAULT_ADMIN_USER  = {user}")
    print(f"  DEFAULT_ADMIN_PASS  = {'*' * len(password)}")
    print(f"  DEFAULT_ADMIN_ROLE  = {role}")
    print()
    print("Buoc tiep theo:")
    print(f"  1. Mo file _bootstrap.sql trong Azure Data Studio")
    print("  2. Nhan Ctrl+Shift+E (Run Selection / Run) ")
    print("  3. Tat ca DB se duoc tao + superadmin se duoc insert!")


if __name__ == "__main__":
    main()
