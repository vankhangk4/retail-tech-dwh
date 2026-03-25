# ============================================================
# config.py - Cau hinh ket noi va duong dan
# Doc tu .env - KHONG hardcode bat ky gia tri nao
# ============================================================
import os
import re
from pathlib import Path
from typing import Iterable
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
_MSSQL_HOST_IN_DOCKER = os.getenv("MSSQL_HOST", "datn_mssql")
MSSQL_PORT = os.getenv("MSSQL_PORT", "1433")
MSSQL_USER = "sa"
MSSQL_PASSWORD = os.getenv("MSSQL_SA_PASSWORD")
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

print(f"[config] Server={MSSQL_SERVER}:{MSSQL_PORT}, DB={MSSQL_DATABASE}, Driver={MSSQL_DRIVER}")
print(f"[config] Sales file: {SALES_FILE}")
print(f"[config] Running in Docker: {RUNNING_IN_DOCKER}")


def get_tenant_conn_str(tenant_id: str) -> str:
    """Shared DB model: tenant context is logical only, connection stays the same."""
    return CONN_STR


def get_tenant_data_dir(tenant_id: str) -> Path:
    """Trả về thư mục data upload của tenant: /app/uploads/{tenant_id}/"""
    upload_dir = Path(os.getenv("UPLOAD_DIR", "/app/uploads"))
    return upload_dir / tenant_id


def _normalize_name(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _find_preferred_file(tenant_dir: Path, candidates: Iterable[str]) -> Path | None:
    """Find file by exact candidate names first, then by safe fuzzy contains match."""
    if not tenant_dir.exists():
        return None

    existing = [p for p in tenant_dir.iterdir() if p.is_file()]
    if not existing:
        return None

    candidate_list = list(candidates)

    # 1) Exact match (case-insensitive)
    lower_map = {p.name.lower(): p for p in existing}
    for c in candidate_list:
        found = lower_map.get(c.lower())
        if found:
            return found

    # 2) Safe Fuzzy Match: strip digits to get core keyword
    norm_files = [(p, _normalize_name(p.stem)) for p in existing]
    for c in candidate_list:
        needle = _normalize_name(Path(c).stem)
        if not needle:
            continue

        # Strip digits (2025, 2024...) to get core keyword for safe matching
        core_needle = re.sub(r'\d+', '', needle)

        # Only match if core keyword is long enough (>=4, avoid too-broad matches)
        if len(core_needle) < 4:
            continue

        for p, stem_norm in norm_files:
            # Safe contains: core keyword must be contained in the uploaded filename
            if core_needle in stem_norm:
                return p

    return None


def get_tenant_file_paths(tenant_id: str) -> dict:
    """
    Trả về mapping file paths cho tenant.

    Ưu tiên:
    1) Tên chuẩn expected
    2) Fuzzy theo keyword
    3) Fallback về data/sources mặc định
    """
    tenant_dir = get_tenant_data_dir(tenant_id)

    file_map = {
        "SALES_FILE": (
            ["BaoCaoDoanhThu_2025.xlsx", "sales.xlsx", "sales.csv", "doanhthu.xlsx"],
            SALES_FILE,
        ),
        "INVENTORY_FILE": (
            ["QuanLyKho_2025.xlsx", "inventory.xlsx", "inventory.csv", "tonkho.xlsx"],
            INVENTORY_FILE,
        ),
        "PRODUCT_FILE": (
            ["DanhMucSanPham.csv", "product.csv", "products.csv", "sanpham.csv"],
            PRODUCT_FILE,
        ),
        "CUSTOMER_FILE": (
            ["DanhSachKhachHang.csv", "customer.csv", "customers.csv", "khachhang.csv"],
            CUSTOMER_FILE,
        ),
        "STORE_FILE": (
            ["DanhSachCuaHang.csv", "store.csv", "stores.csv", "cuahang.csv"],
            STORE_FILE,
        ),
        "EMPLOYEE_FILE": (
            ["DanhSachNhanVien.csv", "employee.csv", "employees.csv", "nhanvien.csv"],
            EMPLOYEE_FILE,
        ),
        "SUPPLIER_FILE": (
            ["DanhSachNhaCungCap.csv", "supplier.csv", "suppliers.csv", "nhacungcap.csv"],
            SUPPLIER_FILE,
        ),
    }

    result = {}
    for key, (candidates, fallback) in file_map.items():
        preferred = _find_preferred_file(tenant_dir, candidates)
        result[key] = preferred if preferred is not None else fallback

    return result
