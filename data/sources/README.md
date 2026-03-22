# Thư mục data/sources - Nguồn dữ liệu thực tế

Thư mục này chứa các file dữ liệu thực tế từ hệ thống nguồn (POS, Kho, Sản phẩm).

## Cấu trúc file nguồn

### 1. BaoCaoDoanhThu_2025.xlsx
- **Mô tả**: Báo cáo doanh thu từ hệ thống POS
- **Định dạng**: Excel (.xlsx), có thể chứa nhiều sheets (theo tháng)
- **Sheet**: `DanhSachHoaDon` hoặc theo tháng (VD: `2025-01`)
- **Cột**:
  - `MaHoaDon` (VARCHAR): Mã hóa đơn
  - `MaSP` (VARCHAR): Mã sản phẩm
  - `MaKH` (VARCHAR): Mã khách hàng (NULL nếu khách lẻ)
  - `MaCH` (VARCHAR): Mã cửa hàng
  - `MaNV` (VARCHAR): Mã nhân viên bán hàng
  - `NgayBan` (DATE): Ngày bán (định dạng DD/MM/YYYY)
  - `SoLuong` (INT): Số lượng bán
  - `DonGiaBan` (DECIMAL): Đơn giá bán
  - `ChietKhau` (DECIMAL): Số tiền chiết khấu
  - `ThueSuat` (DECIMAL): Thuế suất VAT (mặc định 0.10)
  - `PhuongThucTT` (VARCHAR): Phương thức thanh toán
  - `KenhBan` (VARCHAR): Kênh bán (InStore/Online)
  - `IsHoanTra` (BIT): Cờ hoàn trả (0/1)

### 2. QuanLyKho_2025.xlsx
- **Mô tả**: Báo cáo tồn kho từ hệ thống quản lý kho
- **Định dạng**: Excel (.xlsx)
- **Sheet**: `QuanLyKho` hoặc theo tháng
- **Cột**:
  - `MaPhieu` (VARCHAR): Mã phiếu
  - `MaSP` (VARCHAR): Mã sản phẩm
  - `MaCH` (VARCHAR): Mã cửa hàng/kho
  - `MaNCC` (VARCHAR): Mã nhà cung cấp
  - `NgayChot` (DATE): Ngày chốt tồn kho
  - `TonDauNgay` (INT): Tồn đầu ngày
  - `TonCuoiNgay` (INT): Tồn cuối ngày
  - `NhapTrongNgay` (INT): Số lượng nhập trong ngày
  - `XuatTrongNgay` (INT): Số lượng xuất trong ngày

### 3. DanhMucSanPham.csv
- **Mô tả**: Danh mục sản phẩm từ bộ phận thu mua
- **Định dạng**: CSV (UTF-8)
- **Cột**:
  - `MaSP`, `TenSP`, `ThuongHieu`, `DanhMuc`, `DanhMucCon`
  - `GiaVon`, `GiaNiemYet`, `DonViTinh`, `BaoHanh_Thang`

### 4. DanhSachKhachHang.csv
- **Mô tả**: Danh sách khách hàng đã đăng ký
- **Định dạng**: CSV (UTF-8)
- **Cột**:
  - `MaKH`, `HoTen`, `GioiTinh`, `NgaySinh`, `DienThoai`, `Email`
  - `ThanhPho`, `LoaiKH`, `DiemTichLuy`, `NgayDangKy`

### 5. DanhSachCuaHang.csv
- **Mô tả**: Thông tin cửa hàng
- **Định dạng**: CSV (UTF-8)
- **Cột**:
  - `MaCH`, `TenCH`, `LoaiHinh`, `DiaChi`, `QuanHuyen`, `ThanhPho`
  - `NgayKhaiTruong`, `QuanLy`, `DienTich_m2`

### 6. DanhSachNhanVien.csv
- **Mô tả**: Danh sách nhân viên
- **Định dạng**: CSV (UTF-8)
- **Cột**:
  - `MaNV`, `HoTen`, `PhongBan`, `ChucVu`, `MaCH`, `NgayVaoLam`

### 7. DanhSachNhaCungCap.csv
- **Mô tả**: Danh sách nhà cung cấp
- **Định dạng**: CSV (UTF-8)
- **Cột**:
  - `MaNCC`, `TenNCC`, `QuocGia`, `NguoiLienHe`, `DienThoai`, `Email`, `DieuKhoanTT_Ngay`

## Ghi chú

- Tất cả file phải được đặt trong thư mục `data/sources/`
- ETL pipeline sẽ tự động nhận diện và rename columns
- Nếu file nguồn có cấu trúc khác, chỉnh sửa mapping trong `etl/extract/*.py`
- File mẫu sinh tự động: xem `data/samples/generate_mock_data.py`
