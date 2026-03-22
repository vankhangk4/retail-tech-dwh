# ============================================================
# config.py - Cấu hình kết nối và đường dẫn
# ============================================================
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---- Base Paths ----
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SOURCES_DIR = DATA_DIR / "sources"
SAMPLES_DIR = DATA_DIR / "samples"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ---- SQL Server Connection ----
MSSQL_SERVER = os.getenv("MSSQL_HOST", "localhost")
MSSQL_PORT = os.getenv("MSSQL_PORT", "1433")
MSSQL_USER = os.getenv("MSSQL_USER", "sa")
MSSQL_PASSWORD = os.getenv("MSSQL_PASSWORD", "YourStrong@Passw0rd123")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "DWH_RetailTech")
MSSQL_DRIVER = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")

# PyODBC connection string
CONN_STR = (
    f"DRIVER={{{MSSQL_DRIVER}}};"
    f"SERVER={MSSQL_SERVER},{MSSQL_PORT};"
    f"DATABASE={MSSQL_DATABASE};"
    f"UID={MSSQL_USER};"
    f"PWD={MSSQL_PASSWORD};"
)

# SQLAlchemy URI
SQLALCHEMY_URI = (
    f"mssql+pyodbc://{MSSQL_USER}:{MSSQL_PASSWORD}@"
    f"{MSSQL_SERVER}:{MSSQL_PORT}/{MSSQL_DATABASE}?"
    f"driver={MSSQL_DRIVER.replace(' ', '+')}"
)

# ---- File Paths ----
SALES_FILE = SOURCES_DIR / "BaoCaoDoanhThu_2025.xlsx"
INVENTORY_FILE = SOURCES_DIR / "QuanLyKho_2025.xlsx"
PRODUCT_FILE = SOURCES_DIR / "DanhMucSanPham.csv"
CUSTOMER_FILE = SOURCES_DIR / "DanhSachKhachHang.csv"
STORE_FILE = SOURCES_DIR / "DanhSachCuaHang.csv"
EMPLOYEE_FILE = SOURCES_DIR / "DanhSachNhanVien.csv"
SUPPLIER_FILE = SOURCES_DIR / "DanhSachNhaCungCap.csv"

# Fallback to sample data
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
