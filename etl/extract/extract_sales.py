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
    'Mã NCC': 'MaNCC',
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
    'Đã thanh toán': 'DaThanhToan',
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
        'SELECT MAX(LastProcessedAt) FROM ETL_Watermark '
        'WHERE TenantID = %s AND TableName = %s',
        (tenant_id, source_type)
    )
    row = cursor.fetchone()
    return row[0] if row[0] else datetime(2020, 1, 1)


def update_watermark(conn, tenant_id: str, table_name: str, status: str, commit: bool = True) -> None:
    """Cập nhật watermark sau mỗi lần ETL."""
    cursor = conn.cursor()

    if status == 'SUCCESS':
        cursor.execute(
            'UPDATE ETL_Watermark SET LastProcessedAt = GETDATE() '
            'WHERE TenantID = %s AND TableName = %s',
            (tenant_id, table_name)
        )
        if cursor.rowcount == 0:
            cursor.execute(
                'INSERT INTO ETL_Watermark (TenantID, TableName, LastProcessedAt) '
                'VALUES (%s, %s, GETDATE())',
                (tenant_id, table_name)
            )
    if commit:
        conn.commit()
    logger.info(f'[{tenant_id}] Watermark updated: {table_name} -> {status}')


# =============================================================================
# Extract: Sales from Excel
# =============================================================================

def extract_sales_from_excel(
    file_path: str,
    watermark: Optional[datetime],
    tenant_id: str,
    sheet_name: str = 'DanhSachHoaDon'
) -> pd.DataFrame:
    """
    Đọc file Excel bán hàng, lọc theo watermark, gắn TenantID.
    Output columns match STG_SalesRaw schema.

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

        # Map file columns -> STG_SalesRaw columns
        column_map = {
            'Mã hóa đơn': 'InvoiceNumber',
            'MaHoaDon': 'InvoiceNumber',
            'Ngày bán': 'SaleDate',
            'NgayBan': 'SaleDate',
            'Mã sản phẩm': 'ProductID',
            'MaSP': 'ProductID',
            'Mã khách hàng': 'CustomerName',
            'MaKH': 'CustomerName',
            'Mã cửa hàng': 'StoreName',
            'MaCH': 'StoreName',
            'Mã nhân viên': 'EmployeeName',
            'MaNV': 'EmployeeName',
            'Số lượng': 'Quantity',
            'SL': 'Quantity',
            'Đơn giá': 'UnitPrice',
            'DonGiaBan': 'UnitPrice',
            'Chiết khấu': 'Discount',
            'CK': 'Discount',
            'Thuế VAT': 'Tax',
            'Phương thức TT': 'PaymentMethod',
            'PhuongThucTT': 'PaymentMethod',
            'Kênh bán': 'SalesChannel',
            'Hoàn trả': 'IsReturn',
        }
        df = df.rename(columns=column_map)

        # Find date column — after rename it becomes 'SaleDate'
        date_col = None
        for col in ['SaleDate']:
            if col in df.columns:
                date_col = col
                break

        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], dayfirst=True, errors='coerce')
            before_count = len(df)
            if watermark is not None:
                df = df[df[date_col] > pd.Timestamp(watermark)]
                logger.info(
                    f'[{tenant_id}] Watermark={watermark.date()} | '
                    f'Extracted {len(df)}/{before_count} rows from {file_path}'
                )
            else:
                logger.info(f'[{tenant_id}] Full extract {before_count} rows from {file_path}')
        else:
            logger.warning(f'[{tenant_id}] No date column found in {file_path}')
            return pd.DataFrame()

        # Build STG_SalesRaw output
        # ACTUAL DB schema: TenantID, SaleDate, ProductID, CustomerName, StoreName,
        # EmployeeName, PaymentMethod, Quantity, UnitPrice, Discount, Revenue,
        # LoadStatus, ErrorMessage, CreatedAt
        _empty_str = pd.Series([''] * len(df), index=df.index)
        _zero_num  = pd.to_numeric(_empty_str, errors='coerce').fillna(0)

        qty   = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0) if 'Quantity' in df.columns else _zero_num
        price = pd.to_numeric(df['UnitPrice'], errors='coerce').fillna(0) if 'UnitPrice' in df.columns else _zero_num
        disc  = pd.to_numeric(df['Discount'], errors='coerce').fillna(0) if 'Discount' in df.columns else _zero_num

        out = pd.DataFrame()
        out['TenantID']       = [tenant_id] * len(df)
        out['InvoiceNumber']  = df['InvoiceNumber'].fillna('').astype(str).str.strip().str.upper() if 'InvoiceNumber' in df.columns else _empty_str
        out['SaleDate']        = df['SaleDate'].astype(str) if 'SaleDate' in df.columns else _empty_str
        out['ProductID']       = df['ProductID'].fillna('').astype(str).str.strip().str.upper() if 'ProductID' in df.columns else _empty_str
        out['CustomerName']   = df['CustomerName'].fillna('').astype(str).str.strip() if 'CustomerName' in df.columns else _empty_str
        # Ignore store code embedded in the source file; tenant upload context is authoritative.
        out['StoreName']      = pd.Series([tenant_id] * len(df), index=df.index)
        out['EmployeeName']   = df['EmployeeName'].fillna('').astype(str).str.strip() if 'EmployeeName' in df.columns else _empty_str
        out['PaymentMethod']  = df['PaymentMethod'].fillna('Tiền mặt').astype(str).str.strip() if 'PaymentMethod' in df.columns else pd.Series(['Tiền mặt'] * len(df))
        out['Quantity']        = qty
        out['UnitPrice']       = price
        out['Discount']        = disc
        out['Revenue']         = qty * price - disc
        out['LoadStatus']      = 'LOADED'
        out['ErrorMessage']    = None
        out['CreatedAt']       = pd.Timestamp.now()

        # Select only columns that exist in ACTUAL STG_SalesRaw DB schema
        stg_sales_cols = [
            'TenantID', 'InvoiceNumber', 'SaleDate', 'ProductID', 'CustomerName',
            'StoreName', 'EmployeeName', 'PaymentMethod', 'Quantity',
            'UnitPrice', 'Discount', 'Revenue', 'LoadStatus',
            'ErrorMessage', 'CreatedAt'
        ]
        out = out[[c for c in stg_sales_cols if c in out.columns]]

        return out

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

        required_cols = ['MaSP', 'NgayChupAnh']
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            logger.warning(
                f'[{tenant_id}] Inventory missing columns {missing} in {file_path}'
            )
            return pd.DataFrame()

        # Parse date
        df['NgayChupAnh'] = pd.to_datetime(df['NgayChupAnh'], dayfirst=True, errors='coerce')

        # Build STG_InventoryRaw output
        # Column selection must match STG_InventoryRaw schema exactly
        _empty_str = pd.Series([''] * len(df), index=df.index)

        out = pd.DataFrame()
        out['ID']             = ''  # auto-increment; not inserted
        out['TenantID']       = [tenant_id] * len(df)
        out['CheckDate']      = df['NgayChupAnh'].astype(str)
        out['ProductID']      = df['MaSP'].fillna('').astype(str).str.strip().str.upper() if 'MaSP' in df.columns else _empty_str
        # Ignore store code embedded in the source file; tenant upload context is authoritative.
        out['StoreName']      = pd.Series([tenant_id] * len(df), index=df.index)
        out['QuantityOnHand'] = pd.to_numeric(df['TonCuoiNgay'], errors='coerce').fillna(0) if 'TonCuoiNgay' in df.columns else pd.Series([0] * len(df))
        out['LoadStatus']     = 'LOADED'
        out['ErrorMessage']   = None
        out['CreatedAt']      = pd.Timestamp.now()

        # Select only columns that exist in STG_InventoryRaw
        stg_inv_cols = [
            'ID', 'TenantID', 'CheckDate', 'ProductID', 'StoreName',
            'QuantityOnHand', 'LoadStatus', 'ErrorMessage', 'CreatedAt'
        ]
        out = out[[c for c in stg_inv_cols if c in out.columns]]

        logger.info(f'[{tenant_id}] Extracted {len(out)} inventory rows from {file_path}')
        return out

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

        # Build STG table output per file_type
        # All outputs must match their STG_* schema exactly.
        # Use df[col] instead of df.get(col, '') to avoid scalar-string .fillna() bug.
        _empty_str = pd.Series([''] * len(df), index=df.index)
        _zero_num  = pd.to_numeric(_empty_str, errors='coerce').fillna(0)

        if file_type == 'customer':
            out = pd.DataFrame()
            out['ID']             = ''  # auto-increment; not inserted
            out['CustomerID']     = df['MaKH'].fillna('').astype(str).str.strip().str.upper() if 'MaKH' in df.columns else _empty_str
            out['CustomerName']   = df['HoTen'].fillna('').astype(str).str.strip() if 'HoTen' in df.columns else _empty_str
            out['Phone']          = df['SoDienThoai'].fillna('').astype(str).str.strip() if 'SoDienThoai' in df.columns else _empty_str
            out['Email']          = df['Email'].fillna('').astype(str).str.strip() if 'Email' in df.columns else _empty_str
            out['City']           = df['ThanhPho'].fillna('').astype(str).str.strip() if 'ThanhPho' in df.columns else _empty_str
            out['Region']         = df['TinhTP'].fillna('').astype(str).str.strip() if 'TinhTP' in df.columns else _empty_str
            out['CustomerType']  = df['LoaiKH'].fillna('').astype(str).str.strip() if 'LoaiKH' in df.columns else _empty_str
            out['LoadStatus']     = 'LOADED'
            out['ErrorMessage']   = None
            out['CreatedAt']      = pd.Timestamp.now()
            out['TenantID']       = [tenant_id] * len(df)
            # Select only columns that exist in STG_CustomerRaw
            stg_cust_cols = [
                'ID', 'CustomerID', 'CustomerName', 'Phone', 'Email',
                'City', 'Region', 'CustomerType', 'LoadStatus', 'ErrorMessage',
                'CreatedAt', 'TenantID'
            ]
            out = out[[c for c in stg_cust_cols if c in out.columns]]

        elif file_type == 'product':
            out = pd.DataFrame()
            out['ID']             = ''  # auto-increment; not inserted
            out['ProductID']      = df['MaSP'].fillna('').astype(str).str.strip().str.upper() if 'MaSP' in df.columns else _empty_str
            out['ProductName']    = df['TenSP'].fillna('').astype(str).str.strip() if 'TenSP' in df.columns else _empty_str
            out['Category']       = df['DanhMuc'].fillna('').astype(str).str.strip() if 'DanhMuc' in df.columns else _empty_str
            out['SubCategory']    = df['DanhMucCon'].fillna('').astype(str).str.strip() if 'DanhMucCon' in df.columns else _empty_str
            out['UnitPrice']      = pd.to_numeric(df['GiaNiemYet'], errors='coerce').fillna(0) if 'GiaNiemYet' in df.columns else _zero_num
            out['UnitCost']       = pd.to_numeric(df['GiaVon'], errors='coerce').fillna(0) if 'GiaVon' in df.columns else _zero_num
            out['SupplierID']     = df['MaNCC'].fillna('').astype(str).str.strip().str.upper() if 'MaNCC' in df.columns else _empty_str
            out['LoadStatus']     = 'LOADED'
            out['ErrorMessage']   = None
            out['CreatedAt']      = pd.Timestamp.now()
            out['TenantID']       = [tenant_id] * len(df)
            # Select only columns that exist in STG_ProductRaw
            stg_prod_cols = [
                'ID', 'ProductID', 'ProductName', 'Category', 'SubCategory',
                'UnitPrice', 'UnitCost', 'SupplierID', 'LoadStatus', 'ErrorMessage',
                'CreatedAt', 'TenantID'
            ]
            out = out[[c for c in stg_prod_cols if c in out.columns]]

        elif file_type == 'purchase':
            ngay_dat = pd.to_datetime(df['NgayDat'], dayfirst=True, errors='coerce') if 'NgayDat' in df.columns else pd.to_datetime(_empty_str, errors='coerce')
            so_luong = pd.to_numeric(df['SoLuongNhan'], errors='coerce').fillna(0) if 'SoLuongNhan' in df.columns else _zero_num
            don_gia  = pd.to_numeric(df['DonGiaNhap'], errors='coerce').fillna(0)  if 'DonGiaNhap' in df.columns else _zero_num
            out = pd.DataFrame()
            out['ID']           = ''  # auto-increment; not inserted
            out['TenantID']     = [tenant_id] * len(df)
            out['PurchaseDate'] = ngay_dat.astype(str)
            out['ProductID']    = df['MaSP'].fillna('').astype(str).str.strip().str.upper() if 'MaSP' in df.columns else _empty_str
            out['SupplierID']   = df['MaNCC'].fillna('').astype(str).str.strip().str.upper() if 'MaNCC' in df.columns else _empty_str
            out['Quantity']     = so_luong
            out['UnitCost']     = don_gia
            out['TotalCost']    = so_luong * don_gia
            out['IsPaid']       = df['DaThanhToan'].fillna('0').astype(str) if 'DaThanhToan' in df.columns else pd.Series(['0'] * len(df))
            out['LoadStatus']   = 'LOADED'
            out['ErrorMessage'] = None
            out['CreatedAt']     = pd.Timestamp.now()
            # Select only columns that exist in STG_PurchaseRaw
            stg_purch_cols = [
                'ID', 'TenantID', 'PurchaseDate', 'ProductID', 'SupplierID',
                'Quantity', 'UnitCost', 'TotalCost', 'IsPaid',
                'LoadStatus', 'ErrorMessage', 'CreatedAt'
            ]
            out = out[[c for c in stg_purch_cols if c in out.columns]]

        logger.info(f'[{tenant_id}] Extracted {len(out)} {file_type} rows from {file_path}')
        return out

    except Exception as e:
        logger.error(f'[{tenant_id}] Error extracting CSV {file_type}: {e}')
        return pd.DataFrame()


# =============================================================================
# Load to Staging (APPEND mode — no TRUNCATE)
# =============================================================================

def load_to_staging(conn, df: pd.DataFrame, table_name: str,
                    columns: list = None, commit: bool = True) -> int:
    """
    Ghi DataFrame vào bảng Staging (SQL Server) — APPEND mode.

    Args:
        conn: Database connection
        df: DataFrame to insert; must not include the auto-increment ID column
        table_name: Target staging table name
        columns: Optional explicit list of column names to INSERT.
                 If provided, only these columns are selected from df before insert.
                 This prevents the auto-increment ID column from being included.

    Multi-file loads append on top of each other; truncate should be
    handled at the caller level if needed (e.g. per-tenant per-run).

    Returns:
        Số bản ghi đã insert
    """
    if df.empty:
        logger.info(f'[STAGING] No data to load into {table_name}')
        return 0

    cursor = conn.cursor()

    # Respect explicit column list if provided (prevents ID auto-increment col from leaking in)
    if columns is not None:
        insert_cols = [c for c in columns if c in df.columns]
    else:
        insert_cols = [c for c in df.columns]

    placeholders = ', '.join(['%s' for _ in insert_cols])
    insert_sql = (
        f'INSERT INTO {table_name} ({", ".join(insert_cols)}) '
        f'VALUES ({placeholders})'
    )

    # Replace NaN/NaT with None so pymssql passes them as SQL NULL
    df = df.copy()
    df = df.where(pd.notna(df), None)

    cursor.executemany(insert_sql, df[insert_cols].values.tolist())
    if commit:
        conn.commit()

    rows = cursor.rowcount
    logger.info(f'[STAGING] APPEND {rows} rows into {table_name}')
    return rows
