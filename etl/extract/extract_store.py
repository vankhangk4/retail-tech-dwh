# ============================================================
# extract/extract_store.py
# Đọc dữ liệu cửa hàng từ CSV/Excel
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaCH": "MaCH",
    "Mã CH": "MaCH",
    "StoreID": "MaCH",
    "TenCH": "TenCH",
    "Tên CH": "TenCH",
    "StoreName": "TenCH",
    "LoaiHinh": "LoaiHinh",
    "Loại Hình": "LoaiHinh",
    "StoreType": "LoaiHinh",
    "DiaChi": "DiaChi",
    "Địa Chỉ": "DiaChi",
    "Address": "DiaChi",
    "QuanHuyen": "QuanHuyen",
    "Quận/Huyện": "QuanHuyen",
    "District": "QuanHuyen",
    "ThanhPho": "ThanhPho",
    "Thành Phố": "ThanhPho",
    "City": "ThanhPho",
    "NgayKhaiTruong": "NgayKhaiTruong",
    "Ngày Khai Trương": "NgayKhaiTruong",
    "OpenDate": "NgayKhaiTruong",
    "QuanLy": "QuanLy",
    "Quản Lý": "QuanLy",
    "ManagerName": "QuanLy",
    "DienTich_m2": "DienTich_m2",
    "Diện Tích (m2)": "DienTich_m2",
    "StoreArea": "DienTich_m2",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
    df = df.rename(columns=rename_map)
    return df


def extract_store(file_path: str | Path, watermark: Optional = None) -> pd.DataFrame:
    """Đọc dữ liệu cửa hàng."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Store file not found: {file_path}")
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
        logger.error(f"Failed to read store file: {e}")
        return pd.DataFrame()

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    required = ["MaCH", "TenCH", "LoaiHinh", "DiaChi", "ThanhPho", "NgayKhaiTruong"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    if "NgayKhaiTruong" in df.columns:
        df["NgayKhaiTruong"] = pd.to_datetime(df["NgayKhaiTruong"], dayfirst=True, errors="coerce")
    if "DienTich_m2" in df.columns:
        df["DienTich_m2"] = pd.to_numeric(df["DienTich_m2"], errors="coerce")

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    before = len(df)
    df = df.drop_duplicates(subset=["MaCH"], keep="last")
    logger.info(f"Store deduplication: {before} → {len(df)} rows")

    logger.info(f"Extracted {len(df)} stores from {file_path.name}")
    return df
