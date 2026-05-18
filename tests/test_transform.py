"""
Unit tests cho etl/transform/transform_sales.py.
Không cần DB — chỉ test logic pandas thuần.
"""
import pytest
import pandas as pd

from etl.transform.transform_sales import transform_sales, transform_staging_sales, get_transform_stats


# ─────────────────────────────────────────────
# Edge cases — DataFrame rỗng / thiếu cột
# ─────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_df_returns_empty(self):
        result = transform_sales(pd.DataFrame(), 'STORE_HN')
        assert result.empty

    def test_returns_dataframe_type(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert isinstance(result, pd.DataFrame)

    def test_index_is_reset(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert list(result.index) == list(range(len(result)))


# ─────────────────────────────────────────────
# Kiểu dữ liệu
# ─────────────────────────────────────────────

class TestDataTypes:
    def test_ngay_ban_parsed_to_datetime(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert pd.api.types.is_datetime64_any_dtype(result['NgayBan'])

    def test_so_luong_is_integer(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert result['SoLuong'].dtype in ('int32', 'int64')

    def test_don_gia_ban_is_numeric(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert pd.api.types.is_numeric_dtype(result['DonGiaBan'])

    def test_chiet_khau_is_numeric(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert pd.api.types.is_numeric_dtype(result['ChietKhau'])


# ─────────────────────────────────────────────
# Chuẩn hóa chuỗi
# ─────────────────────────────────────────────

class TestStringNormalization:
    def test_ma_hoa_don_uppercase(self, sample_sales_df):
        sample_sales_df['MaHoaDon'] = ['hd001', 'hd002', 'hd003']
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert all(v == v.upper() for v in result['MaHoaDon'])

    def test_ma_sp_uppercase(self, sample_sales_df):
        sample_sales_df['MaSP'] = ['sp001', 'sp002', 'sp001']
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert all(v == v.upper() for v in result['MaSP'])

    def test_ma_hoa_don_stripped(self, sample_sales_df):
        sample_sales_df['MaHoaDon'] = ['  HD001  ', '  HD002  ', '  HD003  ']
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert all(v == v.strip() for v in result['MaHoaDon'])

    def test_null_ma_kh_filled_with_unknown(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        # Row 2 had MaKH=None — should be UNKNOWN
        assert result['MaKH'].notna().all()


# ─────────────────────────────────────────────
# Loại trùng lặp (Business Key = MaHoaDon + MaSP)
# ─────────────────────────────────────────────

class TestDeduplication:
    def test_duplicates_removed(self, duplicate_sales_df):
        result = transform_sales(duplicate_sales_df, 'STORE_HN')
        # HD001+SP001 xuất hiện 2 lần → chỉ còn 1
        key_mask = (result['MaHoaDon'] == 'HD001') & (result['MaSP'] == 'SP001')
        assert key_mask.sum() == 1

    def test_total_rows_after_dedup(self, duplicate_sales_df):
        result = transform_sales(duplicate_sales_df, 'STORE_HN')
        # 3 rows ban đầu (2 trùng + 1 khác) → 2 rows sau dedup
        assert len(result) == 2

    def test_keep_last_on_duplicate(self, duplicate_sales_df):
        result = transform_sales(duplicate_sales_df, 'STORE_HN')
        hd001_row = result[result['MaHoaDon'] == 'HD001'].iloc[0]
        # keep='last' → giữ dòng thứ 2 (SoLuong=5, DonGiaBan=1_200_000)
        assert hd001_row['SoLuong'] == 5


# ─────────────────────────────────────────────
# Lọc dòng không hợp lệ
# ─────────────────────────────────────────────

class TestInvalidRowsFiltering:
    def test_zero_quantity_filtered(self, invalid_rows_df):
        result = transform_sales(invalid_rows_df, 'STORE_HN')
        assert (result['SoLuong'] > 0).all()

    def test_negative_quantity_filtered(self, invalid_rows_df):
        result = transform_sales(invalid_rows_df, 'STORE_HN')
        assert (result['SoLuong'] > 0).all()

    def test_negative_price_filtered(self, invalid_rows_df):
        result = transform_sales(invalid_rows_df, 'STORE_HN')
        assert (result['DonGiaBan'] >= 0).all()

    def test_null_date_filtered(self, invalid_rows_df):
        result = transform_sales(invalid_rows_df, 'STORE_HN')
        assert result['NgayBan'].isna().sum() == 0

    def test_only_valid_rows_remain(self, invalid_rows_df):
        # invalid_rows_df: HD001 hợp lệ, HD002 qty=0, HD003 date=None, HD004 qty<0 & price<0
        result = transform_sales(invalid_rows_df, 'STORE_HN')
        assert list(result['MaHoaDon']) == ['HD001']


# ─────────────────────────────────────────────
# Mapping phương thức thanh toán
# ─────────────────────────────────────────────

class TestPaymentMapping:
    def test_cash_mapped(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'Tiền mặt' in result['PhuongThucTT'].values

    def test_transfer_mapped(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'Chuyển khoản' in result['PhuongThucTT'].values

    def test_ewallet_mapped(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'Ví điện tử' in result['PhuongThucTT'].values

    def test_unknown_payment_defaults_to_tien_mat(self):
        df = pd.DataFrame({
            'MaHoaDon': ['HD001'], 'MaSP': ['SP001'], 'MaKH': ['KH001'],
            'MaCH': ['CH001'], 'MaNV': ['NV001'], 'NgayBan': ['01/01/2024'],
            'SoLuong': [1], 'DonGiaBan': [100_000.0], 'ChietKhau': [0.0],
            'ThueVAT': [0.0], 'PhuongThucTT': ['unknown_method'],
            'KenhBan': ['instore'], 'IsHoanTra': [0],
        })
        result = transform_sales(df, 'STORE_HN')
        assert result['PhuongThucTT'].iloc[0] == 'Tiền mặt'


# ─────────────────────────────────────────────
# Mapping kênh bán
# ─────────────────────────────────────────────

class TestChannelMapping:
    def test_instore_mapped(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'InStore' in result['KenhBan'].values

    def test_online_mapped(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'Online' in result['KenhBan'].values

    def test_offline_maps_to_instore(self, sample_sales_df):
        # 'offline' → 'InStore'
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'InStore' in result['KenhBan'].values


# ─────────────────────────────────────────────
# Cột phái sinh
# ─────────────────────────────────────────────

class TestDerivedColumns:
    def test_gross_sales_amount_created(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'GrossSalesAmount' in result.columns

    def test_net_sales_amount_created(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        assert 'NetSalesAmount' in result.columns

    def test_gross_sales_formula(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        for _, row in result.iterrows():
            expected = row['SoLuong'] * row['DonGiaBan']
            assert abs(row['GrossSalesAmount'] - expected) < 0.01

    def test_net_sales_formula(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        for _, row in result.iterrows():
            expected = row['GrossSalesAmount'] - row['ChietKhau']
            assert abs(row['NetSalesAmount'] - expected) < 0.01

    def test_net_sales_less_than_gross(self, sample_sales_df):
        result = transform_sales(sample_sales_df, 'STORE_HN')
        # Với dòng có ChietKhau > 0, NetSales < GrossSales
        rows_with_discount = result[result['ChietKhau'] > 0]
        assert (rows_with_discount['NetSalesAmount'] < rows_with_discount['GrossSalesAmount']).all()


class TestStagingSalesTransform:
    def test_filters_invalid_and_deduplicates_staging_rows(self):
        df = pd.DataFrame({
            'TenantID': ['STORE_HN', 'STORE_HN', 'STORE_HN'],
            'InvoiceNumber': ['hd001', 'HD001', ''],
            'SaleDate': ['01/01/2024', '01/01/2024', '01/01/2024'],
            'ProductID': ['sp001', 'SP001', 'SP002'],
            'CustomerName': ['kh001', 'kh001', 'kh002'],
            'StoreName': ['wrong', 'wrong', 'wrong'],
            'EmployeeName': ['nv001', 'nv001', 'nv002'],
            'PaymentMethod': ['cash', 'transfer', 'cash'],
            'Quantity': [1, 2, 1],
            'UnitPrice': [100000, 120000, 50000],
            'Discount': [0, 10000, 0],
            'Revenue': [100000, 230000, 50000],
        })

        result = transform_staging_sales(df, 'STORE_HN')

        assert len(result) == 1
        assert result['InvoiceNumber'].iloc[0] == 'HD001'
        assert result['ProductID'].iloc[0] == 'SP001'
        assert result['StoreName'].iloc[0] == 'STORE_HN'
        assert result['PaymentMethod'].iloc[0] == 'Chuyển khoản'
        assert result['Revenue'].iloc[0] == 230000


# ─────────────────────────────────────────────
# get_transform_stats
# ─────────────────────────────────────────────

class TestGetTransformStats:
    def test_returns_dict(self, sample_sales_df):
        df = transform_sales(sample_sales_df, 'STORE_HN')
        stats = get_transform_stats(df, 'STORE_HN')
        assert isinstance(stats, dict)

    def test_required_keys(self, sample_sales_df):
        df = transform_sales(sample_sales_df, 'STORE_HN')
        stats = get_transform_stats(df, 'STORE_HN')
        for key in ('tenant_id', 'total_rows', 'total_revenue', 'unique_invoices', 'unique_products'):
            assert key in stats

    def test_tenant_id_correct(self, sample_sales_df):
        df = transform_sales(sample_sales_df, 'STORE_HN')
        stats = get_transform_stats(df, 'STORE_HN')
        assert stats['tenant_id'] == 'STORE_HN'

    def test_total_rows_correct(self, sample_sales_df):
        df = transform_sales(sample_sales_df, 'STORE_HN')
        stats = get_transform_stats(df, 'STORE_HN')
        assert stats['total_rows'] == len(df)

    def test_total_revenue_positive(self, sample_sales_df):
        df = transform_sales(sample_sales_df, 'STORE_HN')
        stats = get_transform_stats(df, 'STORE_HN')
        assert stats['total_revenue'] > 0

    def test_empty_df_returns_zeros(self):
        stats = get_transform_stats(pd.DataFrame(), 'STORE_HN')
        assert stats['total_rows'] == 0
        assert stats['total_revenue'] == 0
        assert stats['unique_invoices'] == 0
        assert stats['unique_products'] == 0
