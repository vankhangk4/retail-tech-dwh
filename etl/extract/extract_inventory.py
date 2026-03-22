# ============================================================
# extract/extract_inventory.py
# Đọc dữ liệu tồn kho từ Excel (nhiều sheets)
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
        elif col_stripped.lower() in [k.lower() for k in COLUMN_MAP]:
            for k, v in COLUMN_MAP.items():
                if k.lower() == col_stripped.lower():
                    rename_map[col] = v
                    break
    df = df.rename(columns=rename_map)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def extract_inventory(
    file_path: str | Path,
    watermark: Optional[datetime] = None,
    sheet_name: str = None,
) -> pd.DataFrame:
    """Đọc dữ liệu tồn kho từ file Excel (tất cả sheets)."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Inventory file not found: {file_path}")
        return pd.DataFrame()

    try:
        xl = pd.ExcelFile(file_path)
        all_dfs = []
        for sname in xl.sheet_names:
            try:
                sub = pd.read_excel(xl, sheet_name=sname, dtype=str)
                all_dfs.append(sub)
                logger.info(f"  Read sheet '{sname}': {len(sub)} rows")
            except Exception as e:
                logger.warning(f"  Failed to read sheet '{sname}': {e}")
        if not all_dfs:
            logger.error(f"No sheets could be read from {file_path}")
            return pd.DataFrame()
        df = pd.concat(all_dfs, ignore_index=True)
    except Exception as e:
        logger.error(f"Failed to read inventory file: {e}")
        return pd.DataFrame()

    df = rename_columns(df)

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
        if df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: str(x).strip() if pd.notna(x) and isinstance(x, str) else x
            )

    logger.info(f"Extracted {len(df)} inventory records from {file_path.name}")
    return df
