# ============================================================
# FILE: etl/transform/transform_sales.py
# Mô tả: Module Transform — chuẩn hóa dữ liệu, loại trùng, xử lý NULL
# ============================================================

import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def transform_sales(df: pd.DataFrame, tenant_id: str) -> pd.DataFrame:
    """
    Biến đổi và làm sạch DataFrame bán hàng của 1 tenant.

    Các bước:
    1. Chuẩn hóa kiểu dữ liệu (ngày, số, chuỗi)
    2. Làm sạch chuỗi (trim, UPPER cho mã)
    3. Xử lý NULL / giá trị thiếu
    4. Loại trùng lặp theo Business Key (MaHoaDon + MaSP)
    5. Kiểm tra ngưỡng bất thường (qty <= 0, price < 0)
    6. Tính cột phái sinh (GrossSalesAmount, NetSalesAmount)

    Args:
        df: DataFrame từ Extract
        tenant_id: Mã tenant

    Returns:
        DataFrame đã được biến đổi và làm sạch
    """
    if df.empty:
        return df

    original_count = len(df)

    # ---- 1. Chuẩn hóa kiểu dữ liệu ----
    df['NgayBan'] = pd.to_datetime(df['NgayBan'], dayfirst=True, errors='coerce')
    df['SoLuong'] = pd.to_numeric(df.get('SoLuong', 0), errors='coerce').fillna(0).astype(int)
    df['DonGiaBan'] = pd.to_numeric(df.get('DonGiaBan', 0), errors='coerce').fillna(0)
    df['ChietKhau'] = pd.to_numeric(df.get('ChietKhau', 0), errors='coerce').fillna(0)
    df['ThueVAT'] = pd.to_numeric(df.get('ThueVAT', 0), errors='coerce').fillna(0)

    # ---- 2. Làm sạch chuỗi ----
    df['MaHoaDon'] = df.get('MaHoaDon', '').astype(str).str.strip().str.upper()
    df['MaSP']     = df.get('MaSP', '').astype(str).str.strip().str.upper()
    df['MaKH']     = df.get('MaKH', '').astype(str).str.strip().str.upper().fillna('UNKNOWN')
    df['MaCH']     = df.get('MaCH', '').astype(str).str.strip().str.upper()
    df['MaNV']     = df.get('MaNV', '').astype(str).str.strip().str.upper().fillna('UNKNOWN')

    # ---- 3. Xử lý NULL / giá trị thiếu ----
    df['PhuongThucTT'] = df.get('PhuongThucTT', 'Tiền mặt').fillna('Tiền mặt')
    df['KenhBan']      = df.get('KenhBan', 'InStore').fillna('InStore')
    df['IsHoanTra']    = pd.to_numeric(df.get('IsHoanTra', 0), errors='coerce').fillna(0).astype(int)

    # Map phương thức thanh toán
    payment_map = {
        'cash': 'Tiền mặt', 'tm': 'Tiền mặt', 'tien mat': 'Tiền mặt',
        'transfer': 'Chuyển khoản', 'ck': 'Chuyển khoản', 'chuyen khoan': 'Chuyển khoản',
        'credit': 'Tín dụng',
        'ewallet': 'Ví điện tử', 'e-wallet': 'Ví điện tử',
    }
    df['PhuongThucTT'] = df['PhuongThucTT'].str.lower().str.strip().map(
        lambda x: payment_map.get(x, 'Tiền mặt')
    ).fillna('Tiền mặt')

    # Map kênh bán
    channel_map = {
        'instore': 'InStore', 'offline': 'InStore', 'cua hang': 'InStore',
        'online': 'Online', 'website': 'Online',
    }
    df['KenhBan'] = df['KenhBan'].str.lower().str.strip().map(
        lambda x: channel_map.get(x, 'InStore')
    ).fillna('InStore')

    # ---- 4. Loại trùng lặp theo Business Key ----
    before = len(df)
    if 'MaHoaDon' in df.columns and 'MaSP' in df.columns:
        df = df.drop_duplicates(subset=['MaHoaDon', 'MaSP'], keep='last')
    duplicates_dropped = before - len(df)
    if duplicates_dropped > 0:
        logger.info(f'[{tenant_id}] Dropped {duplicates_dropped} duplicate rows')

    # ---- 5. Kiểm tra ngưỡng bất thường ----
    invalid = df[
        (df['SoLuong'] <= 0) |
        (df['DonGiaBan'] < 0) |
        (df['NgayBan'].isna())
    ]
    if len(invalid) > 0:
        logger.warning(
            f'[{tenant_id}] Found {len(invalid)} invalid rows '
            f'(qty<=0, price<0, or null date) — will be excluded'
        )
        df = df[
            (df['SoLuong'] > 0) &
            (df['DonGiaBan'] >= 0) &
            (df['NgayBan'].notna())
        ]

    # ---- 6. Tính cột phái sinh ----
    df['GrossSalesAmount'] = df['SoLuong'] * df['DonGiaBan']
    df['NetSalesAmount']   = df['GrossSalesAmount'] - df['ChietKhau']

    # ---- 7. Kiểm tra null cuối cùng ----
    # Loại dòng không có MaHoaDon hoặc MaSP
    df = df[(df['MaHoaDon'] != '') & (df['MaHoaDon'] != 'NAN') & (df['MaSP'] != '') & (df['MaSP'] != 'NAN')]

    rows_kept = len(df)
    logger.info(
        f'[{tenant_id}] Transform complete: {rows_kept}/{original_count} rows kept '
        f'({original_count - rows_kept} filtered)'
    )

    return df.reset_index(drop=True)


def get_transform_stats(df: pd.DataFrame, tenant_id: str) -> dict:
    """Trả về thống kê transform để ghi vào ETLLogs."""
    return {
        'tenant_id': tenant_id,
        'total_rows': len(df),
        'total_revenue': float(df['NetSalesAmount'].sum()) if not df.empty and 'NetSalesAmount' in df.columns else 0,
        'unique_invoices': int(df['MaHoaDon'].nunique()) if not df.empty and 'MaHoaDon' in df.columns else 0,
        'unique_products': int(df['MaSP'].nunique()) if not df.empty and 'MaSP' in df.columns else 0,
    }