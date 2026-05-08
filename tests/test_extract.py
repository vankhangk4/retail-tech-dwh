"""
Unit tests cho etl/extract/extract_sales.py — watermark helpers và column maps.
Dùng unittest.mock để tránh kết nối DB thực.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

from etl.extract.extract_sales import (
    get_last_watermark,
    COLUMN_MAP_CUSTOMER,
    COLUMN_MAP_PRODUCT,
    COLUMN_MAP_INVENTORY,
    COLUMN_MAP_PURCHASE,
)


# ─────────────────────────────────────────────
# Column Mappings — kiểm tra tính đầy đủ
# ─────────────────────────────────────────────

class TestColumnMaps:
    def test_customer_map_ma_kh(self):
        assert 'Mã KH' in COLUMN_MAP_CUSTOMER
        assert COLUMN_MAP_CUSTOMER['Mã KH'] == 'MaKH'

    def test_customer_map_ho_ten(self):
        assert 'Họ tên' in COLUMN_MAP_CUSTOMER
        assert COLUMN_MAP_CUSTOMER['Họ tên'] == 'HoTen'

    def test_customer_map_ngay_dang_ky(self):
        assert 'Ngày đăng ký' in COLUMN_MAP_CUSTOMER
        assert COLUMN_MAP_CUSTOMER['Ngày đăng ký'] == 'NgayDangKy'

    def test_product_map_ma_sp(self):
        assert 'Mã SP' in COLUMN_MAP_PRODUCT
        assert COLUMN_MAP_PRODUCT['Mã SP'] == 'MaSP'

    def test_product_map_gia_von(self):
        assert 'Giá vốn' in COLUMN_MAP_PRODUCT
        assert COLUMN_MAP_PRODUCT['Giá vốn'] == 'GiaVon'

    def test_product_map_danh_muc(self):
        assert 'Danh mục' in COLUMN_MAP_PRODUCT
        assert COLUMN_MAP_PRODUCT['Danh mục'] == 'DanhMuc'

    def test_inventory_map_ma_sp(self):
        assert 'Mã sản phẩm' in COLUMN_MAP_INVENTORY
        assert COLUMN_MAP_INVENTORY['Mã sản phẩm'] == 'MaSP'

    def test_inventory_map_ma_cua_hang(self):
        assert 'Mã cửa hàng' in COLUMN_MAP_INVENTORY
        assert COLUMN_MAP_INVENTORY['Mã cửa hàng'] == 'MaCH'

    def test_inventory_map_ton_cuoi_ngay(self):
        assert 'Tồn cuối ngày' in COLUMN_MAP_INVENTORY
        assert COLUMN_MAP_INVENTORY['Tồn cuối ngày'] == 'TonCuoiNgay'

    def test_purchase_map_so_phieu_dat(self):
        assert 'Số phiếu đặt' in COLUMN_MAP_PURCHASE
        assert COLUMN_MAP_PURCHASE['Số phiếu đặt'] == 'SoPhieuDat'

    def test_purchase_map_ma_ncc(self):
        assert 'Mã NCC' in COLUMN_MAP_PURCHASE
        assert COLUMN_MAP_PURCHASE['Mã NCC'] == 'MaNCC'

    def test_purchase_map_don_gia_nhap(self):
        assert 'Đơn giá nhập' in COLUMN_MAP_PURCHASE
        assert COLUMN_MAP_PURCHASE['Đơn giá nhập'] == 'DonGiaNhap'


# ─────────────────────────────────────────────
# get_last_watermark — mock DB
# ─────────────────────────────────────────────

class TestGetLastWatermark:
    def _make_mock_conn(self, return_value):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (return_value,)
        return mock_conn

    def test_returns_datetime_when_no_record(self):
        conn = self._make_mock_conn(None)
        result = get_last_watermark(conn, 'STORE_HN', 'sales')
        assert isinstance(result, datetime)

    def test_returns_min_date_when_no_record(self):
        conn = self._make_mock_conn(None)
        result = get_last_watermark(conn, 'STORE_HN', 'sales')
        # Default phải là ngày cũ (không phải tương lai)
        assert result < datetime.now()

    def test_returns_existing_watermark(self):
        existing_ts = datetime(2024, 6, 15, 10, 30, 0)
        conn = self._make_mock_conn(existing_ts)
        result = get_last_watermark(conn, 'STORE_HN', 'sales')
        assert result == existing_ts

    def test_calls_cursor_with_tenant_id(self):
        conn = self._make_mock_conn(None)
        get_last_watermark(conn, 'STORE_HCM', 'inventory')
        call_args = conn.cursor().execute.call_args
        assert 'STORE_HCM' in str(call_args)

    def test_calls_cursor_with_source_type(self):
        conn = self._make_mock_conn(None)
        get_last_watermark(conn, 'STORE_HN', 'purchase')
        call_args = conn.cursor().execute.call_args
        assert 'purchase' in str(call_args)

    def test_different_tenants_independent(self):
        ts_hn  = datetime(2024, 1, 1)
        ts_hcm = datetime(2024, 6, 1)

        conn_hn  = self._make_mock_conn(ts_hn)
        conn_hcm = self._make_mock_conn(ts_hcm)

        result_hn  = get_last_watermark(conn_hn, 'STORE_HN', 'sales')
        result_hcm = get_last_watermark(conn_hcm, 'STORE_HCM', 'sales')

        assert result_hn  == ts_hn
        assert result_hcm == ts_hcm
        assert result_hn != result_hcm
