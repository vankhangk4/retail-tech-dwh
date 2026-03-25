# ============================================================
# extract/extract_product.py
# Đọc dữ liệu danh mục sản phẩm từ CSV
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaSP": "MaSP",
    "Mã SP": "MaSP",
    "ProductID": "MaSP",
    "TenSP": "TenSP",
    "Tên SP": "TenSP",
    "ProductName": "TenSP",
    "ThuongHieu": "ThuongHieu",
    "Thương Hiệu": "ThuongHieu",
    "Brand": "ThuongHieu",
    "DanhMuc": "DanhMuc",
    "Danh Mục": "DanhMuc",
    "Category": "DanhMuc",
    "DanhMucCon": "DanhMucCon",
    "Danh Mục Con": "DanhMucCon",
    "SubCategory": "DanhMucCon",
    "GiaVon": "GiaVon",
    "Giá Vốn": "GiaVon",
    "CostPrice": "GiaVon",
    "GiaNiemYet": "GiaNiemYet",
    "Giá Niêm Yết": "GiaNiemYet",
    "ListPrice": "GiaNiemYet",
    "DonViTinh": "DonViTinh",
    "Đơn Vị Tính": "DonViTinh",
    "Unit": "DonViTinh",
    "BaoHanh_Thang": "BaoHanh_Thang",
    "Bảo Hành (Tháng)": "BaoHanh_Thang",
    "Warranty": "BaoHanh_Thang",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
    df = df.rename(columns=rename_map)
    return df


def extract_product(file_path: str | Path, watermark: Optional = None) -> pd.DataFrame:
    """Đọc dữ liệu sản phẩm từ CSV."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Product file not found: {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(file_path, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    except Exception:
        try:
            df = pd.read_csv(file_path, dtype=str, encoding="utf-8", keep_default_na=False)
        except Exception:
            df = pd.read_csv(file_path, dtype=str, encoding="latin-1", keep_default_na=False)

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    required = ["MaSP", "TenSP", "ThuongHieu", "DanhMuc", "GiaVon", "GiaNiemYet"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    if "GiaVon" in df.columns:
        df["GiaVon"] = pd.to_numeric(df["GiaVon"], errors="coerce").fillna(0)
    if "GiaNiemYet" in df.columns:
        df["GiaNiemYet"] = pd.to_numeric(df["GiaNiemYet"], errors="coerce").fillna(0)
    if "BaoHanh_Thang" in df.columns:
        df["BaoHanh_Thang"] = pd.to_numeric(df["BaoHanh_Thang"], errors="coerce")

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    # Deduplicate by MaSP (keep last)
    before = len(df)
    df = df.drop_duplicates(subset=["MaSP"], keep="last")
    logger.info(f"Product deduplication: {before} → {len(df)} rows")

    logger.info(f"Extracted {len(df)} products from {file_path.name}")
    return df
