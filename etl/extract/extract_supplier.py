# ============================================================
# extract/extract_supplier.py
# Đọc dữ liệu nhà cung cấp từ CSV/Excel
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaNCC": "MaNCC",
    "Mã NCC": "MaNCC",
    "SupplierID": "MaNCC",
    "TenNCC": "TenNCC",
    "Tên NCC": "TenNCC",
    "SupplierName": "TenNCC",
    "QuocGia": "QuocGia",
    "Quốc Gia": "QuocGia",
    "Country": "QuocGia",
    "NguoiLienHe": "NguoiLienHe",
    "Người Liên Hệ": "NguoiLienHe",
    "ContactPerson": "NguoiLienHe",
    "DienThoai": "DienThoai",
    "Điện Thoại": "DienThoai",
    "Phone": "DienThoai",
    "Email": "Email",
    "DieuKhoanTT_Ngay": "DieuKhoanTT_Ngay",
    "Điều Khoản TT (Ngày)": "DieuKhoanTT_Ngay",
    "PaymentTerm": "DieuKhoanTT_Ngay",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
    df = df.rename(columns=rename_map)
    return df


def extract_supplier(file_path: str | Path, watermark: Optional = None) -> pd.DataFrame:
    """Đọc dữ liệu nhà cung cấp."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Supplier file not found: {file_path}")
        return pd.DataFrame()

    try:
        if file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, dtype=str, keep_default_na=False)
        else:
            for enc in ["utf-8-sig", "utf-8", "latin-1"]:
                try:
                    df = pd.read_csv(file_path, dtype=str, encoding=enc, keep_default_na=False)
                    break
                except Exception:
                    continue
    except Exception as e:
        logger.error(f"Failed to read supplier file: {e}")
        return pd.DataFrame()

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    required = ["MaNCC", "TenNCC", "QuocGia"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    if "DieuKhoanTT_Ngay" in df.columns:
        df["DieuKhoanTT_Ngay"] = pd.to_numeric(df["DieuKhoanTT_Ngay"], errors="coerce")

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    before = len(df)
    df = df.drop_duplicates(subset=["MaNCC"], keep="first")
    logger.info(f"Supplier deduplication: {before} → {len(df)} rows")

    logger.info(f"Extracted {len(df)} suppliers from {file_path.name}")
    return df
