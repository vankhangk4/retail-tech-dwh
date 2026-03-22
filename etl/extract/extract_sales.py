# ============================================================
# extract/extract_sales.py
# Đọc dữ liệu bán hàng từ Excel (nhiều sheets)
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger("etl.extract")

COLUMN_MAP = {
    "MaHoaDon": "MaHoaDon",
    "Mã Hóa Đơn": "MaHoaDon",
    "InvoiceID": "MaHoaDon",
    "MaSP": "MaSP",
    "Mã SP": "MaSP",
    "ProductID": "MaSP",
    "MaKH": "MaKH",
    "Mã KH": "MaKH",
    "CustomerID": "MaKH",
    "MaCH": "MaCH",
    "Mã CH": "MaCH",
    "StoreID": "MaCH",
    "MaNV": "MaNV",
    "Mã NV": "MaNV",
    "EmployeeID": "MaNV",
    "NgayBan": "NgayBan",
    "Ngày Bán": "NgayBan",
    "SaleDate": "NgayBan",
    "SoLuong": "SoLuong",
    "Số Lượng": "SoLuong",
    "Quantity": "SoLuong",
    "DonGiaBan": "DonGiaBan",
    "Đơn Giá": "DonGiaBan",
    "UnitPrice": "DonGiaBan",
    "ChietKhau": "ChietKhau",
    "Chiết Khấu": "ChietKhau",
    "Discount": "ChietKhau",
    "ThueSuat": "ThueSuat",
    "Thuế Suất": "ThueSuat",
    "TaxRate": "ThueSuat",
    "PhuongThucTT": "PhuongThucTT",
    "Phương Thức TT": "PhuongThucTT",
    "PaymentMethod": "PhuongThucTT",
    "KenhBan": "KenhBan",
    "Kênh Bán": "KenhBan",
    "SalesChannel": "KenhBan",
    "IsHoanTra": "IsHoanTra",
    "Hoàn Trả": "IsHoanTra",
    "ReturnFlag": "IsHoanTra",
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


def extract_sales(
    file_path: str | Path,
    watermark: Optional[datetime] = None,
    sheet_name: str = None,
) -> pd.DataFrame:
    """
    Đọc dữ liệu bán hàng từ file Excel (tất cả sheets, ghép lại).
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Sales file not found: {file_path}")
        return pd.DataFrame()

    try:
        # Doc tat ca sheets
        if sheet_name:
            xl = pd.ExcelFile(file_path)
            df = pd.read_excel(xl, sheet_name=sheet_name, dtype=str)
        else:
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
        logger.error(f"Failed to read sales file: {e}")
        return pd.DataFrame()

    df = rename_columns(df)

    required = ["MaHoaDon", "MaSP", "MaCH", "NgayBan", "SoLuong", "DonGiaBan"]
    for c in required:
        if c not in df.columns:
            df[c] = None

    # Parse date - handle both string and datetime
    if "NgayBan" in df.columns:
        df["NgayBan"] = pd.to_datetime(df["NgayBan"], dayfirst=True, errors="coerce").dt.date

    if watermark and "NgayBan" in df.columns:
        watermark_date = pd.Timestamp(watermark).date()
        before = len(df)
        df = df[df["NgayBan"] > watermark_date]
        logger.info(f"Watermark filter: {before} → {len(df)} rows (watermark={watermark_date})")

    if "SoLuong" in df.columns:
        df["SoLuong"] = pd.to_numeric(df["SoLuong"], errors="coerce").fillna(0).astype(int)
    if "DonGiaBan" in df.columns:
        df["DonGiaBan"] = pd.to_numeric(df["DonGiaBan"], errors="coerce").fillna(0.0)
    if "ChietKhau" in df.columns:
        df["ChietKhau"] = pd.to_numeric(df["ChietKhau"], errors="coerce").fillna(0.0)
    if "ThueSuat" in df.columns:
        df["ThueSuat"] = pd.to_numeric(df["ThueSuat"], errors="coerce").fillna(0.10)

    # Trim string columns (chỉ những cột nào là string thật)
    for col in df.select_dtypes(include=["object"]).columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(
                lambda x: str(x).strip() if pd.notna(x) and isinstance(x, str) else x
            )

    logger.info(f"Extracted {len(df)} sales records from {file_path.name}")
    return df
