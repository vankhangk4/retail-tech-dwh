-- ============================================================
-- FILE: sql/_vars.sql
-- Tu dong tao boi sql/_read_env_and_build.py
-- Doc gia tri tu .env -> truyen vao 00_init.sql qua SQLCMD variables
-- ============================================================
--   DEFAULT_ADMIN_USER  = admin
--   DEFAULT_ADMIN_PASS  = ********
--   DEFAULT_ADMIN_ROLE  = superadmin
-- ============================================================
-- Chinh sua gia tri o day neu can, hoac doi truc tiep trong .env
-- roi chay lai: python sql/_read_env_and_build.py
-- ============================================================

:setvar DEFAULT_ADMIN_USER  "admin"
:setvar DEFAULT_ADMIN_PASS  "M1tjtnrx"
:setvar DEFAULT_ADMIN_ROLE  "superadmin"
