# ============================================================
# extract/extract_customer.py
# Đọc dữ liệu khách hàng từ CSV/Excel
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaKH": "MaKH",
    "Mã KH": "MaKH",
    "CustomerID": "MaKH",
    "HoTen": "HoTen",
    "Họ Tên": "HoTen",
    "FullName": "HoTen",
    "GioiTinh": "GioiTinh",
    "Giới Tính": "GioiTinh",
    "Gender": "GioiTinh",
    "NgaySinh": "NgaySinh",
    "Ngày Sinh": "NgaySinh",
    "DOB": "NgaySinh",
    "DienThoai": "DienThoai",
    "Điện Thoại": "DienThoai",
    "Phone": "DienThoai",
    "Email": "Email",
    "ThanhPho": "ThanhPho",
    "Thành Phố": "ThanhPho",
    "City": "ThanhPho",
    "LoaiKH": "LoaiKH",
    "Loại KH": "LoaiKH",
    "CustomerType": "LoaiKH",
    "DiemTichLuy": "DiemTichLuy",
    "Điểm Tích Lũy": "DiemTichLuy",
    "LoyaltyPoints": "DiemTichLuy",
    "NgayDangKy": "NgayDangKy",
    "Ngày Đăng Ký": "NgayDangKy",
    "MemberSince": "NgayDangKy",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
    df = df.rename(columns=rename_map)
    return df


def extract_customer(file_path: str | Path, watermark: Optional = None) -> pd.DataFrame:
    """Đọc dữ liệu khách hàng từ CSV/Excel."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Customer file not found: {file_path}")
        return pd.DataFrame()

    try:
        if file_path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(file_path, dtype=str)
        else:
            for enc in ["utf-8-sig", "utf-8", "latin-1"]:
                try:
                    df = pd.read_csv(file_path, dtype=str, encoding=enc)
                    break
                except Exception:
                    continue
    except Exception as e:
        logger.error(f"Failed to read customer file: {e}")
        return pd.DataFrame()

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    required = ["MaKH", "HoTen", "NgayDangKy"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    if "NgaySinh" in df.columns:
        df["NgaySinh"] = pd.to_datetime(df["NgaySinh"], dayfirst=False, errors="coerce")
    if "NgayDangKy" in df.columns:
        df["NgayDangKy"] = pd.to_datetime(df["NgayDangKy"], dayfirst=False, errors="coerce")
    if "DiemTichLuy" in df.columns:
        df["DiemTichLuy"] = pd.to_numeric(df["DiemTichLuy"], errors="coerce").fillna(0)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    before = len(df)
    df = df.drop_duplicates(subset=["MaKH"], keep="last")
    logger.info(f"Customer deduplication: {before} → {len(df)} rows")

    logger.info(f"Extracted {len(df)} customers from {file_path.name}")
    return df
