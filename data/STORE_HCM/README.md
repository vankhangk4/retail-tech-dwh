# ============================================================
# FILE: data/STORE_HCM/README.md
# Mô tả: Hướng dẫn cấu trúc file dữ liệu cho STORE_HCM
# ============================================================

# Thư mục này chứa file Excel/CSV nguồn của Cửa hàng Hồ Chí Minh (STORE_HCM)
# ETL sẽ tự động đọc file trong thư mục này mỗi đêm lúc 02:00 SA

# ============================================================
# 1. Cấu trúc file bắt buộc
# ============================================================

# File báo cáo bán hàng: BaoCaoDoanhThu_HCM_YYYYMMDD.xlsx
#   - Sheet: "DanhSachHoaDon"
#   - Các cột bắt buộc:
#       Mã hóa đơn | Mã sản phẩm | Mã khách hàng | Mã cửa hàng | Mã nhân viên
#       Ngày bán | Số lượng | Đơn giá | Chiết khấu | Thuế VAT
#       Phương thức TT | Kênh bán | Hoàn trả
#
# File quản lý tồn kho: QuanLyKho_HCM_YYYYMMDD.xlsx
#   - Các cột:
#       Mã sản phẩm | Mã cửa hàng | Ngày chụp ảnh
#       Tồn đầu ngày | Tồn cuối ngày | Nhập trong ngày
#       Bán trong ngày | Điều chỉnh | Đơn giá vốn
#
# File danh mục sản phẩm: DanhMucSanPham.csv
#   - Các cột:
#       Mã SP | Tên SP | Thương hiệu | Danh mục | Danh mục con
#       Giá vốn | Giá niêm yết | Đơn vị tính | Bảo hành (tháng)

# ============================================================
# 2. Ví dụ dữ liệu BaoCaoDoanhThu_HCM_20260101.xlsx
# ============================================================

# Sheet: "DanhSachHoaDon"
# | Mã hóa đơn | Mã sản phẩm | Mã khách hàng | Mã cửa hàng | Mã nhân viên | Ngày bán    | Số lượng | Đơn giá   | Chiết khấu | Thuế VAT | Phương thức TT | Kênh bán | Hoàn trả |
# |------------|-------------|--------------|------------|-------------|------------|----------|-----------|------------|----------|---------------|----------|----------|
# | HD_HCM_0001| SP001       | KH001        | STORE_HCM  | NV001       | 01/01/2026 | 3        | 25000000  | 0         | 0        | Tiền mặt     | InStore  | 0        |
# | HD_HCM_0002| SP003       | KH003        | STORE_HCM  | NV002       | 01/01/2026 | 1        | 45000000  | 4500000   | 0        | Chuyển khoản | InStore  | 0        |

# ============================================================
# 3. Lưu ý
# ============================================================

# - Tên file phải có đuôi .xlsx hoặc .csv
# - File phải được đặt TRỰC TIẾP trong thư mục này (không có thư mục con)
# - ETL chỉ đọc file mới hơn watermark lần chạy cuối
# - Mỗi ngày nên có 1 file mới đặt tên theo ngày
