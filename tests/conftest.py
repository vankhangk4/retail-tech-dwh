"""
Shared fixtures và configuration cho toàn bộ test suite.
"""
import os
import pytest
import pandas as pd

# Set test environment variables trước khi import bất kỳ module nào
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-minimum-32-chars!!')
os.environ.setdefault('MSSQL_SERVER', 'localhost')
os.environ.setdefault('MSSQL_USER', 'sa')
os.environ.setdefault('MSSQL_PASSWORD', 'TestPass123!')
os.environ.setdefault('MSSQL_DATABASE', 'DWH_MultiTenant')
os.environ.setdefault('SUPERSET_URL', 'http://localhost:8088')


@pytest.fixture
def sample_sales_df():
    """DataFrame bán hàng mẫu dùng cho các test transform."""
    return pd.DataFrame({
        'MaHoaDon':    ['HD001', 'HD002', 'HD003'],
        'MaSP':        ['SP001', 'SP002', 'SP001'],
        'MaKH':        ['KH001', 'KH002', None],
        'MaCH':        ['CH001', 'CH001', 'CH002'],
        'MaNV':        ['NV001', 'NV001', None],
        'NgayBan':     ['01/01/2024', '15/06/2024', '20/12/2024'],
        'SoLuong':     [2, 1, 3],
        'DonGiaBan':   [1_000_000.0, 500_000.0, 200_000.0],
        'ChietKhau':   [50_000.0, 0.0, 10_000.0],
        'ThueVAT':     [100_000.0, 50_000.0, 20_000.0],
        'PhuongThucTT': ['cash', 'transfer', 'ewallet'],
        'KenhBan':     ['instore', 'online', 'offline'],
        'IsHoanTra':   [0, 0, 1],
    })


@pytest.fixture
def duplicate_sales_df():
    """DataFrame có bản ghi trùng Business Key."""
    return pd.DataFrame({
        'MaHoaDon':    ['HD001', 'HD001', 'HD002'],
        'MaSP':        ['SP001', 'SP001', 'SP002'],
        'MaKH':        ['KH001', 'KH001', 'KH002'],
        'MaCH':        ['CH001', 'CH001', 'CH001'],
        'MaNV':        ['NV001', 'NV001', 'NV002'],
        'NgayBan':     ['01/01/2024', '01/01/2024', '02/01/2024'],
        'SoLuong':     [2, 5, 1],
        'DonGiaBan':   [1_000_000.0, 1_200_000.0, 500_000.0],
        'ChietKhau':   [0.0, 0.0, 0.0],
        'ThueVAT':     [0.0, 0.0, 0.0],
        'PhuongThucTT': ['cash', 'cash', 'transfer'],
        'KenhBan':     ['instore', 'instore', 'online'],
        'IsHoanTra':   [0, 0, 0],
    })


@pytest.fixture
def invalid_rows_df():
    """DataFrame chứa các dòng không hợp lệ."""
    return pd.DataFrame({
        'MaHoaDon':    ['HD001', 'HD002', 'HD003', 'HD004'],
        'MaSP':        ['SP001', 'SP002', 'SP003', 'SP004'],
        'MaKH':        ['KH001', 'KH002', 'KH003', 'KH004'],
        'MaCH':        ['CH001', 'CH001', 'CH001', 'CH001'],
        'MaNV':        ['NV001', 'NV001', 'NV001', 'NV001'],
        'NgayBan':     ['01/01/2024', '02/01/2024', None, '04/01/2024'],
        'SoLuong':     [2, 0, 1, -1],   # HD002 qty=0, HD004 qty=-1 → invalid
        'DonGiaBan':   [1_000_000.0, 500_000.0, 200_000.0, -50_000.0],  # HD004 price<0
        'ChietKhau':   [0.0, 0.0, 0.0, 0.0],
        'ThueVAT':     [0.0, 0.0, 0.0, 0.0],
        'PhuongThucTT': ['cash', 'cash', 'cash', 'cash'],
        'KenhBan':     ['instore', 'instore', 'instore', 'instore'],
        'IsHoanTra':   [0, 0, 0, 0],
    })
