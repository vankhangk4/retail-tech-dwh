# ============================================================
# FILE: etl/extract/extract_sales.py
# Mô tả: Module Extract — đọc Excel, CSV, filter theo watermark, gắn TenantID
# ============================================================

import pandas as pd
import logging
from datetime import datetime
from typing import Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Column mappings for CSV file types
# =============================================================================
COLUMN_MAP_CUSTOMER = {
    'Mã KH': 'MaKH',
    'Họ tên': 'HoTen',
    'Giới tính': 'GioiTinh',
    'Ngày sinh': 'NgaySinh',
    'Thành phố': 'ThanhPho',
    'Tỉnh/TP': 'TinhTP',
    'Số điện thoại': 'SoDienThoai',
    'Email': 'Email',
    'Loại KH': 'LoaiKH',
    'Điểm tích lũy': 'DiemTichLuy',
    'Ngày đăng ký': 'NgayDangKy',
    'Nhóm tuổi': 'NhomTuoi',
}

COLUMN_MAP_PRODUCT = {
    'Mã SP': 'MaSP',
    'Tên SP': 'TenSP',
    'Thương hiệu': 'ThuongHieu',
    'Danh mục': 'DanhMuc',
    'Danh mục con': 'DanhMucCon',
    'Giá vốn': 'GiaVon',
    'Giá niêm yết': 'GiaNiemYet',
    'Đơn vị tính': 'DonViTinh',
    'Bảo hành (tháng)': 'BaoHanh_Thang',
}

COLUMN_MAP_PURCHASE = {
    'Số phiếu đặt': 'SoPhieuDat',
    'Mã SP': 'MaSP',
    'Mã NCC': 'MaNCC',
    'Mã cửa hàng': 'MaCH',
    'Ngày đặt': 'NgayDat',
    'Ngày nhận': 'NgayNhan',
    'Số lượng đặt': 'SoLuongDat',
    'Số lượng nhận': 'SoLuongNhan',
    'Đơn giá nhập': 'DonGiaNhap',
}

COLUMN_MAP_INVENTORY = {
    'Mã sản phẩm': 'MaSP',
    'Mã cửa hàng': 'MaCH',
    'Ngày chụp ảnh': 'NgayChupAnh',
    'Tồn đầu ngày': 'TonDauNgay',
    'Tồn cuối ngày': 'TonCuoiNgay',
    'Nhập trong ngày': 'NhapTrongNgay',
    'Bán trong ngày': 'BanTrongNgay',
    'Điều chỉnh': 'DieuChinh',
    'Đơn giá vốn': 'DonGiaVon',
}


# =============================================================================
# Watermark helpers
# =============================================================================

def get_last_watermark(conn, tenant_id: str, source_type: str) -> datetime:
    """Lấy mốc thời gian ETL thành công cuối cùng của tenant."""
    cursor = conn.cursor()
    cursor.execute(
        'SELECT MAX(LastRunTime) FROM ETL_Watermark '
        'WHERE TenantID = %s AND TableName = %s AND LastRunStatus = %s',
        (tenant_id, source_type, 'SUCCESS')
    )
    row = cursor.fetchone()
    return row[0] if row[0] else datetime(2020, 1, 1)


def update_watermark(conn, tenant_id: str, table_name: str, status: str) -> None:
    """Cập nhật watermark sau mỗi lần ETL."""
    cursor = conn.cursor()

    if status == 'RUNNING':
        cursor.execute(
            'UPDATE ETL_Watermark SET LastRunStatus = %s, UpdatedAt = GETDATE() '
            'WHERE TenantID = %s AND TableName = %s',
            (status, tenant_id, table_name)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                'INSERT INTO ETL_Watermark (TenantID, TableName, LastRunTime, LastRunStatus, UpdatedAt) '
                'VALUES (%s, %s, GETDATE(), %s, GETDATE())',
                (tenant_id, table_name, status)
            )
    elif status == 'SUCCESS':
        cursor.execute(
            'UPDATE ETL_Watermark SET LastRunTime = GETDATE(), LastRunStatus = %s, UpdatedAt = GETDATE() '
            'WHERE TenantID = %s AND TableName = %s',
            (status, tenant_id, table_name)
        )
    elif status == 'FAILED':
        cursor.execute(
            'UPDATE ETL_Watermark SET LastRunStatus = %s, UpdatedAt = GETDATE() '
            'WHERE TenantID = %s AND TableName = %s',
            (status, tenant_id, table_name)
        )
    conn.commit()
    logger.info(f'[{tenant_id}] Watermark updated: {table_name} -> {status}')


# =============================================================================
# Extract: Sales from Excel
# =============================================================================

def extract_sales_from_excel(
    file_path: str,
    watermark: datetime,
    tenant_id: str,
    sheet_name: str = 'DanhSachHoaDon'
) -> pd.DataFrame:
    """
    Đọc file Excel bán hàng, lọc theo watermark, gắn TenantID.

    Args:
        file_path: Đường dẫn file Excel (.xlsx, .xls)
        watermark: Mốc thời gian — chỉ đọc dòng mới hơn mốc này
        tenant_id: Mã tenant để gắn vào mỗi bản ghi
        sheet_name: Tên sheet trong file Excel

    Returns:
        DataFrame chứa dữ liệu đã gắn TenantID
    """
    if not os.path.exists(file_path):
        logger.warning(f'[{tenant_id}] File not found: {file_path}')
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
        df.columns = df.columns.str.strip()

        column_map = {
            'Mã hóa đơn': 'MaHoaDon',
            'MaHoaDon': 'MaHoaDon',
            'Mã sản phẩm': 'MaSP',
            'MaSP': 'MaSP',
            'Mã khách hàng': 'MaKH',
            'MaKH': 'MaKH',
            'Mã cửa hàng': 'MaCH',
            'MaCH': 'MaCH',
            'Mã nhân viên': 'MaNV',
            'MaNV': 'MaNV',
            'Ngày bán': 'NgayBan',
            'NgayBan': 'NgayBan',
            'Số lượng': 'SoLuong',
            'SL': 'SoLuong',
            'Đơn giá': 'DonGiaBan',
            'DonGiaBan': 'DonGiaBan',
            'Chiết khấu': 'ChietKhau',
            'CK': 'ChietKhau',
            'Thuế VAT': 'ThueVAT',
            'Phương thức TT': 'PhuongThucTT',
            'Kênh bán': 'KenhBan',
            'Hoàn trả': 'IsHoanTra',
        }
        df = df.rename(columns=column_map)

        if 'NgayBan' in df.columns:
            df['NgayBan'] = pd.to_datetime(df['NgayBan'], dayfirst=True, errors='coerce')
            before_count = len(df)
            df = df[df['NgayBan'] > pd.Timestamp(watermark)]
            logger.info(
                f'[{tenant_id}] Watermark={watermark.date()} | '
                f'Extracted {len(df)}/{before_count} rows from {file_path}'
            )
        else:
            logger.warning(f'[{tenant_id}] Column NgayBan not found in {file_path}')
            return pd.DataFrame()

        df['TenantID'] = tenant_id
        df['STG_LoadDatetime'] = pd.Timestamp.now()

        df['MaKH'] = df.get('MaKH', '').fillna('UNKNOWN')
        df['MaNV'] = df.get('MaNV', '').fillna('UNKNOWN')
        df['ChietKhau'] = pd.to_numeric(df.get('ChietKhau', 0), errors='coerce').fillna(0)
        df['ThueVAT'] = pd.to_numeric(df.get('ThueVAT', 0), errors='coerce').fillna(0)
        df['KenhBan'] = df.get('KenhBan', 'InStore').fillna('InStore')
        df['IsHoanTra'] = df.get('IsHoanTra', 0).fillna(0).astype(int)
        df['PhuongThucTT'] = df.get('PhuongThucTT', 'Tiền mặt').fillna('Tiền mặt')

        return df

    except Exception as e:
        logger.error(f'[{tenant_id}] Error extracting sales: {e}')
        return pd.DataFrame()


# =============================================================================
# Extract: Inventory from Excel (QuanLyKho files)
# =============================================================================

def extract_inventory_from_excel(
    file_path: str,
    tenant_id: str,
    sheet_name: str = 'QuanLyKho'
) -> pd.DataFrame:
    """
    Đọc file Excel quản lý kho (inventory), gắn TenantID.

    Args:
        file_path: Đường dẫn file Excel (.xlsx, .xls)
        tenant_id: Mã tenant để gắn vào mỗi bản ghi
        sheet_name: Tên sheet trong file Excel

    Returns:
        DataFrame chứa dữ liệu inventory đã gắn TenantID
    """
    if not os.path.exists(file_path):
        logger.warning(f'[{tenant_id}] File not found: {file_path}')
        return pd.DataFrame()

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, dtype=str)
        df.columns = df.columns.str.strip()

        # Normalize column names
        df = df.rename(columns=COLUMN_MAP_INVENTORY)

        required_cols = ['MaSP', 'MaCH', 'NgayChupAnh']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            logger.warning(
                f'[{tenant_id}] Inventory missing columns {missing} in {file_path}'
            )
            return pd.DataFrame()

        # Parse date
        df['NgayChupAnh'] = pd.to_datetime(df['NgayChupAnh'], dayfirst=True, errors='coerce')

        # Gắn TenantID
        df['TenantID'] = tenant_id
        df['STG_LoadDatetime'] = pd.Timestamp.now()

        # Numeric columns
        numeric_cols = [
            'TonDauNgay', 'TonCuoiNgay', 'NhapTrongNgay',
            'BanTrongNgay', 'DieuChinh', 'DonGiaVon',
        ]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0

        logger.info(f'[{tenant_id}] Extracted {len(df)} inventory rows from {file_path}')
        return df

    except Exception as e:
        logger.error(f'[{tenant_id}] Error extracting inventory: {e}')
        return pd.DataFrame()


# =============================================================================
# Extract: Generic CSV reader with column mapping
# =============================================================================

def extract_csv_file(
    file_path: str,
    tenant_id: str,
    file_type: str
) -> pd.DataFrame:
    """
    Đọc file CSV generic với column mapping theo loại file.

    Args:
        file_path: Đường dẫn file CSV
        tenant_id: Mã tenant để gắn vào mỗi bản ghi
        file_type: Loại file — 'customer' | 'product' | 'purchase'

    Returns:
        DataFrame đã chuẩn hóa cột, có TenantID
    """
    if not os.path.exists(file_path):
        logger.warning(f'[{tenant_id}] File not found: {file_path}')
        return pd.DataFrame()

    # Chọn column map theo loại file
    if file_type == 'customer':
        column_map = COLUMN_MAP_CUSTOMER
    elif file_type == 'product':
        column_map = COLUMN_MAP_PRODUCT
    elif file_type == 'purchase':
        column_map = COLUMN_MAP_PURCHASE
    else:
        logger.warning(f'[{tenant_id}] Unknown file_type: {file_type}')
        return pd.DataFrame()

    try:
        # Thử utf-8-sig trước (BOM), fallback utf-8
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except Exception:
            df = pd.read_csv(file_path, encoding='utf-8')

        df.columns = df.columns.str.strip()

        # Rename theo column map (chỉ rename nếu tồn tại)
        rename_dict = {orig: new for orig, new in column_map.items() if orig in df.columns}
        df = df.rename(columns=rename_dict)

        # Check required columns
        if file_type == 'customer':
            required = ['MaKH', 'HoTen']
        elif file_type == 'product':
            required = ['MaSP', 'TenSP']
        elif file_type == 'purchase':
            required = ['SoPhieuDat', 'MaSP']
        else:
            required = []

        missing = [c for c in required if c not in df.columns]
        if missing:
            logger.warning(
                f'[{tenant_id}] {file_type} CSV missing columns {missing} in {file_path}'
            )
            return pd.DataFrame()

        # Gắn TenantID (không gắn cho Product vì nó shared)
        if file_type != 'product':
            df['TenantID'] = tenant_id

        df['STG_LoadDatetime'] = pd.Timestamp.now()

        # Parse dates
        if file_type == 'customer':
            date_cols = ['NgaySinh', 'NgayDangKy']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

        elif file_type == 'purchase':
            date_cols = ['NgayDat', 'NgayNhan']
            for col in date_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')

        # Numeric for purchase
        if file_type == 'purchase':
            num_cols = ['SoLuongDat', 'SoLuongNhan', 'DonGiaNhap']
            for col in num_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Numeric for product
        if file_type == 'product':
            num_cols = ['GiaVon', 'GiaNiemYet']
            for col in num_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        logger.info(f'[{tenant_id}] Extracted {len(df)} {file_type} rows from {file_path}')
        return df

    except Exception as e:
        logger.error(f'[{tenant_id}] Error extracting CSV {file_type}: {e}')
        return pd.DataFrame()


# =============================================================================
# Load to Staging (APPEND mode — no TRUNCATE)
# =============================================================================

def load_to_staging(conn, df: pd.DataFrame, table_name: str) -> int:
    """
    Ghi DataFrame vào bảng Staging (SQL Server) — APPEND mode.

    Multi-file loads append on top of each other; truncate should be
    handled at the caller level if needed (e.g. per-tenant per-run).

    Returns:
        Số bản ghi đã insert
    """
    if df.empty:
        logger.info(f'[STAGING] No data to load into {table_name}')
        return 0

    cursor = conn.cursor()
    columns = list(df.columns)
    placeholders = ', '.join(['%s' for _ in columns])
    insert_sql = (
        f'INSERT INTO {table_name} ({", ".join(columns)}) '
        f'VALUES ({placeholders})'
    )

    # Replace NaN/NaT with None so pymssql passes them as SQL NULL
    df = df.copy()
    df = df.where(pd.notna(df), None)

    cursor.executemany(insert_sql, df.values.tolist())
    conn.commit()

    rows = cursor.rowcount
    logger.info(f'[STAGING] APPEND {rows} rows into {table_name}')
    return rows
