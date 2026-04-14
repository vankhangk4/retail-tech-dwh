# ============================================================
# FILE: etl/extract/extract_sales.py
# Mô tả: Module Extract — đọc Excel, filter theo watermark, gắn TenantID
# ============================================================

import pandas as pd
import logging
from datetime import datetime
from typing import Optional
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_last_watermark(conn, tenant_id: str, source_type: str) -> datetime:
    """Lấy mốc thời gian ETL thành công cuối cùng của tenant."""
    import pyodbc
    source_name = f'{tenant_id}_{source_type}'
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
    import pyodbc
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

        # Chuẩn hóa tên cột
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

        # Parse ngày
        if 'NgayBan' in df.columns:
            df['NgayBan'] = pd.to_datetime(df['NgayBan'], dayfirst=True, errors='coerce')

            # Incremental: chỉ lấy dòng mới hơn watermark
            before_count = len(df)
            df = df[df['NgayBan'] > pd.Timestamp(watermark)]
            logger.info(
                f'[{tenant_id}] Watermark={watermark.date()} | '
                f'Extracted {len(df)}/{before_count} rows from {file_path}'
            )
        else:
            logger.warning(f'[{tenant_id}] Column NgayBan not found in {file_path}')
            return pd.DataFrame()

        # Gắn TenantID
        df['TenantID'] = tenant_id
        df['STG_LoadDatetime'] = pd.Timestamp.now()

        # Gán giá trị mặc định
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


def load_to_staging(conn, df: pd.DataFrame, table_name: str) -> int:
    """
    Ghi DataFrame vào bảng Staging (SQL Server).

    Returns:
        Số bản ghi đã insert
    """
    import pyodbc

    if df.empty:
        logger.info(f'[STAGING] No data to load into {table_name}')
        return 0

    cursor = conn.cursor()

    # Truncate staging table trước khi load (incremental)
    cursor.execute(f'TRUNCATE TABLE {table_name}')
    conn.commit()

    # Chuẩn bị cột
    columns = list(df.columns)
    placeholders = ', '.join(['%s' for _ in columns])
    insert_sql = f'INSERT INTO {table_name} ({", ".join(columns)}) VALUES ({placeholders})'

    cursor.fast_executemany = True
    cursor.executemany(insert_sql, df.values.tolist())
    conn.commit()

    logger.info(f'[STAGING] Loaded {cursor.rowcount} rows into {table_name}')
    return cursor.rowcount
