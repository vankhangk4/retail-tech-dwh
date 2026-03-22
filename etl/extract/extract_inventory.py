# ============================================================
# extract/extract_inventory.py
# Đọc dữ liệu tồn kho từ Excel
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaPhieu": "MaPhieu",
    "Mã Phiếu": "MaPhieu",
    "MaSP": "MaSP",
    "Mã SP": "MaSP",
    "MaCH": "MaCH",
    "Mã CH": "MaCH",
    "MaNCC": "MaNCC",
    "Mã NCC": "MaNCC",
    "NgayChot": "NgayChot",
    "Ngày Chốt": "NgayChot",
    "TonDauNgay": "TonDauNgay",
    "Tồn Đầu Ngày": "TonDauNgay",
    "OpeningStock": "TonDauNgay",
    "TonCuoiNgay": "TonCuoiNgay",
    "Tồn Cuối Ngày": "TonCuoiNgay",
    "ClosingStock": "TonCuoiNgay",
    "NhapTrongNgay": "NhapTrongNgay",
    "Nhập Trong Ngày": "NhapTrongNgay",
    "StockReceived": "NhapTrongNgay",
    "XuatTrongNgay": "XuatTrongNgay",
    "Xuất Trong Ngày": "XuatTrongNgay",
    "StockSold": "XuatTrongNgay",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
    df = df.rename(columns=rename_map)
    return df


def extract_inventory(
    file_path: str | Path,
    watermark: Optional[datetime] = None,
    sheet_name: str = "QuanLyKho"
) -> pd.DataFrame:
    """Đọc dữ liệu tồn kho từ file Excel."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Inventory file not found: {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
    except Exception as e:
        logger.warning(f"Sheet '{sheet_name}' not found: {e}")
        try:
            df = pd.read_excel(file_path, dtype=str)
        except Exception as e2:
            logger.error(f"Failed to read inventory file: {e2}")
            return pd.DataFrame()

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    required = ["MaPhieu", "MaSP", "MaCH", "NgayChot", "TonCuoiNgay"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    if "NgayChot" in df.columns:
        df["NgayChot"] = pd.to_datetime(df["NgayChot"], dayfirst=True, errors="coerce").dt.date

    if watermark and "NgayChot" in df.columns:
        watermark_date = pd.Timestamp(watermark).date()
        df = df[df["NgayChot"] > watermark_date]

    numeric_cols = ["TonDauNgay", "TonCuoiNgay", "NhapTrongNgay", "XuatTrongNgay"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    logger.info(f"Extracted {len(df)} inventory records from {file_path.name}")
    return df
