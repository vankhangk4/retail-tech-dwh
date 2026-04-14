# ============================================================
# FILE: data/STORE_HN/README.md
# Mô tả: Hướng dẫn cấu trúc file dữ liệu cho STORE_HN
# ============================================================

# Thư mục này chứa file Excel/CSV nguồn của Cửa hàng Hà Nội (STORE_HN)
# ETL sẽ tự động đọc file trong thư mục này mỗi đêm lúc 02:00 SA

# ============================================================
# 1. Cấu trúc file bắt buộc
# ============================================================

# File báo cáo bán hàng: BaoCaoDoanhThu_HN_YYYYMMDD.xlsx
#   - Sheet: "DanhSachHoaDon"
#   - Các cột bắt buộc:
#       Mã hóa đơn | Mã sản phẩm | Mã khách hàng | Mã cửa hàng | Mã nhân viên
#       Ngày bán | Số lượng | Đơn giá | Chiết khấu | Thuế VAT
#       Phương thức TT | Kênh bán | Hoàn trả
#
# File quản lý tồn kho: QuanLyKho_HN_YYYYMMDD.xlsx
#   - Sheet: (mặc định)
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
# 2. Ví dụ dữ liệu BaoCaoDoanhThu_HN_20260101.xlsx
# ============================================================

# Sheet: "DanhSachHoaDon"
# | Mã hóa đơn | Mã sản phẩm | Mã khách hàng | Mã cửa hàng | Mã nhân viên | Ngày bán    | Số lượng | Đơn giá   | Chiết khấu | Thuế VAT | Phương thức TT | Kênh bán | Hoàn trả |
# |------------|-------------|--------------|------------|-------------|------------|----------|-----------|------------|----------|---------------|----------|----------|
# | HD_HN_0001 | SP001       | KH001        | STORE_HN   | NV001       | 01/01/2026 | 2        | 25000000  | 500000    | 0        | Tiền mặt     | InStore  | 0        |
# | HD_HN_0002 | SP002       | KH002        | STORE_HN   | NV001       | 01/01/2026 | 1        | 35000000  | 0         | 0        | Chuyển khoản | InStore  | 0        |
# | HD_HN_0003 | SP001       | KH001        | STORE_HN   | NV002       | 02/01/2026 | 1        | 25000000  | 2500000   | 0        | Tiền mặt     | InStore  | 0        |

# ============================================================
# 3. Lưu ý
# ============================================================

# - Tên file phải có đuôi .xlsx hoặc .csv
# - File phải được đặt TRỰC TIẾP trong thư mục này (không có thư mục con)
# - ETL chỉ đọc file mới hơn watermark lần chạy cuối
# - Nếu cần load lại toàn bộ data: xóa bản ghi trong ETL_Watermark
# - Mỗi ngày nên có 1 file mới đặt tên theo ngày
