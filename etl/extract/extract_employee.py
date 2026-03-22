# ============================================================
# extract/extract_employee.py
# Đọc dữ liệu nhân viên từ CSV/Excel
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaNV": "MaNV",
    "Mã NV": "MaNV",
    "EmployeeID": "MaNV",
    "HoTen": "HoTen",
    "Họ Tên": "HoTen",
    "FullName": "HoTen",
    "PhongBan": "PhongBan",
    "Phòng Ban": "PhongBan",
    "Department": "PhongBan",
    "ChucVu": "ChucVu",
    "Chức Vụ": "ChucVu",
    "Position": "ChucVu",
    "MaCH": "MaCH",
    "Mã CH": "MaCH",
    "StoreID": "MaCH",
    "NgayVaoLam": "NgayVaoLam",
    "Ngày Vào Làm": "NgayVaoLam",
    "HireDate": "NgayVaoLam",
}


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {}
    for col in df.columns:
        col_stripped = str(col).strip()
        if col_stripped in COLUMN_MAP:
            rename_map[col] = COLUMN_MAP[col_stripped]
    df = df.rename(columns=rename_map)
    return df


def extract_employee(file_path: str | Path, watermark: Optional = None) -> pd.DataFrame:
    """Đọc dữ liệu nhân viên."""
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Employee file not found: {file_path}")
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
        logger.error(f"Failed to read employee file: {e}")
        return pd.DataFrame()

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    required = ["MaNV", "HoTen", "PhongBan", "ChucVu", "MaCH", "NgayVaoLam"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    if "NgayVaoLam" in df.columns:
        df["NgayVaoLam"] = pd.to_datetime(df["NgayVaoLam"], dayfirst=True, errors="coerce")

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    before = len(df)
    df = df.drop_duplicates(subset=["MaNV"], keep="last")
    logger.info(f"Employee deduplication: {before} → {len(df)} rows")

    logger.info(f"Extracted {len(df)} employees from {file_path.name}")
    return df
