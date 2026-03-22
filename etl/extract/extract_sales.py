# ============================================================
# extract/extract_sales.py
# Đọc dữ liệu bán hàng từ Excel
# ============================================================
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger("etl.extract")

# Column mapping: source column → standard column
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
    """Rename columns to standard names."""
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
    return df


def extract_sales(
    file_path: str | Path,
    watermark: Optional[datetime] = None,
    sheet_name: str = "DanhSachHoaDon"
) -> pd.DataFrame:
    """
    Đọc dữ liệu bán hàng từ file Excel.

    Args:
        file_path: Đường dẫn file Excel
        watermark: Chỉ lấy bản ghi mới hơn watermark
        sheet_name: Tên sheet đọc

    Returns:
        DataFrame đã được chuẩn hóa
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.warning(f"Sales file not found: {file_path}")
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
    except Exception as e:
        # Try first sheet if specified sheet not found
        logger.warning(f"Sheet '{sheet_name}' not found, trying default: {e}")
        try:
            df = pd.read_excel(file_path, dtype=str)
        except Exception as e2:
            logger.error(f"Failed to read sales file: {e2}")
            return pd.DataFrame()

    df = rename_columns(df)
    df.columns = df.columns.str.strip()

    # Ensure required columns exist
    required = ["MaHoaDon", "MaSP", "MaCH", "NgayBan", "SoLuong", "DonGiaBan"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        logger.warning(f"Missing columns in sales file: {missing}. Available: {list(df.columns)}")
        # Return with what we have
        for c in required:
            if c not in df.columns:
                df[c] = None

    # Parse date
    if "NgayBan" in df.columns:
        df["NgayBan"] = pd.to_datetime(df["NgayBan"], dayfirst=True, errors="coerce").dt.date

    # Filter by watermark
    if watermark and "NgayBan" in df.columns:
        watermark_date = pd.Timestamp(watermark).date()
        before = len(df)
        df = df[df["NgayBan"] > watermark_date]
        logger.info(f"Watermark filter: {before} → {len(df)} rows (watermark={watermark_date})")

    # Type casting
    if "SoLuong" in df.columns:
        df["SoLuong"] = pd.to_numeric(df["SoLuong"], errors="coerce").fillna(0).astype(int)
    if "DonGiaBan" in df.columns:
        df["DonGiaBan"] = pd.to_numeric(df["DonGiaBan"], errors="coerce").fillna(0)
    if "ChietKhau" in df.columns:
        df["ChietKhau"] = pd.to_numeric(df["ChietKhau"], errors="coerce").fillna(0)
    if "ThueSuat" in df.columns:
        df["ThueSuat"] = pd.to_numeric(df["ThueSuat"], errors="coerce").fillna(0.10)

    # Trim string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip() if df[col].dtype == "object" else df[col]

    logger.info(f"Extracted {len(df)} sales records from {file_path.name}")
    return df
