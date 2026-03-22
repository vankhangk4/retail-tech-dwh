# ============================================================
# config.py - Cau hinh ket noi va duong dan
# Doc tu .env - KHONG hardcode bat ky gia tri nao
# ============================================================
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env tu thu muc project root
PROJECT_ROOT = Path(__file__).parent.parent
_dotenv_path = PROJECT_ROOT / ".env"
load_dotenv(_dotenv_path)

# ---- Base Paths ----
DATA_DIR = PROJECT_ROOT / "data"
SOURCES_DIR = DATA_DIR / "sources"
SAMPLES_DIR = DATA_DIR / "samples"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---- SQL Server Connection (doc tu .env) ----
# MSSQL_HOST trong .env = container name (dung trong Docker network)
# Khi chay tren host, dung localhost (port 1433 da map ra host)
_MSSQL_HOST_IN_DOCKER = os.getenv("MSSQL_HOST", "datn_mssql")
MSSQL_PORT = os.getenv("MSSQL_PORT", "1433")
MSSQL_USER = "sa"
MSSQL_PASSWORD = os.getenv("MSSQL_SA_PASSWORD")  # doc tu .env
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "DWH_RetailTech")

# ODBC Driver - auto detect
import pyodbc as _pyodbc
_ODBC_DRIVERS = _pyodbc.drivers()
MSSQL_DRIVER = os.getenv("MSSQL_DRIVER", None)
if not MSSQL_DRIVER or MSSQL_DRIVER not in _ODBC_DRIVERS:
    MSSQL_DRIVER = None
    for d in _ODBC_DRIVERS:
        if "ODBC Driver 18" in d:
            MSSQL_DRIVER = d
            break
    if not MSSQL_DRIVER:
        for d in _ODBC_DRIVERS:
            if "ODBC Driver 17" in d:
                MSSQL_DRIVER = d
                break
    if not MSSQL_DRIVER:
        for d in _ODBC_DRIVERS:
            if "ODBC Driver" in d or "SQL Server" in d:
                MSSQL_DRIVER = d
                break
    if not MSSQL_DRIVER:
        MSSQL_DRIVER = _ODBC_DRIVERS[-1] if _ODBC_DRIVERS else "ODBC Driver 17 for SQL Server"

# Server: localhost khi chay host, container name khi chay trong Docker
RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
MSSQL_SERVER = _MSSQL_HOST_IN_DOCKER if RUNNING_IN_DOCKER else "localhost"

# ---- Connection Strings ----
CONN_STR = (
    f"DRIVER={{{MSSQL_DRIVER}}};"
    f"SERVER={MSSQL_SERVER},{MSSQL_PORT};"
    f"DATABASE={MSSQL_DATABASE};"
    f"UID={MSSQL_USER};"
    f"PWD={MSSQL_PASSWORD};"
    f"TrustServerCertificate=yes;"
    f"Connection Timeout=30;"
)

SQLALCHEMY_URI = (
    f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}@"
    f"{MSSQL_SERVER}:{MSSQL_PORT}/{MSSQL_DATABASE}?"
    f"driver={MSSQL_DRIVER.replace(' ', '+')}&TrustServerCertificate=yes"
)

# ---- File Paths ----
SALES_FILE = SOURCES_DIR / "BaoCaoDoanhThu_2025.xlsx"
INVENTORY_FILE = SOURCES_DIR / "QuanLyKho_2025.xlsx"
PRODUCT_FILE = SOURCES_DIR / "DanhMucSanPham.csv"
CUSTOMER_FILE = SOURCES_DIR / "DanhSachKhachHang.csv"
STORE_FILE = SOURCES_DIR / "DanhSachCuaHang.csv"
EMPLOYEE_FILE = SOURCES_DIR / "DanhSachNhanVien.csv"
SUPPLIER_FILE = SOURCES_DIR / "DanhSachNhaCungCap.csv"

# Fallback to sample data if sources dir is empty
if not SOURCES_DIR.exists() or not any(SOURCES_DIR.iterdir()):
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    SALES_FILE = SAMPLES_DIR / "BaoCaoDoanhThu_2025.xlsx"
    INVENTORY_FILE = SAMPLES_DIR / "QuanLyKho_2025.xlsx"
    PRODUCT_FILE = SAMPLES_DIR / "DanhMucSanPham.csv"
    CUSTOMER_FILE = SAMPLES_DIR / "DanhSachKhachHang.csv"
    STORE_FILE = SAMPLES_DIR / "DanhSachCuaHang.csv"
    EMPLOYEE_FILE = SAMPLES_DIR / "DanhSachNhanVien.csv"
    SUPPLIER_FILE = SAMPLES_DIR / "DanhSachNhaCungCap.csv"

# ---- ETL Settings ----
BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "5000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ETL_TIMEOUT_SECONDS = int(os.getenv("ETL_TIMEOUT_SECONDS", "1800"))

# ---- Print config (debug) ----
print(f"[config] Server={MSSQL_SERVER}:{MSSQL_PORT}, DB={MSSQL_DATABASE}, Driver={MSSQL_DRIVER}")
print(f"[config] Sales file: {SALES_FILE}")
print(f"[config] Running in Docker: {RUNNING_IN_DOCKER}")
