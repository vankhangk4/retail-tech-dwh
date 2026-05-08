# Hướng dẫn sử dụng — DWH Multi-Tenant System

**Phiên bản:** 1.0  
**Cập nhật:** 2026-05-08

---

## Mục lục

1. [Tổng quan hệ thống](#1-tổng-quan-hệ-thống)
2. [Hướng dẫn cho SuperAdmin](#2-hướng-dẫn-cho-superadmin)
3. [Hướng dẫn cho TenantAdmin](#3-hướng-dẫn-cho-tenantadmin)
4. [Hướng dẫn cho TenantViewer](#4-hướng-dẫn-cho-tenantviewer)
5. [Quản lý ETL & Dữ liệu](#5-quản-lý-etl--dữ-liệu)
6. [Sử dụng Dashboard Superset](#6-sử-dụng-dashboard-superset)
7. [Quản lý hồ sơ cá nhân](#7-quản-lý-hồ-sơ-cá-nhân)

---

## 1. Tổng quan hệ thống

Hệ thống DWH Multi-Tenant cho phép nhiều chi nhánh (tenant) sử dụng chung một nền tảng Data Warehouse, nhưng dữ liệu mỗi chi nhánh được **tách biệt hoàn toàn**.

### Các role trong hệ thống

| Role | Mô tả | Quyền hạn |
|------|--------|-----------|
| **superadmin** | Quản trị viên tổng | Xem & quản lý tất cả tenants |
| **admin** | Quản trị viên tenant | Quản lý 1 tenant cụ thể |
| **viewer** | Người dùng xem | Chỉ xem dashboard của tenant mình |

### Kiến trúc hệ thống

```
[Trình duyệt]
     │
     ▼
[Frontend Flask :5000]  ← trang đăng nhập, dashboard embed
     │
     ▼
[API FastAPI :8000]  ← xác thực JWT, quản lý tenant
     │
     ├──► [SQL Server :1433]  ← DWH, AppUsers, ETL logs
     │
     └──► [Superset :8088]  ← BI dashboards (guest token)
```

---

## 2. Hướng dẫn cho SuperAdmin

### 2.1. Đăng nhập

1. Mở trình duyệt, truy cập `http://localhost:5000`
2. Nhập tài khoản SuperAdmin (mặc định: `admin` / `admin`)
3. Bấm **Đăng nhập**

### 2.2. Thêm Tenant mới

**Qua API (curl):**
```bash
curl -X POST http://localhost:8000/api/tenants \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "STORE_DN",
    "tenant_name": "Chi nhánh Đà Nẵng",
    "file_path": "/data/store_dn/",
    "is_active": true
  }'
```

Hệ thống sẽ **tự động**:
- Tạo bản ghi trong bảng `Tenants`
- Provisioning Superset user + RLS rule cho tenant mới

### 2.3. Quản lý người dùng

**Xem danh sách users:**
```bash
curl http://localhost:8000/api/users \
  -H "Authorization: Bearer <access_token>"
```

**Tạo user mới cho tenant:**
```bash
curl -X POST http://localhost:8000/api/admin/users \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nhanvien01",
    "password": "StrongPass123!",
    "tenant_id": "STORE_DN",
    "role": "viewer"
  }'
```

**Khoá/mở khoá tài khoản:**
```bash
curl -X PUT http://localhost:8000/api/users/5 \
  -H "Authorization: Bearer <access_token>" \
  -d '{"is_active": false}'
```

### 2.4. Xem trạng thái ETL toàn hệ thống

```bash
curl http://localhost:8000/api/etl-status \
  -H "Authorization: Bearer <access_token>"
```

### 2.5. Xem KPI tổng hợp

```bash
curl http://localhost:8000/api/kpi \
  -H "Authorization: Bearer <access_token>"
```

Kết quả trả về: tổng doanh thu, số đơn hàng, số tenant, ETL runs gần nhất.

---

## 3. Hướng dẫn cho TenantAdmin

### 3.1. Đăng nhập

1. Truy cập `http://localhost:5000`
2. Đăng nhập bằng tài khoản admin của tenant mình
3. Chỉ thấy dữ liệu của tenant mình

### 3.2. Upload dữ liệu

**Qua giao diện web:**
1. Vào trang **Dashboard** → chọn **Upload Data**
2. Chọn file Excel/CSV
3. Chọn loại dữ liệu: Sales / Inventory / Purchase
4. Bấm **Upload & Run ETL**
5. Theo dõi tiến độ ETL trong phần **ETL Status**

**Qua API:**
```bash
# Upload file
curl -X POST http://localhost:8000/api/upload/STORE_HN \
  -H "Authorization: Bearer <access_token>" \
  -F "file=@/path/to/sales_data.xlsx"

# Trigger ETL sau khi upload
curl -X POST "http://localhost:8000/api/upload/STORE_HN/etl?filename=sales_data.xlsx" \
  -H "Authorization: Bearer <access_token>"
```

### 3.3. Theo dõi ETL

```bash
curl "http://localhost:8000/api/etl/logs?tenant_id=STORE_HN&limit=10" \
  -H "Authorization: Bearer <access_token>"
```

### 3.4. Trigger ETL thủ công

```bash
curl -X POST http://localhost:8000/api/etl/trigger/STORE_HN \
  -H "Authorization: Bearer <access_token>"
```

---

## 4. Hướng dẫn cho TenantViewer

### 4.1. Đăng ký tài khoản

1. Truy cập `http://localhost:5000/register`
2. Điền thông tin:
   - **Tenant ID**: mã chi nhánh của bạn (do admin cung cấp)
   - **Tên đăng nhập**: chỉ chứa chữ cái, số, dấu gạch dưới
   - **Mật khẩu**: tối thiểu 8 ký tự
3. Bấm **Đăng ký**

### 4.2. Đăng nhập và xem Dashboard

1. Truy cập `http://localhost:5000`
2. Đăng nhập bằng tài khoản của mình
3. Chọn Dashboard muốn xem từ menu:
   - 📊 **Doanh thu** — phân tích doanh số theo thời gian
   - 📦 **Sản phẩm** — TOP sản phẩm, tỷ trọng danh mục
   - 🏪 **Tồn kho** — cảnh báo hàng tồn, turnover rate
   - 👥 **Khách hàng** — RFM segmentation, CLV
   - 👨‍💼 **Nhân viên** — hiệu suất bán hàng

### 4.3. Tính năng Dashboard

- **Lọc theo thời gian**: chọn date range ở thanh lọc trên cùng
- **Lọc theo cửa hàng**: chọn store từ dropdown
- **Drill-down**: click vào biểu đồ để xem chi tiết hơn
- **Cross-filter**: click 1 chart để filter các chart còn lại
- **Export**: bấm nút ⋮ → Download để tải CSV/Excel

---

## 5. Quản lý ETL & Dữ liệu

### 5.1. Cấu trúc file dữ liệu

**Sales (Excel/CSV):**
| Cột | Bắt buộc | Định dạng | Ví dụ |
|-----|----------|-----------|-------|
| MaHoaDon | ✅ | VARCHAR | HD001 |
| MaSP | ✅ | VARCHAR | SP001 |
| MaKH | ❌ | VARCHAR | KH001 |
| MaCH | ✅ | VARCHAR | CH001 |
| MaNV | ❌ | VARCHAR | NV001 |
| NgayBan | ✅ | DD/MM/YYYY | 01/06/2024 |
| SoLuong | ✅ | INT > 0 | 2 |
| DonGiaBan | ✅ | DECIMAL >= 0 | 1000000 |
| ChietKhau | ❌ | DECIMAL | 50000 |
| ThueVAT | ❌ | DECIMAL | 100000 |
| PhuongThucTT | ❌ | TEXT | cash / transfer |
| KenhBan | ❌ | TEXT | instore / online |

**Inventory (CSV):**
Cột: Mã sản phẩm, Mã cửa hàng, Ngày chụp ảnh, Tồn đầu ngày, Tồn cuối ngày, Nhập trong ngày, Bán trong ngày, Điều chỉnh, Đơn giá vốn

**Purchase (CSV):**
Cột: Số phiếu đặt, Mã SP, Mã NCC, Mã cửa hàng, Ngày đặt, Ngày nhận, Số lượng đặt, Số lượng nhận, Đơn giá nhập

### 5.2. Quy trình ETL tự động

```
1. SCAN      → Tìm files mới trong thư mục tenant
2. EXTRACT   → Đọc file, filter theo watermark
3. TRANSFORM → Làm sạch, chuẩn hóa, dedup
4. LOAD DIMS → Upsert vào Dimension tables
5. LOAD FACTS→ Insert vào Fact tables
6. REFRESH DM→ Cập nhật Data Mart aggregations
7. WATERMARK → Ghi mốc thời gian thành công
```

### 5.3. Xem lỗi ETL

Khi ETL có lỗi, cần kiểm tra:
1. ETLLogs table: `SELECT * FROM ETLLogs WHERE RunStatus = 'FAILED'`
2. STG_ErrorLog table: `SELECT * FROM STG_ErrorLog ORDER BY CreatedAt DESC`
3. File log tại: `logs/{tenant_id}/etl_{date}.log`

---

## 6. Sử dụng Dashboard Superset

### 6.1. Các Dashboard có sẵn

| Dashboard | Metric chính | Filters |
|-----------|-------------|---------|
| Doanh thu | TotalRevenue, AvgOrderValue, YoY% | Thời gian, Store, Category |
| Sản phẩm | TOP10 sản phẩm, Gross Margin% | Thời gian, Category, Brand |
| Tồn kho | Stock alerts, Turnover rate | Store, Category |
| Khách hàng | RFM Segment, CLV | Thời gian, Segment |
| Nhân viên | Revenue/employee, Conversion rate | Thời gian, Store, Shift |

### 6.2. RFM Segments

| Segment | Recency | Frequency | Monetary |
|---------|---------|-----------|----------|
| Champion | < 30 ngày | > 10 lần | > 5M VND |
| Loyal | < 60 ngày | > 5 lần | > 2M VND |
| At Risk | > 90 ngày | > 3 lần | > 1M VND |
| Lost | > 180 ngày | Bất kỳ | Bất kỳ |

---

## 7. Quản lý hồ sơ cá nhân

### 7.1. Cập nhật thông tin

1. Đăng nhập → click avatar/tên ở góc trên phải
2. Chọn **Cài đặt** (Settings)
3. Cập nhật: Display Name, Email, Số điện thoại
4. Bấm **Lưu thay đổi**

### 7.2. Đổi mật khẩu

1. Vào **Cài đặt** → tab **Bảo mật**
2. Nhập mật khẩu hiện tại
3. Nhập mật khẩu mới (tối thiểu 8 ký tự)
4. Xác nhận mật khẩu mới
5. Bấm **Đổi mật khẩu**

### 7.3. Upload ảnh đại diện

1. Vào **Cài đặt** → click vào ảnh đại diện
2. Chọn file ảnh (JPG/PNG, tối đa 5MB)
3. Bấm **Lưu**

### 7.4. Xem lịch sử đăng nhập

Vào **Cài đặt** → tab **Lịch sử đăng nhập** để xem 20 phiên đăng nhập gần nhất (thời gian, IP, thiết bị).

---

## Thông tin liên hệ hỗ trợ

- **Email:** vankhangk4@gmail.com
- **Báo lỗi:** Tạo issue tại GitHub repository của dự án
- **Tài liệu kỹ thuật:** Xem `DEPLOYMENT.md` và `docs/TROUBLESHOOTING.md`
