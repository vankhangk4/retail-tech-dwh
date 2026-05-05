**TRƯỜNG ĐẠI HỌC THUỶ LỢI**

**KHOA CÔNG NGHỆ THÔNG TIN**

**ĐỀ CƯƠNG ĐỒ ÁN TỐT NGHIỆP**

**Tên đề tài: Xây dựng hệ thống Data Warehouse và trực quan hóa dữ liệu kinh doanh**

**cho chuỗi cửa hàng bán lẻ thiết bị công nghệ (Phiên bản Multi-Tenant)**

Sinh viên thực hiện: Nguyễn Văn Khang

Lớp: 64HTTT4  |  Mã sinh viên: 2251162042

Số điện thoại: 0977159653  |  Email: vankhangk4@gmail.com

Giáo viên hướng dẫn: TS. Đỗ Oanh Cường

# **CHƯƠNG 1: TỔNG QUAN HỆ THỐNG**

## **1.1. Bối cảnh và Thực trạng Doanh nghiệp**

### **1.1.1. Mô tả Thực trạng**

Trong bối cảnh nền kinh tế số đang phát triển mạnh mẽ, các doanh nghiệp bán lẻ thiết bị công nghệ phải đối mặt với áp lực cạnh tranh ngày càng gay gắt. Dữ liệu kinh doanh được xem là tài sản chiến lược, tuy nhiên nhiều doanh nghiệp vừa và nhỏ vẫn chưa khai thác hiệu quả nguồn tài nguyên này.

Hiện tại, doanh nghiệp đang quản lý toàn bộ dữ liệu hoạt động kinh doanh thông qua các tệp tin đơn lẻ dạng Microsoft Excel hoặc Google Sheets. Mỗi bộ phận (kinh doanh, kho vận, kế toán, nhân sự) duy trì một hệ thống tệp tin riêng biệt, không có sự liên thông và tích hợp.

| 📌 Các vấn đề nổi cộm trong thực trạng hiện tại • Dữ liệu bị phân mảnh: Mỗi tệp Excel là một 'đảo dữ liệu' độc lập, không có cơ chế tích hợp tự động. • Không nhất quán: Cùng một chỉ số có thể cho kết quả khác nhau tùy theo người tổng hợp. • Không có lịch sử: Dữ liệu lịch sử theo thời gian bị ghi đè hoặc lưu trữ tùy tiện. • Hiệu quả thấp: Báo cáo hàng tháng mất 3–5 ngày làm việc thủ công. • Rủi ro mất dữ liệu: Không có cơ chế backup tập trung và kiểm soát phiên bản. |
| :---- |

### **1.1.2. Phân tích Hệ thống Nguồn Dữ liệu**

Dữ liệu hiện tại đến từ ba nguồn chính, hoạt động độc lập:

| Nguồn Dữ liệu | Định dạng | Tần suất cập nhật | Người phụ trách |
| :---- | :---- | :---- | :---- |
| Hệ thống Bán hàng (POS) | Excel / CSV | Hàng ngày | Bộ phận Kinh doanh |
| Hệ thống Quản lý Kho | Excel / Google Sheets | Hàng ngày | Bộ phận Kho vận |
| Danh mục Sản phẩm | Excel / CSV tĩnh | Theo đợt nhập hàng | Bộ phận Thu mua |

## **1.2. Lý do Cần xây dựng Data Warehouse**

* Tập trung hóa dữ liệu: Mọi nguồn được tích hợp vào một điểm duy nhất (Single Source of Truth).

* Hỗ trợ phân tích lịch sử: DWH lưu trữ dữ liệu theo chiều thời gian, cho phép phân tích xu hướng dài hạn.

* Nâng cao chất lượng dữ liệu: Quy trình ETL tích hợp các bước làm sạch, chuẩn hóa có hệ thống.

* Tốc độ phân tích: Star Schema được tối ưu cho truy vấn OLAP, báo cáo theo thời gian thực.

* Hỗ trợ đa người dùng (Multi-Tenant): Nhiều cửa hàng/chi nhánh dùng chung hạ tầng, mỗi đơn vị chỉ truy cập dữ liệu của mình. \[MỚI\]

## **1.3. Mục tiêu Dự án**

### **1.3.1. Mục tiêu Tổng quát**

Xây dựng một hệ thống Data Warehouse toàn diện, bao gồm cơ sở hạ tầng lưu trữ, quy trình xử lý dữ liệu tự động (ETL), và nền tảng trực quan hóa phục vụ phân tích kinh doanh cho chuỗi cửa hàng bán lẻ thiết bị công nghệ, với khả năng phục vụ nhiều người dùng độc lập (multi-tenant).

### **1.3.2. Mục tiêu Cụ thể**

1. Xây dựng cơ sở dữ liệu Data Warehouse trên SQL Server với mô hình Star Schema, đảm bảo lưu trữ hàng triệu bản ghi giao dịch.

2. Triển khai quy trình ETL tự động có khả năng thu thập dữ liệu từ nhiều nguồn không đồng nhất.

3. Xây dựng các bảng Dimension và Fact phản ánh đầy đủ các thực thể kinh doanh.

4. Triển khai Apache Superset làm nền tảng BI, xây dựng ít nhất 5 Dashboard tương tác phân tích KPIs.

5. Xây dựng hệ thống phân quyền đa người dùng (multi-tenant): mỗi cửa hàng chỉ xem dữ liệu của mình; admin quản lý toàn bộ. \[MỚI\]

6. Đảm bảo hiệu năng truy vấn dưới 3 giây cho báo cáo tổng hợp thông thường.

# **CHƯƠNG 2: YÊU CẦU HỆ THỐNG**

## **2.1. Yêu cầu Chức năng**

### **2.1.1. Nhóm Chức năng Thu thập và Tích hợp Dữ liệu**

* FR-01: Hỗ trợ đọc và xử lý tệp tin .xlsx, .xls, .csv từ thư mục cục bộ hoặc mạng nội bộ.

* FR-02: Hỗ trợ kết nối đến CSDL quan hệ (SQL Server, MySQL) thông qua ODBC/JDBC làm nguồn dữ liệu.

* FR-03: Hỗ trợ lập lịch (scheduling) tự động cho quy trình ETL với tần suất tùy chỉnh.

* FR-04: Cơ chế trích xuất tăng dần (Incremental Extraction) — mỗi tenant có watermark riêng; watermark được cập nhật sau mỗi lần ETL thành công bằng cách ghi GETDATE() vào bảng ETL\_Watermark với LastRunStatus \= 'SUCCESS'.

### **2.1.2. Nhóm Chức năng Biến đổi và Làm sạch Dữ liệu**

* FR-05: Phát hiện và loại bỏ các bản ghi trùng lặp dựa trên khóa nghiệp vụ (business key).

* FR-06: Chuẩn hóa định dạng: ngày tháng (DD/MM/YYYY → DATE), đơn vị tiền tệ (loại bỏ ký tự thừa), chuỗi ký tự (UPPER/TRIM).

* FR-07: Xử lý giá trị NULL và dữ liệu thiếu bằng chiến lược thay thế phù hợp (giá trị mặc định, ghi lỗi).

* FR-08: Kiểm tra ràng buộc toàn vẹn tham chiếu: FK trong bảng Fact phải trỏ đến PK hợp lệ trong bảng Dimension.

* FR-09: Ghi log chi tiết cho toàn bộ quá trình ETL (số bản ghi xử lý, số lỗi, thời gian, TenantID).

### **2.1.3. Nhóm Chức năng Quản lý Người dùng Đa Tenant \[MỚI\]**

| 🆕 Yêu cầu mới — Multi-Tenant User Management • FR-10: Hệ thống hỗ trợ đăng ký và quản lý nhiều tenant (cửa hàng/chi nhánh) độc lập trong cùng một CSDL. • FR-11: Mỗi tenant có tài khoản riêng biệt, đăng nhập qua Auth Gateway (FastAPI) nhận JWT token chứa tenant\_id và role. • FR-12: Dữ liệu của tenant A tuyệt đối không hiển thị đối với tenant B — được đảm bảo bởi Superset Row Level Security. • FR-13: Admin có thể xem và quản lý dữ liệu của toàn bộ tenant — không bị giới hạn bởi bất kỳ RLS filter nào. • FR-14: ETL pipeline tự động gắn tenant\_id vào mọi bản ghi ngay từ bước Extract (df\['TenantID'\] \= tenant\_id). • FR-15: Superset Row Level Security (RLS) tự động append WHERE tenant\_id='X' vào mọi query của user thuộc tenant X. • FR-16: Người dùng tenant không có quyền truy cập Superset admin panel — chỉ có role TenantViewer (read-only). |
| :---- |

### **2.1.4. Nhóm Chức năng Dashboard và Trực quan hóa**

* FR-17: Dashboard Phân tích Doanh thu: biểu đồ doanh thu theo ngày/tuần/tháng/năm, so sánh cùng kỳ, phân tích theo cửa hàng và danh mục sản phẩm.

* FR-18: Dashboard Phân tích Sản phẩm: TOP 10 sản phẩm bán chạy, tỷ lệ đóng góp doanh thu, phân tích biên lợi nhuận gộp.

* FR-19: Dashboard Quản lý Tồn kho: cảnh báo tồn kho dưới ngưỡng tối thiểu, xu hướng nhập/xuất kho.

* FR-20: Dashboard Phân tích Khách hàng: phân khúc theo RFM (Recency, Frequency, Monetary), tỷ lệ khách hàng quay lại.

* FR-21: Dashboard Hiệu suất Nhân viên: doanh số theo nhân viên, tỷ lệ chuyển đổi, hiệu quả theo ca làm việc.

* FR-22: Hỗ trợ lọc dữ liệu đa chiều (drill-down/drill-up) theo thời gian, địa điểm, danh mục sản phẩm.

**2.1B. Biểu đồ và Đặc tả Use Case**

Phần này trình bày mô hình Use Case UML thể hiện các chức năng chính của hệ thống, xác định rõ Actor (tác nhân) và các Use Case tương tác. Code PlantUML được cung cấp để sinh biểu đồ tự động.

**2.1B.1. Xác định các Actor (Tác nhân)**

| STT | Tên Actor | Mô tả | Loại |
| :---- | :---- | :---- | :---- |
| 1 | System Admin | Người quản lý toàn bộ hạ tầng DWH, giám sát ETL, quản lý tenant & user | Primary |
| 2 | Tenant Viewer | Người dùng tại chi nhánh — chỉ xem Dashboard thuộc cửa hàng mình | Primary |
| 3 | ETL Scheduler | Hệ thống tự động chạy ETL lúc 02:00 SA hàng ngày | System Actor |

**2.1B.2. Biểu đồ Use Case tổng quát (PlantUML)**

![][image1]

**2.1B.3. Đặc tả Use Case chi tiết**

**2.1B.3.1. UC01 — Đăng nhập Auth Gateway**

| Thuộc tính | Nội dung |
| :---- | :---- |
| Use Case ID | UC01 |
| Use Case Name | Đăng nhập Auth Gateway |
| Actor | System Admin, Tenant Viewer |
| Mục tiêu | Xác thực người dùng, cấp JWT token chứa tenant\_id và role |
| Tiền điều kiện (Precondition) | Người dùng đã có tài khoản trong bảng AppUsers |
| Hậu điều kiện (Postcondition) | JWT token được trả về, frontend lưu token và gửi kèm mọi request |

**Luồng sự kiện chính (Main Flow):**

1\. User mở giao diện đăng nhập.

2\. User nhập Username và Password.

3\. Hệ thống gọi POST /auth/login với {username, password}.

4\. Auth Gateway truy vấn bảng AppUsers, xác thực bcrypt.

5\. Hệ thống tạo JWT token chứa {user\_id, tenant\_id, role}.

6\. Token được trả về cho client.

**Luồng thay thế (Alternate Flow):**

A1: Sai mật khẩu → Trả về HTTP 401 Unauthorized.

A2: Tài khoản bị khóa (IsActive \= 0\) → Trả về HTTP 403 Forbidden.

A3: Tenant không hoạt động → Trả về HTTP 403 Forbidden.

**2.1B.3.2. UC02 — Xem Dashboard Phân tích Doanh thu**

| Thuộc tính | Nội dung |
| :---- | :---- |
| Use Case ID | UC02 |
| Use Case Name | Xem Dashboard Phân tích Doanh thu |
| Actor | System Admin, Tenant Viewer |
| Mục tiêu | Cho phép user xem biểu đồ doanh thu theo thời gian, cửa hàng, sản phẩm |
| Tiền điều kiện | User đã đăng nhập (JWT hợp lệ); dữ liệu đã được nạp qua ETL |
| Hậu điều kiện | Dashboard hiển thị dữ liệu phù hợp với tenant\_id của user |

**Luồng sự kiện chính:**

1\. User chọn Dashboard "Phân tích Doanh thu" trên Superset.

2\. Superset gửi SQL query đến SQL Server với RLS filter tự động.

3\. RLS tự động thêm WHERE tenant\_id \= '\<current\_tenant\>' vào query.

4\. SQL Server trả dữ liệu về Superset.

5\. Superset render biểu đồ: doanh thu theo ngày/tuần/tháng, TOP sản phẩm.

**Sequence Diagram — UC02 (PlantUML):**

![][image2]

**2.1B.3.3. UC06 — Chạy ETL Pipeline**

| Thuộc tính | Nội dung |
| :---- | :---- |
| Use Case ID | UC06 |
| Use Case Name | Chạy ETL Pipeline |
| Actor | ETL Scheduler (tự động), System Admin (thủ công) |
| Mục tiêu | Trích xuất, làm sạch, chuyển đổi và nạp dữ liệu vào DWH |
| Tiền điều kiện | File Excel/CSV nguồn tồn tại tại FilePath của tenant; kết nối DB thành công |
| Hậu điều kiện | Dữ liệu mới được insert/update vào các bảng Fact & Dimension; watermark được cập nhật |

**Luồng sự kiện chính:**

1\. Scheduler kích hoạt job hoặc Admin nhấn "Run ETL" trên Admin Panel.

2\. ETL process truy vấn bảng Tenants để lấy danh sách tenant active.

3\. Với mỗi tenant: đọc file Excel/CSV từ FilePath tương ứng.

4\. Thực hiện Extract: incremental dựa trên watermark (ngày cắt ngưỒn).

5\. Thực hiện Transform: loại bỏ trùng, chuẩn hóa, kiểm tra FK.

6\. Gắn tenant\_id vào mọi bản ghi (df\['TenantID'\] \= tenant\_id).

7\. Load: INSERT/UPDATE vào FactSales, FactInventory, FactPurchase & các Dimension.

8\. Cập nhật watermark cho tenant đó.

9\. Ghi log chi tiết vào bảng ETLLogs.

**Sequence Diagram — UC06 (PlantUML):**

## **![][image3]2.2. Yêu cầu Phi chức năng**

| Mã yêu cầu | Danh mục | Yêu cầu cụ thể | Chỉ tiêu đo lường |
| :---- | :---- | :---- | :---- |
| NFR-01 | Hiệu năng (Performance) | Tốc độ truy vấn báo cáo tổng hợp | ≤ 3 giây cho tập dữ liệu ≤ 5 triệu bản ghi |
| NFR-02 | Hiệu năng (Performance) | Thời gian thực thi ETL hàng ngày | ≤ 30 phút cho ≤ 50.000 giao dịch/ngày |
| NFR-03 | Khả năng lưu trữ | Dung lượng dữ liệu tối đa | Hỗ trợ ≥ 100 triệu bản ghi trong bảng Fact |
| NFR-04 | Toàn vẹn dữ liệu | Chính xác dữ liệu sau ETL | Tỷ lệ bản ghi lỗi ≤ 0.1% tổng số bản ghi |
| NFR-05 | Độ tin cậy (Availability) | Uptime hệ thống | ≥ 99% trong giờ làm việc (8:00–22:00) |
| NFR-06 | Bảo mật (Security) | Xác thực và phân quyền | JWT HS256, bcrypt password hash, RBAC \+ RLS theo tenant\_id \[MỚI\] |
| NFR-07 | Bảo mật (Security) | Truyền dữ liệu | HTTPS bắt buộc cho toàn bộ API và Superset endpoint |
| NFR-08 | Bảo mật (Security) | JWT Token expiry | Access token hết hạn sau 8 giờ, refresh token sau 7 ngày \[MỚI\] |
| NFR-09 | Khả năng mở rộng (Scalability) | Thêm tenant mới | Không cần thay đổi kiến trúc — chỉ INSERT vào bảng Tenants \[MỚI\] |
| NFR-10 | Khả năng mở rộng (Scalability) | Thêm nguồn dữ liệu mới | Thêm module Extract mới mà không ảnh hưởng pipeline hiện tại |
| NFR-11 | Khả dụng | Tương thích trình duyệt | Chrome, Firefox, Edge (phiên bản mới nhất) |
| NFR-12 | Giám sát (Monitoring) | Alert khi ETL thất bại | Gửi email/Slack trong vòng 5 phút khi ETL status \= FAILED \[MỚI\] |

# **CHƯƠNG 3: KIẾN TRÚC HỆ THỐNG TỔNG THỂ**

## **3.1. Mô hình Kiến trúc Đề xuất**

Hệ thống được thiết kế theo kiến trúc phân tầng (Layered Architecture) gồm 5 tầng chính — cập nhật từ 4 tầng trong thiết kế đơn người dùng, bổ sung Tầng 0 Auth Gateway phục vụ multi-tenant.

| 📌 Sơ đồ Kiến trúc Tổng thể 5 Tầng • Tầng 0: Auth Gateway — FastAPI/JWT, xác thực user, gán tenant\_id vào token \[MỚI\] • Tầng 1: Data Sources — File Excel/CSV riêng của từng tenant • Tầng 2: ETL Processing Layer — Python ETL với tenant\_id tagging \+ Error Logging • Tầng 3: Data Warehouse — SQL Server với Row-Level Isolation theo tenant\_id • Tầng 4: BI & Visualization — Apache Superset với RBAC \+ Row Level Security |
| :---- |

## **3.2. Mô tả Chi tiết từng Tầng**

### **3.2.1. Tầng 0: Auth Gateway \[MỚI\]**

| 🆕 Auth Gateway — FastAPI/JWT • Xây dựng bằng FastAPI \+ PyJWT \+ bcrypt. • Quản lý bảng AppUsers và Tenants trong SQL Server. • Endpoint /login: xác thực username/password (bcrypt), trả về JWT chứa tenant\_id và role. • Endpoint /dashboard-token: nhận JWT, tạo Superset Guest Token để user xem dashboard. • Người dùng tenant KHÔNG đăng nhập trực tiếp vào Superset. |
| :---- |

### **3.2.2. Tầng 1: Data Sources**

Mỗi tenant (cửa hàng/chi nhánh) upload file Excel/CSV riêng. Dữ liệu được đọc theo chế độ Read-Only, không can thiệp vào hệ thống nguồn.

* Nguồn 1 – Hệ thống Bán hàng: Tệp Excel/CSV xuất từ phần mềm POS, chứa thông tin hóa đơn và chi tiết giao dịch.

* Nguồn 2 – Hệ thống Quản lý Kho: Tệp Excel/Google Sheets ghi nhận phiếu nhập kho, xuất kho, tồn kho.

* Nguồn 3 – Danh mục Sản phẩm: Tệp CSV tĩnh định nghĩa cấu trúc danh mục, giá nhập, giá niêm yết.

### **3.2.3. Tầng 2: ETL Processing Layer**

Tầng xử lý dữ liệu được cập nhật để nhận tenant\_id như tham số bắt buộc. Mọi bản ghi được tag tenant\_id trước khi nạp vào Staging.

* Staging Database: Tất cả bảng STG\_\* đều có cột TenantID.

* Transformation Engine: Mọi Stored Procedure Transform đều nhận @TenantID làm tham số.

* ETL Orchestrator: Chạy vòng lặp qua danh sách tenant đang hoạt động, gọi ETL cho từng tenant.

* Error Logging: Bảng STG\_ErrorLog ghi nhận mọi bản ghi lỗi kèm TenantID.

* Monitoring: Sau mỗi lần chạy ETL, hệ thống gửi alert qua email/Slack nếu status \= FAILED.

### **3.2.4. Tầng 3: Data Warehouse — SQL Server**

* Staging Layer (STG\_\*): Dữ liệu thô sau Extract — truncate và reload mỗi chu kỳ, có cột TenantID.

* Core DWH Layer: FactSales, FactInventory, FactPurchase có TenantID. DimProduct, DimDate, DimSupplier là bảng Shared (không cần TenantID).

* Data Mart Layer (DM\_\*): Aggregate Table và View được tính toán sẵn theo tenant, tối ưu hiệu năng dashboard.

### **3.2.5. Tầng 4: BI & Visualization — Apache Superset**

* Interactive Dashboards: Giao diện web-based chỉ đọc cho người dùng tenant.

* Role TenantViewer: Chỉ xem dashboard — không có quyền write, admin hay sửa đổi.

* Row Level Security: Superset tự động append WHERE tenant\_id='X' vào mọi query từ tenant X.

* Admin View: Admin xem toàn bộ data, không bị bất kỳ RLS filter nào.

## **3.3. Công nghệ và Stack Kỹ thuật**

| Thành phần | Công nghệ | Phiên bản | Ghi chú / Vai trò |
| :---- | :---- | :---- | :---- |
| Auth Gateway \[MỚI\] | FastAPI | 0.110+ | REST API xác thực, cấp JWT, tạo Superset guest token |
| Auth — JWT | PyJWT | 2.8+ | Ký và xác minh JWT HS256; access token 8h, refresh 7 ngày |
| Auth — Password Hash | bcrypt (passlib) | 1.7+ | Hash mật khẩu bcrypt rounds=12 trước khi lưu DB |
| CSDL Data Warehouse | Microsoft SQL Server | 2019 / 2022 | Lưu trữ Staging, DWH Core, Data Mart, Tenants, AppUsers |
| ETL Engine | Python | 3.10+ | Xử lý biến đổi và nạp dữ liệu (có tenant\_id param) |
| ETL Libraries | pandas 2.x, pyodbc 5.x, sqlalchemy 2.x | Mới nhất | Đọc file Excel/CSV, kết nối SQL Server, xử lý DataFrame |
| ETL Stored Procs | T-SQL (SQL Server) | SQL Server 2019 | usp\_Transform\_FactSales, usp\_Load\_DimProduct, v.v. |
| ETL Scheduler | Python schedule / SQL Server Agent | — | Chạy ETL lúc 02:00 SA hàng ngày, có cơ chế retry |
| BI Platform | Apache Superset | 3.x LTS | Dashboard với RBAC \+ Row Level Security |
| Containerization | Docker \+ Docker Compose | Latest | Service: superset, superset-db, superset-redis, api \[MỚI\] |
| Monitoring — Alert | Python smtplib \+ Slack Webhook | — | Gửi email/Slack khi ETL FAILED trong vòng 5 phút \[MỚI\] |
| Môi trường triển khai | Linux Ubuntu 22.04 / Windows Server | — | Hạ tầng triển khai production |

# **CHƯƠNG 4: THIẾT KẾ CƠ SỞ DỮ LIỆU**

## **4.1. Phương pháp Thiết kế — Dimensional Modeling**

Hệ thống Data Warehouse được thiết kế theo phương pháp Dimensional Modeling (Ralph Kimball) sử dụng Star Schema. Với multi-tenant, cột TenantID được thêm vào tất cả bảng Fact và Dimension gắn với cửa hàng. Các bảng dùng chung (DimDate, DimProduct, DimSupplier) không cần TenantID.

**4.2B. Sơ đồ Star Schema và Multi-Tenant ERD**

Phần này trình bày sơ đồ ERD trực quan cho mô hình Data Warehouse. Star Schema thể hiện quan hệ giữa bảng Fact (bảng sự kiện) ở trung tâm và các bảng Dimension (bảng chiều) bao quanh. Multi-Tenant ERD thể hiện cơ chế rào chắn dữ liệu qua TenantID.

**Biểu đồ ERD**

![][image4]

**4.2B.1. Sơ đồ Star Schema Core (PlantUML)**

![][image5]

**Bảng chú thích phân loại bảng (Shared vs Tenant-Specific):**

| Tên Bảng | Loại | Mô tả | Có TenantID? |
| :---- | :---- | :---- | :---- |
| DimDate | Shared | Chiều thời gian — dùng chung cho mọi tenant | Không (vì mỗi tenant có data riêng trong Fact) |
| DimStore | Shared | Chiều cửa hàng — 1 row/tenant; TenantID là PK | Có (là PK) |
| DimProduct | Tenant-Specific | Chiều sản phẩm riêng của từng tenant | Có (FK) |
| DimCustomer | Tenant-Specific | Chiều khách hàng riêng của từng tenant | Có (FK) |
| DimEmployee | Tenant-Specific | Chiều nhân viên riêng của từng tenant | Có (FK) |
| DimSupplier | Tenant-Specific | Chiều nhà cung cấp riêng của từng tenant | Có (FK) |
| FactSales | Tenant-Specific | Sự kiện bán hàng — core table | Có (FK) |
| FactInventory | Tenant-Specific | Sự kiện tồn kho theo ngày | Có (FK) |
| FactPurchase | Tenant-Specific | Sự kiện nhập hàng từ nhà cung cấp | Có (FK) |

**4.2B.2. Sơ đồ Multi-Tenant ERD (PlantUML)**

![][image6]

## **4.2. Bảng Quản lý Tenant và Người dùng \[MỚI\]**

| 🆕 Hai bảng mới bổ sung cho multi-tenant • Tenants: Lưu thông tin từng cửa hàng/chi nhánh — là bảng lookup cho toàn bộ hệ thống. • AppUsers: Lưu tài khoản người dùng với role admin hoặc viewer. • TenantID trong AppUsers là FK tham chiếu Tenants — đảm bảo mọi user đều thuộc 1 tenant hợp lệ. • AppUsers tách biệt hoàn toàn với Superset users — Auth Gateway quản lý phần này. |
| :---- |

**Bảng Tenants:**

| Tên Cột | Kiểu Dữ liệu | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| TenantID | VARCHAR(20) | NOT NULL | — | PK — Mã định danh cửa hàng (VD: 'STORE\_HN') |
| TenantName | NVARCHAR(200) | NOT NULL | — | Tên cửa hàng/chi nhánh |
| FilePath | NVARCHAR(500) | NULL | — | Đường dẫn file Excel/CSV của tenant này |
| IsActive | BIT | NOT NULL | 1 | Trạng thái hoạt động (1=active) |
| CreatedAt | DATETIME2 | NOT NULL | GETDATE() | Ngày tạo tenant |

**Bảng AppUsers:**

| Tên Cột | Kiểu Dữ liệu | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| UserID | INT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key tự tăng |
| Username | VARCHAR(100) | NOT NULL | — | Tên đăng nhập — UNIQUE |
| PasswordHash | VARCHAR(255) | NOT NULL | — | Mật khẩu đã hash bằng bcrypt (rounds=12) |
| TenantID | VARCHAR(20) | NULL | — | FK → Tenants — NULL nếu là admin |
| Role | VARCHAR(20) | NOT NULL | 'viewer' | Vai trò: 'admin' hoặc 'viewer' |
| IsActive | BIT | NOT NULL | 1 | Trạng thái tài khoản |
| CreatedAt | DATETIME2 | NOT NULL | GETDATE() | Ngày tạo tài khoản |

## **4.3. Thiết kế Bảng Dimension**

### **4.3.1. DimDate — Chiều Thời gian (Shared)**

Bảng dùng chung cho tất cả tenant. Được khởi tạo trước (pre-populated) từ 2015-01-01 đến 2030-12-31. Không cần cột TenantID.

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| DateKey | INT | NOT NULL | — | PK — Khóa chính dạng số (YYYYMMDD, VD: 20240115\) |
| FullDate | DATE | NOT NULL | — | Ngày đầy đủ — UNIQUE |
| DayOfWeek | TINYINT | NOT NULL | — | Ngày trong tuần (1=Thứ 2 ... 7=Chủ nhật) |
| DayName | VARCHAR(15) | NOT NULL | — | Tên ngày (Thứ Hai, Thứ Ba, ...) |
| DayOfMonth | TINYINT | NOT NULL | — | Ngày trong tháng (1–31) |
| WeekOfYear | TINYINT | NOT NULL | — | Tuần trong năm (1–53) |
| MonthNumber | TINYINT | NOT NULL | — | Số tháng (1–12) |
| MonthName | VARCHAR(15) | NOT NULL | — | Tên tháng (Tháng 1, Tháng 2, ...) |
| Quarter | TINYINT | NOT NULL | — | Quý (1–4) |
| QuarterName | CHAR(2) | NOT NULL | — | Tên Quý (Q1, Q2, Q3, Q4) |
| Year | SMALLINT | NOT NULL | — | Năm (VD: 2024\) |
| IsWeekend | BIT | NOT NULL | 0 | Cờ cuối tuần (1=Cuối tuần) |
| IsHoliday | BIT | NOT NULL | 0 | Cờ ngày lễ/tết |
| HolidayName | NVARCHAR(100) | NULL | — | Tên ngày lễ (nếu có) |
| FiscalYear | SMALLINT | NOT NULL | — | Năm tài chính |
| FiscalQuarter | TINYINT | NOT NULL | — | Quý tài chính |

### **4.3.2. DimProduct — Chiều Sản phẩm (Shared, SCD Type 2\)**

Bảng dùng chung cho tất cả tenant. Áp dụng SCD Type 2 để theo dõi lịch sử thay đổi giá.

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| ProductKey | INT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key tự tăng |
| ProductCode | VARCHAR(50) | NOT NULL | — | Mã sản phẩm nghiệp vụ (Business Key) |
| ProductName | NVARCHAR(255) | NOT NULL | — | Tên sản phẩm đầy đủ |
| Brand | NVARCHAR(100) | NOT NULL | — | Thương hiệu (Apple, Samsung, Dell, ...) |
| CategoryName | NVARCHAR(100) | NOT NULL | — | Tên danh mục (Điện thoại, Laptop, ...) |
| SubCategory | NVARCHAR(100) | NULL | — | Danh mục con |
| UnitCostPrice | DECIMAL(18,2) | NOT NULL | — | Giá vốn tại thời điểm hiệu lực — FK cho SCD2 |
| UnitListPrice | DECIMAL(18,2) | NOT NULL | — | Giá niêm yết tại thời điểm hiệu lực |
| UnitOfMeasure | VARCHAR(20) | NOT NULL | 'cái' | Đơn vị tính |
| Warranty\_Months | TINYINT | NULL | — | Thời gian bảo hành (tháng) |
| IsActive | BIT | NOT NULL | 1 | Trạng thái kinh doanh |
| EffectiveDate | DATE | NOT NULL | — | Ngày bắt đầu hiệu lực (SCD Type 2\) |
| ExpirationDate | DATE | NULL | — | Ngày hết hiệu lực — NULL \= bản ghi hiện tại (SCD2) |
| IsCurrent | BIT | NOT NULL | 1 | Cờ bản ghi hiện tại (SCD Type 2\) |

### **4.3.3. DimCustomer — Chiều Khách hàng (Có TenantID)**

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| CustomerKey | INT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| CustomerCode | VARCHAR(50) | NOT NULL | — | Mã khách hàng từ hệ thống nguồn (BK) |
| TenantID | VARCHAR(20) | NOT NULL | — | FK → Tenants — Cửa hàng sở hữu khách hàng \[MỚI\] |
| FullName | NVARCHAR(150) | NOT NULL | — | Họ và tên đầy đủ |
| Gender | CHAR(1) | NULL | — | Giới tính (M=Nam, F=Nữ, U=Không xác định) |
| DateOfBirth | DATE | NULL | — | Ngày sinh |
| AgeGroup | VARCHAR(20) | NULL | — | Nhóm tuổi (18-24, 25-34, 35-44, ...) |
| Phone | VARCHAR(20) | NULL | — | Số điện thoại (đã ẩn bớt ký tự) |
| Email | VARCHAR(150) | NULL | — | Email (đã ẩn bớt ký tự) |
| City | NVARCHAR(100) | NULL | — | Thành phố |
| Province | NVARCHAR(100) | NULL | — | Tỉnh/Thành phố |
| CustomerType | VARCHAR(20) | NOT NULL | 'Lẻ' | Loại KH (Lẻ, Doanh nghiệp, VIP) |
| LoyaltyPoint | INT | NOT NULL | 0 | Điểm tích lũy hiện tại |
| MemberSince | DATE | NOT NULL | — | Ngày đăng ký thành viên |
| EffectiveDate | DATE | NOT NULL | GETDATE() | Ngày bắt đầu hiệu lực (SCD Type 2\) \[BỔ SUNG\] |
| ExpirationDate | DATE | NULL | — | Ngày hết hiệu lực — NULL \= bản ghi hiện tại (SCD2) \[BỔ SUNG\] |
| IsCurrent | BIT | NOT NULL | 1 | Cờ bản ghi hiện tại (SCD Type 2\) \[BỔ SUNG\] |
| IsActive | BIT | NOT NULL | 1 |        |

### **4.3.4. DimStore — Chiều Cửa hàng (Có TenantID)**

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| StoreKey | INT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| StoreCode | VARCHAR(20) | NOT NULL | — | Mã cửa hàng nghiệp vụ — UNIQUE (BK) |
| TenantID | VARCHAR(20) | NOT NULL | — | FK → Tenants — Mã tenant/chi nhánh \[MỚI\] |
| StoreName | NVARCHAR(150) | NOT NULL | — | Tên cửa hàng |
| StoreType | VARCHAR(50) | NOT NULL | — | Loại hình (Flagship, Chi nhánh, Online) |
| Address | NVARCHAR(255) | NOT NULL | — | Địa chỉ đầy đủ |
| District | NVARCHAR(100) | NOT NULL | — | Quận/Huyện |
| City | NVARCHAR(100) | NOT NULL | — | Thành phố |
| OpenDate | DATE | NOT NULL | — | Ngày khai trương |
| ManagerName | NVARCHAR(150) | NULL | — | Tên quản lý cửa hàng |
| StoreArea\_m2 | DECIMAL(8,2) | NULL | — | Diện tích mặt sàn (m²) |
| IsActive | BIT | NOT NULL | 1 | Trạng thái hoạt động |

### **4.3.5. DimEmployee — Chiều Nhân viên (Có TenantID)**

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| EmployeeKey | INT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| EmployeeCode | VARCHAR(20) | NOT NULL | — | Mã nhân viên (BK) |
| TenantID | VARCHAR(20) | NOT NULL | — | FK → Tenants — Mã tenant/cửa hàng \[MỚI\] |
| FullName | NVARCHAR(150) | NOT NULL | — | Họ và tên |
| Department | NVARCHAR(100) | NOT NULL | — | Phòng/Bộ phận |
| Position | NVARCHAR(100) | NOT NULL | — | Chức vụ (Nhân viên bán hàng, Trưởng ca, ...) |
| StoreKey | INT | NOT NULL | — | FK → DimStore — Cửa hàng phụ trách |
| HireDate | DATE | NOT NULL | — | Ngày vào làm |
| IsActive | BIT | NOT NULL | 1 | Trạng thái làm việc |

### **4.3.6. DimSupplier — Chiều Nhà cung cấp (Shared)**

Bảng dùng chung cho tất cả tenant. Nhà cung cấp thường là đối tác cấp toàn chuỗi.

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| SupplierKey | INT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| SupplierCode | VARCHAR(50) | NOT NULL | — | Mã nhà cung cấp — UNIQUE (BK) |
| SupplierName | NVARCHAR(200) | NOT NULL | — | Tên nhà cung cấp/nhà phân phối |
| Country | NVARCHAR(100) | NOT NULL | — | Quốc gia |
| ContactPerson | NVARCHAR(150) | NULL | — | Người liên hệ chính |
| Phone | VARCHAR(30) | NULL | — | Số điện thoại |
| Email | VARCHAR(150) | NULL | — | Email liên hệ |
| PaymentTerm\_Days | TINYINT | NULL | — | Điều khoản thanh toán (số ngày) |
| IsActive | BIT | NOT NULL | 1 | Trạng thái |

## **4.4. Thiết kế Bảng Fact**

### **4.4.1. FactSales — Sự kiện Bán hàng (Grain: 1 dòng \= 1 sản phẩm / 1 hóa đơn)**

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| SalesKey | BIGINT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| TenantID | VARCHAR(20) | NOT NULL | — | FK → Tenants — Row-Level isolation \[MỚI\] |
| DateKey | INT | NOT NULL | — | FK → DimDate |
| ProductKey | INT | NOT NULL | — | FK → DimProduct (IsCurrent=1) |
| CustomerKey | INT | NOT NULL | — | FK → DimCustomer (-1 \= Unknown) |
| StoreKey | INT | NOT NULL | — | FK → DimStore |
| EmployeeKey | INT | NOT NULL | — | FK → DimEmployee (-1 \= Unknown) |
| InvoiceNumber | VARCHAR(50) | NOT NULL | — | Số hóa đơn (Degenerate Dimension) |
| Quantity | SMALLINT | NOT NULL | — | Số lượng bán — CHECK \> 0 |
| UnitPrice | DECIMAL(18,2) | NOT NULL | — | Đơn giá thực tế bán |
| DiscountAmount | DECIMAL(18,2) | NOT NULL | 0 | Số tiền chiết khấu |
| GrossSalesAmount | DECIMAL(18,2) | NOT NULL | — | Doanh thu gộp (Qty × UnitPrice) |
| NetSalesAmount | DECIMAL(18,2) | NOT NULL | — | Doanh thu thuần (Gross \- Discount) |
| CostAmount | DECIMAL(18,2) | NOT NULL | — | Giá vốn (Qty × UnitCostPrice) |
| GrossProfitAmount | DECIMAL(18,2) | NOT NULL | — | Lợi nhuận gộp (Net \- Cost) |
| TaxAmount | DECIMAL(18,2) | NOT NULL | 0 | Thuế VAT |
| PaymentMethod | VARCHAR(30) | NOT NULL | — | Phương thức thanh toán (Tiền mặt, Chuyển khoản, ...) |
| SalesChannel | VARCHAR(20) | NOT NULL | 'InStore' | Kênh bán (InStore, Online) |
| ReturnFlag | BIT | NOT NULL | 0 | Cờ giao dịch hoàn trả (1=Hoàn trả) |
| LoadDatetime | DATETIME2 | NOT NULL | GETDATE() | Thời điểm nạp vào DWH |

### **4.4.2. FactInventory — Sự kiện Tồn kho (Grain: 1 sản phẩm / 1 cửa hàng / 1 ngày)**

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| InventoryKey | BIGINT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| TenantID | VARCHAR(20) | NOT NULL | — | FK → Tenants \[MỚI\] |
| DateKey | INT | NOT NULL | — | FK → DimDate — Ngày chụp ảnh tồn kho |
| ProductKey | INT | NOT NULL | — | FK → DimProduct |
| StoreKey | INT | NOT NULL | — | FK → DimStore |
| SupplierKey | INT | NULL | — | FK → DimSupplier — Nhà cung cấp chính |
| OpeningStock | INT | NOT NULL | 0 | Tồn đầu ngày |
| ClosingStock | INT | NOT NULL | 0 | Tồn cuối ngày |
| StockReceived | INT | NOT NULL | 0 | Số lượng nhập trong ngày |
| StockSold | INT | NOT NULL | 0 | Số lượng bán trong ngày |
| StockAdjusted | INT | NOT NULL | 0 | Điều chỉnh tồn kho (mất mát, hỏng, ...) |
| ReorderPoint | INT | NULL | — | Mức tồn kho tối thiểu (trigger đặt hàng) |
| UnitCost | DECIMAL(18,2) | NOT NULL | — | Giá vốn tại thời điểm chụp |
| TotalInventoryValue | DECIMAL(18,2) | NOT NULL | — | Giá trị tồn (ClosingStock × UnitCost) |
| LoadDatetime | DATETIME2 | NOT NULL | GETDATE() | Thời điểm nạp |

### **4.4.3. FactPurchase — Sự kiện Nhập hàng**

| Tên Cột | Kiểu DL | Nullable | Mặc định | Mô tả |
| :---- | :---- | :---- | :---- | :---- |
| PurchaseKey | BIGINT IDENTITY | NOT NULL | AUTO | PK — Surrogate Key |
| TenantID | VARCHAR(20) | NOT NULL | — | FK → Tenants \[MỚI\] |
| DateKey | INT | NOT NULL | — | FK → DimDate — Ngày nhập hàng |
| ProductKey | INT | NOT NULL | — | FK → DimProduct |
| SupplierKey | INT | NOT NULL | — | FK → DimSupplier |
| StoreKey | INT | NOT NULL | — | FK → DimStore — Kho nhận hàng |
| PurchaseOrderNo | VARCHAR(50) | NOT NULL | — | Số phiếu đặt hàng (Degenerate Dimension) |
| QuantityOrdered | INT | NOT NULL | — | Số lượng đặt |
| QuantityReceived | INT | NOT NULL | — | Số lượng thực nhận |
| UnitPurchasePrice | DECIMAL(18,2) | NOT NULL | — | Đơn giá nhập |
| TotalPurchaseAmount | DECIMAL(18,2) | NOT NULL | — | Tổng giá trị nhập |
| LeadTime\_Days | SMALLINT | NULL | — | Thời gian giao hàng thực tế (ngày) |
| LoadDatetime | DATETIME2 | NOT NULL | GETDATE() | Thời điểm nạp |

## **4.5. Bảng Staging Layer (STG\_\*)**

Các bảng Staging là vùng đệm tạm thời, được truncate và reload mỗi chu kỳ ETL. Cấu trúc phản chiếu nguồn dữ liệu nhưng đã thêm cột TenantID và cột kiểm soát.

| Bảng Staging | Nguồn dữ liệu | Cột đặc biệt | Mô tả |
| :---- | :---- | :---- | :---- |
| STG\_SalesRaw | File Excel/CSV POS | TenantID, STG\_LoadDatetime | Dữ liệu bán hàng thô chưa biến đổi |
| STG\_InventoryRaw | File Excel/Google Sheets Kho | TenantID, STG\_LoadDatetime | Dữ liệu tồn kho thô |
| STG\_PurchaseRaw | File Excel đặt hàng | TenantID, STG\_LoadDatetime | Dữ liệu nhập hàng thô |
| STG\_ProductRaw | File CSV danh mục | STG\_LoadDatetime (Shared) | Danh mục sản phẩm — không cần TenantID |
| STG\_ErrorLog | Tất cả nguồn | TenantID, ErrorType, RawData | Ghi nhận bản ghi lỗi trong quá trình Transform |

## **4.6. Data Mart Layer (DM\_\*) \[MỚI\]**

Các Data Mart là Aggregate Table và View được tính toán sẵn, tối ưu hiệu năng cho Dashboard. Superset kết nối vào Data Mart thay vì truy vấn trực tiếp bảng Fact.

| View / Table | Loại | Cột chính | Phục vụ Dashboard |
| :---- | :---- | :---- | :---- |
| DM\_SalesSummary | Aggregate Table | TenantID, DateKey, StoreKey, TotalRevenue, TotalProfit | Dashboard Doanh thu |
| DM\_ProductPerformance | Aggregate View | TenantID, ProductKey, TotalQty, TotalRevenue, Rank | Dashboard Sản phẩm |
| DM\_InventoryAlert | Aggregate View | TenantID, StoreKey, ProductKey, ClosingStock, ReorderPoint | Dashboard Tồn kho |
| DM\_CustomerRFM | Aggregate Table | TenantID, CustomerKey, Recency, Frequency, Monetary, Segment | Dashboard Khách hàng |
| DM\_EmployeePerformance | Aggregate View | TenantID, EmployeeKey, TotalSales, ConversionRate | Dashboard Nhân viên |

\-- Ví dụ: Script tạo DM\_SalesSummary

CREATE TABLE DM\_SalesSummary (

    SummaryKey       BIGINT IDENTITY PRIMARY KEY,

    TenantID         VARCHAR(20)    NOT NULL,

    DateKey          INT            NOT NULL,

    StoreKey         INT            NOT NULL,

    CategoryName     NVARCHAR(100)  NOT NULL,

    TotalRevenue     DECIMAL(18,2)  NOT NULL DEFAULT 0,

    TotalProfit      DECIMAL(18,2)  NOT NULL DEFAULT 0,

    TotalOrders      INT            NOT NULL DEFAULT 0,

    TotalQty         INT            NOT NULL DEFAULT 0,

    LastRefreshed    DATETIME2      NOT NULL DEFAULT GETDATE()

);

\-- Stored Procedure refresh DM\_SalesSummary theo tenant

CREATE OR ALTER PROCEDURE usp\_Refresh\_DM\_SalesSummary

    @TenantID VARCHAR(20)

AS BEGIN

    DELETE FROM DM\_SalesSummary WHERE TenantID \= @TenantID;

    INSERT INTO DM\_SalesSummary (TenantID, DateKey, StoreKey, CategoryName,

                                  TotalRevenue, TotalProfit, TotalOrders, TotalQty)

    SELECT f.TenantID, f.DateKey, f.StoreKey, p.CategoryName,

           SUM(f.NetSalesAmount), SUM(f.GrossProfitAmount),

           COUNT(DISTINCT f.InvoiceNumber), SUM(f.Quantity)

    FROM FactSales f

    INNER JOIN DimProduct p ON p.ProductKey \= f.ProductKey AND p.IsCurrent \= 1

    WHERE f.TenantID \= @TenantID

    GROUP BY f.TenantID, f.DateKey, f.StoreKey, p.CategoryName;

END;

## **4.7. Script SQL — Tạo Cấu trúc Multi-Tenant \[MỚI\]**

\-- \============================================================

\-- BƯỚC 1: Tạo bảng Tenants và AppUsers

\-- \============================================================

CREATE TABLE Tenants (

    TenantID     VARCHAR(20)    PRIMARY KEY,

    TenantName   NVARCHAR(200)  NOT NULL,

    FilePath     NVARCHAR(500)  NULL,

    IsActive     BIT            NOT NULL DEFAULT 1,

    CreatedAt    DATETIME2      NOT NULL DEFAULT GETDATE()

);

CREATE TABLE AppUsers (

    UserID       INT IDENTITY   PRIMARY KEY,

    Username     VARCHAR(100)   NOT NULL UNIQUE,

    PasswordHash VARCHAR(255)   NOT NULL,

    TenantID     VARCHAR(20)    NULL REFERENCES Tenants(TenantID),

    Role         VARCHAR(20)    NOT NULL DEFAULT 'viewer'

                               CHECK (Role IN ('admin','viewer')),

    IsActive     BIT            NOT NULL DEFAULT 1,

    CreatedAt    DATETIME2      NOT NULL DEFAULT GETDATE()

);

\-- BƯỚC 2: Thêm cột TenantID vào bảng Fact/Dimension (đã sửa theo 3 bước)

\-- BƯỚC 2a: Thêm cột TenantID (cho phép NULL tạm thời)

ALTER TABLE FactSales      ADD TenantID VARCHAR(20) NULL;

ALTER TABLE FactInventory  ADD TenantID VARCHAR(20) NULL;

ALTER TABLE FactPurchase   ADD TenantID VARCHAR(20) NULL;

ALTER TABLE STG\_SalesRaw   ADD TenantID VARCHAR(20) NULL;

ALTER TABLE STG\_InventoryRaw ADD TenantID VARCHAR(20) NULL;

ALTER TABLE DimStore       ADD TenantID VARCHAR(20) NULL;

ALTER TABLE DimCustomer    ADD TenantID VARCHAR(20) NULL;

ALTER TABLE DimEmployee    ADD TenantID VARCHAR(20) NULL;

\-- BƯỚC 2b: Gán TenantID cho dữ liệu hiện có (ví dụ tenant STORE\_HN)

UPDATE FactSales     SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE FactInventory SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE FactPurchase  SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE STG\_SalesRaw  SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE STG\_InventoryRaw SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE DimStore      SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE DimCustomer   SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

UPDATE DimEmployee   SET TenantID \= 'STORE\_HN' WHERE TenantID IS NULL;

\-- BƯỚC 2c: Đổi sang NOT NULL và thêm FK constraint

ALTER TABLE FactSales    ALTER COLUMN TenantID VARCHAR(20) NOT NULL;

ALTER TABLE FactInventory ALTER COLUMN TenantID VARCHAR(20) NOT NULL;

ALTER TABLE FactPurchase  ALTER COLUMN TenantID VARCHAR(20) NOT NULL;

ALTER TABLE DimStore     ALTER COLUMN TenantID VARCHAR(20) NOT NULL;

ALTER TABLE DimCustomer  ALTER COLUMN TenantID VARCHAR(20) NOT NULL;

ALTER TABLE DimEmployee  ALTER COLUMN TenantID VARCHAR(20) NOT NULL;

ALTER TABLE FactSales    ADD CONSTRAINT FK\_FactSales\_Tenant    FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID);

ALTER TABLE FactInventory ADD CONSTRAINT FK\_FactInventory\_Tenant FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID);

ALTER TABLE FactPurchase  ADD CONSTRAINT FK\_FactPurchase\_Tenant  FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID);

ALTER TABLE DimStore     ADD CONSTRAINT FK\_DimStore\_Tenant     FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID);

ALTER TABLE DimCustomer  ADD CONSTRAINT FK\_DimCustomer\_Tenant  FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID);

ALTER TABLE DimEmployee  ADD CONSTRAINT FK\_DimEmployee\_Tenant  FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID);

\-- BƯỚC 3: Thêm Index tối ưu query theo TenantID

CREATE INDEX IX\_FactSales\_TenantID      ON FactSales(TenantID, DateKey);

CREATE INDEX IX\_FactInventory\_TenantID  ON FactInventory(TenantID, DateKey);

CREATE INDEX IX\_FactPurchase\_TenantID   ON FactPurchase(TenantID, DateKey);

CREATE INDEX IX\_DimProduct\_ProductCode  ON DimProduct(ProductCode) WHERE IsCurrent \= 1;

CREATE INDEX IX\_DimCustomer\_TenantCode  ON DimCustomer(TenantID, CustomerCode) WHERE IsCurrent \= 1;

CREATE INDEX IX\_DimEmployee\_TenantCode  ON DimEmployee(TenantID, EmployeeCode);

CREATE INDEX IX\_DimStore\_TenantCode     ON DimStore(TenantID, StoreCode);

CREATE INDEX IX\_DimSupplier\_Code        ON DimSupplier(SupplierCode);

\-- BƯỚC 4: Tạo View filter tự động theo SESSION\_CONTEXT (đã thêm wrapper)

\-- 1\. Tạo View (giữ nguyên)

CREATE VIEW v\_FactSales\_ByTenant AS

    SELECT \* FROM FactSales

    WHERE TenantID \= ISNULL(CAST(SESSION\_CONTEXT(N'tenant\_id') AS VARCHAR(20)), '\#\#INVALID\#\#');  \-- \[DA SUA\] Neu SESSION\_CONTEXT chua set \=\> tra 0 dong, khong loi am tham

GO

\-- 2\. Stored Procedure wrapper: set context trước khi truy vấn

CREATE OR ALTER PROCEDURE usp\_SetTenantContext

    @TenantID VARCHAR(20)

AS BEGIN

    IF NOT EXISTS (SELECT 1 FROM Tenants WHERE TenantID \= @TenantID AND IsActive \= 1\)

    BEGIN

        RAISERROR('Tenant khong hop le hoac khong hoat dong.', 16, 1); RETURN;

    END;

    EXEC sp\_set\_session\_context N'tenant\_id', @TenantID, @read\_only \= 1;

END;

GO

\-- 3\. Vi du su dung: EXEC usp\_SetTenantContext 'STORE\_HN';

\--                   SELECT \* FROM v\_FactSales\_ByTenant WHERE DateKey \= 20240115;

\-- 4\. Luu y: SESSION\_CONTEXT reset khi ket thuc connection; goi ngay sau khi mo connection.

\-- BƯỚC 5: Insert dữ liệu mẫu ban đầu

INSERT INTO Tenants VALUES ('STORE\_HN',  N'Cửa hàng Hà Nội',  './data/hn/',  1, GETDATE());

INSERT INTO Tenants VALUES ('STORE\_HCM', N'Cửa hàng HCM',     './data/hcm/', 1, GETDATE());

### **4.8. Bổ sung DDL — STG\_CustomerRaw \[BỔ SUNG\]**

Bảng STG\_CustomerRaw bị thiếu DDL trong thiết kế gốc nhưng được sử dụng trong usp\_Load\_DimCustomer. Script dưới đây là bắt buộc để SP chạy không lỗi:

\-- \[BỔ SUNG\] Bảng Staging cho dữ liệu khách hàng thô

CREATE TABLE STG\_CustomerRaw (

    STGCustomerID    INT IDENTITY(1,1) PRIMARY KEY,

    TenantID         VARCHAR(20)   NOT NULL,

    MaKH             VARCHAR(50)   NOT NULL,

    HoTen            NVARCHAR(150) NOT NULL,

    GioiTinh         CHAR(1)       NULL,

    NgaySinh         DATE          NULL,

    ThanhPho         NVARCHAR(100) NULL,

    TinhTP           NVARCHAR(100) NULL,

    SoDienThoai      VARCHAR(20)   NULL,

    Email            VARCHAR(150)  NULL,

    LoaiKH           VARCHAR(20)   NOT NULL DEFAULT 'Le',

    DiemTichLuy      INT           NULL DEFAULT 0,

    NgayDangKy       DATE          NOT NULL,

    IsActive         BIT           NOT NULL DEFAULT 1,

    STG\_LoadDatetime DATETIME2     NOT NULL DEFAULT GETDATE()

);

CREATE INDEX IX\_STG\_Customer\_TenantMa ON STG\_CustomerRaw(TenantID, MaKH);

### **4.9. Bổ sung DDL — ETLLogs / ETL\_RunLog \[BỔ SUNG\]**

Bảng ETLLogs được tham chiếu trong mục 5.5 ('ghi ETL\_RunLog') và trong code orchestrator nhưng không có DDL. Script dưới đây tạo bảng log đầy đủ:

\-- \[BỔ SUNG\] Bảng ghi lich su moi lan chay ETL

CREATE TABLE ETLLogs (

    LogID            INT IDENTITY(1,1) PRIMARY KEY,

    TenantID         VARCHAR(20)   NOT NULL REFERENCES Tenants(TenantID),

    BatchDate        DATE          NOT NULL,

    SourceTable      VARCHAR(100)  NOT NULL,   \-- VD: 'FactSales', 'DimCustomer'

    RunStatus        VARCHAR(20)   NOT NULL

                     CHECK (RunStatus IN ('SUCCESS','FAILED','RUNNING')),

    RowsExtracted    INT           NULL,       \-- So ban ghi doc tu nguon

    RowsInserted     INT           NULL,       \-- So ban ghi insert thanh cong

    RowsRejected     INT           NULL,       \-- So ban ghi loi / bi tu choi

    StartTime        DATETIME2     NOT NULL DEFAULT GETDATE(),

    EndTime          DATETIME2     NULL,

    DurationSeconds  AS DATEDIFF(SECOND, StartTime, EndTime),  \-- Computed column

    ErrorMessage     NVARCHAR(MAX) NULL,

    CreatedAt        DATETIME2     NOT NULL DEFAULT GETDATE()

);

CREATE INDEX IX\_ETLLogs\_Tenant\_Date ON ETLLogs(TenantID, BatchDate);

CREATE INDEX IX\_ETLLogs\_Status      ON ETLLogs(RunStatus, StartTime);

### **4.10. Bổ sung Index cho DM\_SalesSummary \[BỔ SUNG\]**

Script tạo DM\_SalesSummary trong mục 4.6 chỉ có PRIMARY KEY. Dashboard query theo TenantID \+ DateKey sẽ full scan khi data lớn. Thêm index sau khi tạo bảng:

\-- \[BỔ SUNG\] Index cho DM layer \-- can thiet de dashboard dat NFR-01 (\<= 3s)

CREATE INDEX IX\_DM\_Sales\_Tenant\_Date

    ON DM\_SalesSummary(TenantID, DateKey);

CREATE INDEX IX\_DM\_Sales\_Store

    ON DM\_SalesSummary(TenantID, StoreKey, DateKey);

\-- Index tuong tu cho cac DM khac

CREATE INDEX IX\_DM\_CustRFM\_Tenant

    ON DM\_CustomerRFM(TenantID, Segment);

### **4.11. Bổ sung Unique Index SCD2 cho DimCustomer \[BỔ SUNG\]**

Đảm bảo mỗi (TenantID, CustomerCode) chỉ có đúng 1 bản ghi IsCurrent=1, tránh SP lookup trả về nhiều dòng:

\-- \[BỔ SUNG\] Filtered unique index: moi khach hang chi co 1 ban ghi hien tai

CREATE UNIQUE INDEX UQ\_DimCustomer\_Current

    ON DimCustomer(TenantID, CustomerCode)

    WHERE IsCurrent \= 1;

\-- Tuong tu cho DimProduct (Shared \-- khong co TenantID)

CREATE UNIQUE INDEX UQ\_DimProduct\_Current

    ON DimProduct(ProductCode)

    WHERE IsCurrent \= 1;

# **CHƯƠNG 5: THIẾT KẾ TIẾN TRÌNH ETL**

## **5.1. Tổng quan Quy trình ETL**

Quy trình ETL (Extract – Transform – Load) là xương sống của hệ thống Data Warehouse. Với multi-tenant, pipeline ETL chạy vòng lặp qua danh sách tenant đang hoạt động, tag tenant\_id vào mọi bản ghi trước khi nạp.

| 📌 Chiến lược ETL Multi-Tenant • Tần suất chạy: Hàng ngày lúc 02:00 SA (giờ thấp điểm). • Incremental Load: Mỗi tenant có watermark riêng — SourceName \= '{TenantID}\_Sales\_Excel'. Watermark được cập nhật bằng cách ghi GETDATE() vào ETL\_Watermark sau khi ETL SUCCESS. • Tenant isolation: ETL gắn TenantID vào mọi DataFrame trước khi load\_to\_staging(). • Xử lý lỗi: Bản ghi không tìm thấy dimension → ghi vào STG\_ErrorLog kèm TenantID, tiếp tục xử lý bản ghi hợp lệ. • Idempotency: Kiểm tra NOT EXISTS trước INSERT — có thể chạy lại mà không sinh dữ liệu trùng. • Monitoring: Sau mỗi lần chạy, nếu status \= FAILED → gửi alert email/Slack ngay lập tức. |
| :---- |

## **5.2. Bước 1 — EXTRACT**

### **5.2.1. Module Extract (Có tenant\_id tagging)**

\# etl/extract/extract\_sales.py

import pandas as pd, pyodbc, logging

from datetime import datetime

def get\_last\_watermark(conn, tenant\_id: str, source\_type: str) \-\> datetime:

    """Lay moc thoi gian ETL thanh cong cuoi cung cua tenant."""

    source\_name \= f'{tenant\_id}\_{source\_type}'

    cursor \= conn.cursor()

    cursor.execute(

        'SELECT MAX(WatermarkValue) FROM ETL\_Watermark

         WHERE SourceName \= ? AND LastRunStatus \= ?',

        (source\_name, 'SUCCESS')

    )

    row \= cursor.fetchone()

    return row\[0\] if row\[0\] else datetime(2020, 1, 1\)

def extract\_sales\_from\_excel(file\_path, watermark, tenant\_id) \-\> pd.DataFrame:

    """Doc Excel, loc theo watermark, gan tenant\_id."""

    df \= pd.read\_excel(file\_path, sheet\_name='DanhSachHoaDon',

                       dtype={'MaHoaDon': str, 'MaSP': str, 'MaKH': str})

    df.columns \= df.columns.str.strip()

    df\['NgayBan'\] \= pd.to\_datetime(df\['NgayBan'\], dayfirst=True)

    df \= df\[df\['NgayBan'\] \> pd.Timestamp(watermark)\]

    df\['TenantID'\] \= tenant\_id              \# TAG TENANT\_ID

    df\['STG\_LoadDatetime'\] \= pd.Timestamp.now()

    logging.info(f'\[{tenant\_id}\] Extracted {len(df)} rows from sales')

    return df

### **5.2.2. Cơ chế Watermark Incremental Extraction**

Watermark đảm bảo mỗi lần ETL chỉ xử lý dữ liệu mới kể từ lần chạy thành công trước. Cơ chế cập nhật:

* Trước khi chạy: đặt LastRunStatus \= 'RUNNING'.

* Sau khi thành công: UPDATE WatermarkValue \= GETDATE(), LastRunStatus \= 'SUCCESS'.

* Nếu thất bại: UPDATE LastRunStatus \= 'FAILED' — giữ nguyên WatermarkValue để lần sau retry từ cùng điểm.

  \-- Bảng ETL\_Watermark (cập nhật \-- có TenantID)

  CREATE TABLE ETL\_Watermark (

      WatermarkID  INT IDENTITY(1,1) PRIMARY KEY,

      TenantID     VARCHAR(20) NOT NULL REFERENCES Tenants(TenantID),  \-- FK ro rang \[DA SUA\]

      TableName    VARCHAR(100) NOT NULL,  \-- Doi ten: ro hon SourceName \[DA SUA\]

      LastRunTime  DATETIME2 NULL,         \-- Thoi diem ETL thanh cong cuoi cung

      LastRunStatus VARCHAR(20) NOT NULL DEFAULT 'PENDING'

          CHECK (LastRunStatus IN ('PENDING','RUNNING','SUCCESS','FAILED')),  \-- \[DA SUA\]

      UpdatedAt    DATETIME2 NOT NULL DEFAULT GETDATE(),

      CONSTRAINT UQ\_ETL\_Watermark UNIQUE (TenantID, TableName)  \-- \[DA SUA\]

  );

  CREATE INDEX IX\_ETL\_Watermark\_Tenant ON ETL\_Watermark(TenantID, TableName);

  \-- \[DA SUA\] Cac cot RowsExtracted, Notes, RowsInserted da duoc gop vao CREATE TABLE ETL\_RunLog o muc 7.4 ben duoi.

  );

## **5.3. Bước 2 — TRANSFORM**

### **5.3.1. Danh mục các Phép biến đổi**

| Loại biến đổi | Mô tả | Công cụ | Ví dụ |
| :---- | :---- | :---- | :---- |
| Chuẩn hóa kiểu DL | Chuyển đổi kiểu dữ liệu về chuẩn DWH | Python (pandas) | String '15/01/2024' → DATE 2024-01-15 |
| Làm sạch chuỗi | Loại bỏ khoảng trắng thừa, chuẩn hóa HOA/thường | Python (str.strip, upper) |  ' iphone 15 ' → 'IPHONE 15' |
| Xử lý NULL | Điền giá trị mặc định hoặc ghi vào ErrorLog | Python / T-SQL ISNULL() | NULL → 'Unknown', NULL → 0 |
| Loại trùng lặp | Giữ bản ghi mới nhất theo business key | Python (drop\_duplicates) | Nhiều dòng cùng MaHoaDon+MaSP → giữ 1 |
| Tra cứu Surrogate Key | Ánh xạ business key → surrogate key DWH | T-SQL Stored Procedure | MaSP='SP001' → ProductKey=45 |
| Tính cột phái sinh | Tính các chỉ số từ cột gốc | Python / T-SQL | GrossProfit \= NetSales \- CostAmount |
| Kiểm tra tham chiếu | Đảm bảo FK hợp lệ trước khi INSERT vào Fact | T-SQL NOT EXISTS | DateKey phải tồn tại trong DimDate |
| Tag TenantID \[MỚI\] | Gắn tenant\_id vào mọi bản ghi từ bước Extract | Python (df\['TenantID'\]) | Mọi bản ghi Tenant A → TenantID='STORE\_HN' |
| Kiểm tra ngưỡng | Phát hiện giá trị bất thường | Python assert / log | Quantity ≤ 0 hoặc UnitPrice \< 0 → lỗi |

### **5.3.2. Code Python — Transform DataFrame trước khi Load**

\# etl/transform/transform\_sales.py

import pandas as pd, logging

def transform\_sales(df: pd.DataFrame, tenant\_id: str) \-\> pd.DataFrame:

    """Bien doi va lam sach DataFrame ban hang cua 1 tenant."""

    \# 1\. Chuan hoa kieu du lieu

    df\['NgayBan'\]  \= pd.to\_datetime(df\['NgayBan'\], dayfirst=True, errors='coerce')

    df\['SoLuong'\]  \= pd.to\_numeric(df\['SoLuong'\], errors='coerce').fillna(0).astype(int)

    df\['DonGiaBan'\]= pd.to\_numeric(df\['DonGiaBan'\], errors='coerce').fillna(0)

    \# 2\. Lam sach chuoi

    df\['MaHoaDon'\] \= df\['MaHoaDon'\].str.strip().str.upper()

    df\['MaSP'\]     \= df\['MaSP'\].str.strip().str.upper()

    df\['MaKH'\]     \= df\['MaKH'\].str.strip().str.upper().fillna('UNKNOWN')

    \# 3\. Xu ly NULL

    df\['ChietKhau'\] \= df.get('ChietKhau', 0).fillna(0)

    df\['KenhBan'\]   \= df.get('KenhBan', 'InStore').fillna('InStore')

    \# 4\. Loai trung lap

    before \= len(df)

    df \= df.drop\_duplicates(subset=\['MaHoaDon','MaSP'\], keep='last')

    logging.info(f'\[{tenant\_id}\] Dropped {before \- len(df)} duplicates')

    \# 5\. Kiem tra nguong bat thuong

    invalid \= df\[(df\['SoLuong'\] \<= 0\) | (df\['DonGiaBan'\] \< 0)\]

    if len(invalid) \> 0:

        logging.warning(f'\[{tenant\_id}\] {len(invalid)} invalid rows (qty\<=0 or price\<0)')

    df \= df\[(df\['SoLuong'\] \> 0\) & (df\['DonGiaBan'\] \>= 0)\]

    \# 6\. Tinh cot phai sinh

    df\['GrossSalesAmount'\] \= df\['SoLuong'\] \* df\['DonGiaBan'\]

    df\['NetSalesAmount'\]   \= df\['GrossSalesAmount'\] \- df\['ChietKhau'\]

    return df

### **5.3.3. Stored Procedure — usp\_Transform\_FactSales (Cập nhật)**

CREATE OR ALTER PROCEDURE usp\_Transform\_FactSales

    @BatchDate DATE     \= NULL,

    @TenantID  VARCHAR(20)

AS BEGIN

    SET NOCOUNT ON;

    \-- \[BỔ SUNG\] Transaction dam bao atomic: neu loi giua chung, rollback toan bo

    BEGIN TRY

    BEGIN TRANSACTION;

    IF @BatchDate IS NULL SET @BatchDate \= CAST(GETDATE() AS DATE);

    \-- Ghi nhan ban ghi loi (khong tim thay Dimension)

    INSERT INTO STG\_ErrorLog (TenantID, SourceTable, ErrorType, RawData, LoadDatetime)

    SELECT @TenantID,'STG\_SalesRaw','DIMENSION\_NOT\_FOUND',

           CONCAT('MaSP=',s.MaSP,',MaKH=',s.MaKH), GETDATE()

    FROM STG\_SalesRaw s

    WHERE s.TenantID \= @TenantID AND CAST(s.NgayBan AS DATE) \= @BatchDate

      AND NOT EXISTS(SELECT 1 FROM DimProduct p

                     WHERE p.ProductCode \= s.MaSP AND p.IsCurrent \= 1);

    \-- Nap du lieu hop le vao FactSales

    INSERT INTO FactSales (TenantID,DateKey,ProductKey,CustomerKey,

        StoreKey,EmployeeKey,InvoiceNumber,Quantity,UnitPrice,DiscountAmount,

        GrossSalesAmount,NetSalesAmount,CostAmount,GrossProfitAmount,

        TaxAmount,

        PaymentMethod,SalesChannel,ReturnFlag,LoadDatetime)

    SELECT @TenantID,

        CONVERT(INT,FORMAT(s.NgayBan,'yyyyMMdd')),

        p.ProductKey, ISNULL(c.CustomerKey,-1), st.StoreKey, ISNULL(e.EmployeeKey,-1),

        UPPER(LTRIM(RTRIM(s.MaHoaDon))),

        s.SoLuong, s.DonGiaBan, ISNULL(s.ChietKhau,0),

        s.SoLuong\*s.DonGiaBan,

        (s.SoLuong\*s.DonGiaBan)-ISNULL(s.ChietKhau,0),

        s.SoLuong\*p.UnitCostPrice,

        (s.SoLuong\*s.DonGiaBan)-ISNULL(s.ChietKhau,0)-(s.SoLuong\*p.UnitCostPrice),

        ISNULL(s.ThueTVGT, 0),  \-- TaxAmount

        ISNULL(s.PhuongThucTT,'Tien mat'), ISNULL(s.KenhBan,'InStore'),

        ISNULL(s.IsHoanTra,0), GETDATE()

    FROM STG\_SalesRaw s

    INNER JOIN DimProduct  p  ON p.ProductCode  \= s.MaSP AND p.IsCurrent \= 1

    INNER JOIN DimStore    st ON st.StoreCode   \= s.MaCH AND st.TenantID  \= @TenantID

    LEFT  JOIN DimCustomer c  ON c.CustomerCode \= s.MaKH AND c.TenantID   \= @TenantID

    LEFT  JOIN DimEmployee e  ON e.EmployeeCode \= s.MaNV AND e.TenantID   \= @TenantID

    WHERE s.TenantID \= @TenantID AND CAST(s.NgayBan AS DATE) \= @BatchDate

      AND NOT EXISTS(SELECT 1 FROM FactSales f

                     WHERE f.InvoiceNumber \= UPPER(LTRIM(RTRIM(s.MaHoaDon)))

                       AND f.TenantID \= @TenantID AND f.ProductKey \= p.ProductKey);

    COMMIT TRANSACTION;

    END TRY

    BEGIN CATCH

        IF @@TRANCOUNT \> 0 ROLLBACK TRANSACTION;  \-- \[BỔ SUNG\]

        THROW;  \-- Re-raise loi de ETL Orchestrator bat duoc

    END CATCH;

END;

## **5.4. Bước 3 — LOAD: ETL Orchestrator**

\# etl/orchestrator/main\_etl.py

import logging, pyodbc, smtplib

from datetime import date

from email.mime.text import MIMEText

def send\_alert(subject, body):

    """Gui email alert khi ETL that bai."""

    msg \= MIMEText(body)

    msg\['Subject'\] \= subject

    msg\['From'\]    \= 'etl@company.com'

    msg\['To'\]      \= 'admin@company.com'

    with smtplib.SMTP('smtp.gmail.com', 587\) as s:

        s.starttls()

        s.login('etl@company.com', SMTP\_PASSWORD)

        s.send\_message(msg)

def run\_etl\_for\_tenant(tenant\_id, file\_path):

    batch\_date \= date.today().strftime('%Y-%m-%d')

    logging.info(f'===== ETL Tenant: {tenant\_id} | {batch\_date} \=====')

    conn \= pyodbc.connect(CONN\_STR, autocommit=False)

    try:

        \# PHASE 1: EXTRACT

        run\_sp(conn,'usp\_Update\_Watermark',{'SourceName':f'{tenant\_id}\_Sales\_Excel','Status':'RUNNING'})

        wm      \= get\_last\_watermark(conn, tenant\_id, 'Sales\_Excel')

        df      \= extract\_sales\_from\_excel(file\_path, wm, tenant\_id)

        df      \= transform\_sales(df, tenant\_id)

        load\_to\_staging(df, conn, 'STG\_SalesRaw')

        \# PHASE 2: LOAD DIMENSIONS

        run\_sp(conn, 'usp\_Load\_DimProduct')  \# Shared

        run\_sp(conn, 'usp\_Load\_DimCustomer', {'TenantID': tenant\_id})

        run\_sp(conn, 'usp\_Load\_DimStore',    {'TenantID': tenant\_id})

        run\_sp(conn, 'usp\_Load\_DimEmployee', {'TenantID': tenant\_id})

        \# PHASE 3: LOAD FACTS

        run\_sp(conn,'usp\_Transform\_FactSales',    {'BatchDate':batch\_date,'TenantID':tenant\_id})

        run\_sp(conn,'usp\_Transform\_FactInventory',{'BatchDate':batch\_date,'TenantID':tenant\_id})

        run\_sp(conn,'usp\_Transform\_FactPurchase', {'BatchDate':batch\_date,'TenantID':tenant\_id})

        \# PHASE 4: REFRESH DATA MART

        run\_sp(conn,'usp\_Refresh\_DM\_SalesSummary',    {'TenantID':tenant\_id})

        run\_sp(conn,'usp\_Refresh\_DM\_InventoryAlert',  {'TenantID':tenant\_id})

        run\_sp(conn,'usp\_Refresh\_DM\_CustomerRFM',     {'TenantID':tenant\_id})

        \# PHASE 5: UPDATE WATERMARK

        run\_sp(conn,'usp\_Update\_Watermark',{'SourceName':f'{tenant\_id}\_Sales\_Excel','Status':'SUCCESS'})

        logging.info(f'\[{tenant\_id}\] ETL COMPLETED successfully')

    except Exception as ex:

        logging.error(f'\[{tenant\_id}\] ETL FAILED: {ex}', exc\_info=True)

        run\_sp(conn,'usp\_Update\_Watermark',{'SourceName':f'{tenant\_id}\_Sales\_Excel','Status':'FAILED'})

        send\_alert(f'ETL FAILED: {tenant\_id}',

                   f'Tenant {tenant\_id} ETL failed at {batch\_date}.\\nError: {ex}')

    finally:

        conn.close()

## **5.5. Thứ tự Nạp Dữ liệu**

Thứ tự nạp phải tuân theo quan hệ phụ thuộc — Dimension trước Fact:

7. Nạp/Cập nhật DimDate (chạy một lần, pre-populated, Shared)

8. Nạp/Cập nhật DimSupplier (Shared, không cần TenantID)

9. Nạp/Cập nhật DimProduct (SCD Type 2, Shared)

10. Nạp/Cập nhật DimCustomer (có TenantID)

11. Nạp/Cập nhật DimStore (có TenantID)

12. Nạp/Cập nhật DimEmployee (có TenantID)

13. Nạp FactSales (gọi usp\_Transform\_FactSales với @TenantID)

14. Nạp FactInventory (gọi usp\_Transform\_FactInventory với @TenantID)

15. Nạp FactPurchase (gọi usp\_Transform\_FactPurchase với @TenantID)

16. Refresh Data Mart (DM\_SalesSummary, DM\_InventoryAlert, DM\_CustomerRFM)

17. Cập nhật ETL\_Watermark và ghi ETL\_RunLog

## **5.6. Xử lý SCD Type 2 — DimProduct (Shared)**

CREATE OR ALTER PROCEDURE usp\_Load\_DimProduct AS

BEGIN

    \-- Buoc 1: Dong ban ghi cu khi gia thay doi

    UPDATE dp SET

        dp.ExpirationDate \= DATEADD(DAY,-1,CAST(GETDATE() AS DATE)),

        dp.IsCurrent      \= 0

    FROM DimProduct dp INNER JOIN STG\_ProductRaw s ON s.MaSP \= dp.ProductCode

    WHERE dp.IsCurrent \= 1

      AND (dp.UnitCostPrice \<\> s.GiaVon OR dp.UnitListPrice \<\> s.GiaNiemYet);

    \-- Buoc 2: Chen ban ghi moi (san pham moi hoac gia thay doi)

    INSERT INTO DimProduct (ProductCode,ProductName,Brand,CategoryName,

        UnitCostPrice,UnitListPrice,IsActive,EffectiveDate,ExpirationDate,IsCurrent)

    SELECT s.MaSP,s.TenSP,s.ThuongHieu,s.DanhMuc,

        s.GiaVon,s.GiaNiemYet,1,CAST(GETDATE() AS DATE),NULL,1

    FROM STG\_ProductRaw s

    WHERE NOT EXISTS(SELECT 1 FROM DimProduct dp

                     WHERE dp.ProductCode \= s.MaSP AND dp.IsCurrent \= 1);

END;

## **5.7. Xử lý SCD Type 2 — DimCustomer (Có TenantID)**

DimCustomer cũng áp dụng SCD Type 2 để theo dõi lịch sử thay đổi thông tin khách hàng (địa chỉ, hạng thành viên). Khác với DimProduct, DimCustomer cần lọc theo TenantID để đảm bảo không bị nhầm khách hàng giữa các tenant.

CREATE OR ALTER PROCEDURE usp\_Load\_DimCustomer

    @TenantID VARCHAR(20)

AS BEGIN

    \-- Buoc 1: Dong ban ghi cu khi thong tin thay doi

    UPDATE dc SET

        dc.ExpirationDate \= DATEADD(DAY,-1,CAST(GETDATE() AS DATE)),

        dc.IsCurrent      \= 0

    FROM DimCustomer dc INNER JOIN STG\_CustomerRaw s

        ON s.MaKH \= dc.CustomerCode AND dc.TenantID \= @TenantID

    WHERE dc.IsCurrent \= 1

      AND (dc.FullName \<\> s.HoTen OR dc.CustomerType \<\> s.LoaiKH

           OR dc.City \<\> s.ThanhPho);

    \-- Buoc 2: Chen ban ghi moi (KH moi hoac thay doi thong tin)

    INSERT INTO DimCustomer (CustomerCode,TenantID,FullName,Gender,City,

        CustomerType,LoyaltyPoint,MemberSince,IsActive,

        EffectiveDate,ExpirationDate,IsCurrent)

    SELECT s.MaKH,@TenantID,s.HoTen,s.GioiTinh,s.ThanhPho,

        s.LoaiKH,ISNULL(s.DiemTichLuy,0),s.NgayDangKy,1,

        CAST(GETDATE() AS DATE),NULL,1

    FROM STG\_CustomerRaw s

    WHERE s.TenantID \= @TenantID

      AND NOT EXISTS(SELECT 1 FROM DimCustomer dc

                     WHERE dc.CustomerCode \= s.MaKH

                       AND dc.TenantID \= @TenantID AND dc.IsCurrent \= 1);

END;

# **CHƯƠNG 6: THIẾT KẾ HỆ THỐNG ĐA NGƯỜI DÙNG (MULTI-TENANT) \[MỚI\]**

## **6.1. Auth Gateway — FastAPI**

Auth Gateway là thành phần trung gian giữa người dùng và Superset. Người dùng tenant đăng nhập vào Auth Gateway, nhận JWT token, rồi Auth Gateway tạo Superset Guest Token — người dùng không bao giờ cần đăng nhập trực tiếp vào Superset.

\# api/auth.py

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel

from passlib.context import CryptContext

import jwt, pyodbc, requests, os

from datetime import datetime, timedelta

app     \= FastAPI()

pwd\_ctx \= CryptContext(schemes=\['bcrypt'\], deprecated='auto')

SECRET  \= os.environ\['JWT\_SECRET\_KEY'\]

ALGORITHM       \= 'HS256'

ACCESS\_EXPIRE   \= timedelta(hours=8)

class LoginReq(BaseModel):

    username: str

    password: str

@app.post('/login')

def login(req: LoginReq):

    conn   \= pyodbc.connect(os.environ\['CONN\_STR'\])

    cursor \= conn.cursor()

    cursor.execute('SELECT UserID,PasswordHash,TenantID,Role FROM AppUsers

                    WHERE Username \= ? AND IsActive \= 1', req.username)

    user \= cursor.fetchone()

    if not user or not pwd\_ctx.verify(req.password, user.PasswordHash):

        raise HTTPException(401, detail='Sai tai khoan hoac mat khau')

    payload \= {'user\_id':user.UserID,'tenant\_id':user.TenantID,

               'role':user.Role,'exp':datetime.utcnow()+ACCESS\_EXPIRE}

    token \= jwt.encode(payload, SECRET, algorithm=ALGORITHM)

    return {'access\_token': token, 'token\_type': 'bearer'}

@app.get('/dashboard-token')

def get\_dashboard\_token(token: str):

    payload \= jwt.decode(token, SECRET, algorithms=\[ALGORITHM\])

    r \= requests.post(f'{SUPERSET\_URL}/api/v1/security/login',

                      json={'username':'admin','password':os.environ\['SUPERSET\_ADMIN\_PWD'\],

                            'provider':'db'})

    admin\_token \= r.json()\['access\_token'\]

    guest \= requests.post(f'{SUPERSET\_URL}/api/v1/security/guest\_token/',

        headers={'Authorization': f'Bearer {admin\_token}'},

        json={'user':{'username':payload\['tenant\_id'\]},

              'resources':\[{'type':'dashboard','id':'1'}\],

              'rls':\[{'clause':f"tenant\_id='{payload\['tenant\_id'\]}'"}\]})

    return {'guest\_token': guest.json()\['token'\]}

## **6.2. Security Design Chi tiết \[MỚI\]**

| Hạng mục | Giải pháp | Chi tiết |
| :---- | :---- | :---- |
| Password Hashing | bcrypt (passlib) | rounds=12 — đủ mạnh cho production; hash mỗi password trước INSERT |
| JWT Algorithm | HS256 (HMAC-SHA256) | Secret key ≥ 32 ký tự, lưu trong biến môi trường — KHÔNG commit vào code |
| JWT Access Token | 8 giờ expiry | Sau 8 giờ phải đăng nhập lại — cân bằng giữa UX và bảo mật |
| JWT Refresh Token | 7 ngày expiry | Lưu trong HttpOnly cookie — không expose cho JavaScript |
| HTTPS | Bắt buộc cho tất cả endpoints | Dùng nginx reverse proxy với Let's Encrypt SSL certificate |
| Superset Admin Pwd | Lưu trong env var | SUPERSET\_ADMIN\_PWD trong Docker Compose .env — không hardcode |
| SQL Injection | Parameterized queries | Tất cả query dùng ? placeholder — không string concatenation |
| Sensitive Data | Ẩn bớt ký tự | Phone: '0977\*\*\*653', Email: 'user@\*\*\*.com' trước khi lưu vào DWH |

## **6.3. Cấu hình Superset — RBAC và Row Level Security**

### **6.3.1. Tạo Role TenantViewer**

Trong Superset, vào Security → List Roles → (+) tạo role TenantViewer với các permission:

| Permission | Được phép | Ghi chú |
| :---- | :---- | :---- |
| can read on Dashboard | ✅ Có | Xem dashboard read-only |
| can read on Chart | ✅ Có | Xem biểu đồ |
| can read on Dataset | ✅ Có | Xem dataset metadata |
| can explore on Superset | ✅ Có | Truy cập trang Explore (view only) |
| menu access on Dashboards | ✅ Có | Hiện menu Dashboards trong sidebar |
| menu access on Charts | ✅ Có | Hiện menu Charts trong sidebar |
| can write on Dashboard | ❌ Không | User không thể tạo/sửa dashboard |
| can write on Chart | ❌ Không | User không thể tạo/sửa biểu đồ |
| Admin menu access | ❌ Không | User không thể vào Security, SQL Lab, Settings |
| can add/edit/delete (bất kỳ) | ❌ Không | Không có bất kỳ quyền ghi nào |

### **6.3.2. Cấu hình Row Level Security (RLS)**

Trong Superset, vào Security → Row Level Security → (+). Tạo rule cho mỗi bảng Fact và mỗi tenant:

| Trường | Giá trị ví dụ | Mô tả |
| :---- | :---- | :---- |
| Table | FactSales | Bảng áp dụng RLS (tạo thêm cho FactInventory, FactPurchase, DimCustomer, DimStore) |
| Role | RLS\_STORE\_HN | Role riêng cho tenant STORE\_HN — gán cho Superset user của tenant này |
| Clause | tenant\_id \= 'STORE\_HN' | Superset tự động append vào mọi query từ role này — user không thể bypass |
| Filter Type | Regular | Áp dụng cho toàn bộ query không phân biệt loại |

### **6.3.3. File superset\_config.py**

\# superset/superset\_config.py

\# Tat self-register (user khong tu dang ky)

AUTH\_USER\_REGISTRATION     \= False

\# Tat public access

PUBLIC\_ROLE\_LIKE           \= None

\# Bat CSRF protection

WTF\_CSRF\_ENABLED           \= True

WTF\_CSRF\_TIME\_LIMIT        \= 3600

\# Session timeout

PERMANENT\_SESSION\_LIFETIME \= 28800  \# 8 gio

\# Tat SQL Lab voi Viewer

FEATURE\_FLAGS \= {

    'ENABLE\_TEMPLATE\_PROCESSING': True,

    'SQLLAB\_BACKEND\_PERSISTENCE': True,

}

### **6.3.4. Script Tạo Superset Users Hàng loạt**

\# superset/scripts/create\_users.py

import requests

def get\_admin\_token(url, pwd):

    r \= requests.post(f'{url}/api/v1/security/login',

                      json={'username':'admin','password':pwd,'provider':'db'})

    return r.json()\['access\_token'\]

def get\_role\_id(url, token, name):

    r \= requests.get(f'{url}/api/v1/security/roles/', headers={'Authorization':f'Bearer {token}'})

    return next(x\['id'\] for x in r.json()\['result'\] if x\['name'\] \== name)

def create\_user(url, token, tenant\_id, username, email, password):

    payload \= {'username':username,'email':email,'password':password,'active':True,

               'roles':\[get\_role\_id(url,token,'TenantViewer'),

                        get\_role\_id(url,token,f'RLS\_{tenant\_id}')\]}

    r \= requests.post(f'{url}/api/v1/security/users/',

                      json=payload, headers={'Authorization':f'Bearer {token}'})

    print(f'\[{r.status\_code}\] Created {username} for {tenant\_id}')

URL   \= 'http://localhost:8088'

TOKEN \= get\_admin\_token(URL, 'your\_admin\_pwd')

for tid,uname,email,pwd in \[

    ('STORE\_HN',  'manager\_hn',  'hn@co.vn',  'Pass@HN123'),

    ('STORE\_HCM', 'manager\_hcm', 'hcm@co.vn', 'Pass@HCM123'),

\]:

    create\_user(URL, TOKEN, tid, uname, email, pwd)

## **6.4. Monitoring và Alerting \[MỚI\]**

Hệ thống giám sát đảm bảo phát hiện sự cố sớm và thông báo đến admin trong vòng 5 phút.

| Sự kiện | Phương thức alert | Nội dung thông báo | Thời gian phản hồi |
| :---- | :---- | :---- | :---- |
| ETL FAILED | Email \+ Slack Webhook | Tenant ID, batch date, error message, traceback | ≤ 5 phút |
| ETL chạy quá 45 phút | Email | Tenant ID, thời gian bắt đầu, số bản ghi đã xử lý | ≤ 5 phút |
| Tỷ lệ lỗi \> 5% | Email | Tenant ID, số bản ghi lỗi, tổng bản ghi, tỷ lệ % | Cuối mỗi ETL run |
| Superset unreachable | Cron health check mỗi 5 phút | Service down, uptime log | ≤ 5 phút |
| JWT token giả mạo | Log vào file security.log | IP, username, timestamp, error code | Real-time log |

\# etl/utils/monitoring.py

import smtplib, requests, logging

from email.mime.text import MIMEText

from datetime import datetime

import os

SLACK\_WEBHOOK \= os.environ.get('SLACK\_WEBHOOK\_URL','')

SMTP\_HOST     \= 'smtp.gmail.com'

def send\_email\_alert(subject: str, body: str):

    msg \= MIMEText(body)

    msg\['Subject'\] \= f'\[DWH ALERT\] {subject}'

    msg\['From'\]    \= os.environ\['ALERT\_FROM\_EMAIL'\]

    msg\['To'\]      \= os.environ\['ALERT\_TO\_EMAIL'\]

    with smtplib.SMTP(SMTP\_HOST, 587\) as s:

        s.starttls()

        s.login(os.environ\['SMTP\_USER'\], os.environ\['SMTP\_PASS'\])

        s.send\_message(msg)

    logging.info(f'Alert email sent: {subject}')

def send\_slack\_alert(message: str):

    if SLACK\_WEBHOOK:

        requests.post(SLACK\_WEBHOOK, json={'text': f':rotating\_light: {message}'})

def alert(subject: str, detail: str):

    send\_email\_alert(subject, detail)

    send\_slack\_alert(f'{subject}\\n{detail}')

## **6.5. Backup và Disaster Recovery \[MỚI\]**

| Loại Backup | Tần suất | Phương pháp | Thời gian giữ lại |
| :---- | :---- | :---- | :---- |
| Full Backup — SQL Server DWH | Mỗi Chủ nhật 00:00 | SQL Server BACKUP DATABASE TO DISK | 4 tuần gần nhất |
| Differential Backup | Hàng ngày 00:30 | SQL Server BACKUP DATABASE WITH DIFFERENTIAL | 7 ngày gần nhất |
| Transaction Log Backup | Mỗi 4 giờ | SQL Server BACKUP LOG | 48 giờ gần nhất |
| File Excel/CSV nguồn | Sau mỗi lần upload | Copy vào thư mục archive/ với timestamp | 3 tháng |
| Superset Dashboard Config | Mỗi tuần | Export dashboard JSON, commit vào Git | Toàn bộ lịch sử Git |

Recovery Time Objective (RTO): ≤ 4 giờ — thời gian tối đa để khôi phục hệ thống sau sự cố.

Recovery Point Objective (RPO): ≤ 24 giờ — tối đa 24 giờ dữ liệu có thể bị mất.

## **6.6. Cấu trúc Thư mục Dự án**

dwh\_project/

├── api/                          \# Auth Gateway \[MỚI\]

│   ├── main.py                   \# Khoi tao FastAPI app

│   ├── auth.py                   \# Endpoint /login, /dashboard-token

│   └── models.py                 \# Pydantic models

│

├── etl/

│   ├── extract/

│   │   ├── extract\_sales.py      \# Doc Excel, gan TenantID \[CẬP NHẬT\]

│   │   └── extract\_inventory.py

│   ├── transform/

│   │   └── transform\_sales.py    \# Transform DataFrame \[MỚI\]

│   └── orchestrator/

│       └── main\_etl.py           \# Vong lap tenant, monitoring \[CẬP NHẬT\]

│

├── sql/

│   ├── schema/

│   │   ├── 01\_create\_tenants.sql      \# Tenants, AppUsers \[MỚI\]

│   │   ├── 02\_create\_dimensions.sql   \# DimDate, DimProduct, v.v.

│   │   ├── 03\_create\_facts.sql        \# FactSales, FactInventory, FactPurchase

│   │   ├── 04\_create\_staging.sql      \# STG\_\*, ETL\_Watermark, STG\_ErrorLog

│   │   ├── 05\_create\_datamart.sql     \# DM\_SalesSummary, DM\_CustomerRFM \[MỚI\]

│   │   └── 06\_add\_tenant\_id.sql       \# ALTER TABLE \+ INDEX \[MỚI\]

│   ├── sp/

│   │   ├── usp\_Load\_DimProduct.sql    \# SCD Type 2

│   │   ├── usp\_Load\_DimCustomer.sql   \# SCD Type 2 \+ TenantID \[MỚI\]

│   │   ├── usp\_Transform\_FactSales.sql \# Co @TenantID \[CẬP NHẬT\]

│   │   └── usp\_Refresh\_DM\_\*.sql       \# Refresh Data Mart \[MỚI\]

│   └── views/

│       └── v\_FactSales\_ByTenant.sql   \# SESSION\_CONTEXT filter \[MỚI\]

│

├── superset/

│   ├── docker-compose.yml

│   ├── superset\_config.py             \# AUTH\_USER\_REGISTRATION=False \[CẬP NHẬT\]

│   └── scripts/

│       └── create\_users.py            \# Tao users hang loat \[MỚI\]

│

├── monitoring/

│   └── monitoring.py                  \# Email \+ Slack alert \[MỚI\]

│

├── data/                              \# Thu muc du lieu theo tenant \[MỚI\]

│   ├── STORE\_HN/

│   │   ├── BaoCaoDoanhThu.xlsx

│   │   └── QuanLyKho.xlsx

│   └── STORE\_HCM/

│       ├── BaoCaoDoanhThu.xlsx

│       └── QuanLyKho.xlsx

│

├── docker-compose.yml                 \# Them service api \[CẬP NHẬT\]

└── .env                               \# JWT\_SECRET, SMTP\_PASS, v.v. (KHÔNG commit Git)

## **6.7. Luồng Hoạt động End-to-End**

| Bước | Actor | Hành động | Kết quả |
| :---- | :---- | :---- | :---- |
| 1 | Tenant User | POST /login với username/password | Nhận JWT access token (chứa tenant\_id, role, exp 8h) |
| 2 | Tenant User | GET /dashboard-token với JWT | Auth Gateway tạo Superset Guest Token cho tenant này |
| 3 | Browser | Load Superset embedded iframe với guest token | Superset hiển thị dashboard — user không cần biết Superset tồn tại |
| 4 | Superset | Thực thi query trên FactSales | Superset tự động append WHERE tenant\_id='STORE\_HN' từ RLS rule |
| 5 | SQL Server | Trả về kết quả query đã lọc | Chỉ data của STORE\_HN — data STORE\_HCM hoàn toàn không xuất hiện |
| 6 | Admin User | Đăng nhập Superset với admin account | Xem toàn bộ data của mọi tenant — không bị RLS filter |
| 7 | ETL Scheduler | Chạy main\_etl.py lúc 02:00 SA | Lặp qua từng tenant, nạp data, refresh Data Mart |
| 8 | ETL (nếu lỗi) | ETL FAILED | Gửi email \+ Slack alert ngay lập tức, giữ watermark cũ để retry |

# **KẾT LUẬN**

Báo cáo Phân tích và Thiết kế Hệ thống đã trình bày một cách toàn diện và có hệ thống về giải pháp Data Warehouse đa người dùng cho chuỗi cửa hàng bán lẻ thiết bị công nghệ. Các nội dung chính đã được đề cập bao gồm:

* Phân tích thực trạng: Hệ thống dữ liệu phân mảnh hiện tại gây ra nhiều bất cập nghiêm trọng, từ sự thiếu nhất quán trong báo cáo đến khả năng ra quyết định hạn chế.

* Yêu cầu hệ thống: Đã xác định đầy đủ 22 yêu cầu chức năng (FR-01 đến FR-22) và 12 yêu cầu phi chức năng (NFR-01 đến NFR-12), bổ sung nhóm yêu cầu multi-tenant FR-10 đến FR-16.

* Kiến trúc 5 tầng: Bổ sung Tầng 0 (Auth Gateway) phục vụ xác thực và phân quyền multi-tenant, stack công nghệ đầy đủ với phiên bản cụ thể cho từng công cụ.

* Thiết kế CSDL: Star Schema mở rộng với cột TenantID xuyên suốt bảng Fact/Dimension liên quan đến cửa hàng. Bổ sung bảng Tenants, AppUsers, Staging Layer đầy đủ cột, Data Mart Layer (5 DM\_\* tables).

* Thiết kế ETL: Pipeline ETL cập nhật chạy vòng lặp theo tenant, code Transform Python đầy đủ, SCD Type 2 cho cả DimProduct và DimCustomer, cơ chế Watermark Incremental với logic cập nhật rõ ràng.

* Hệ thống đa người dùng (Chương 6): Auth Gateway FastAPI/JWT với Security Design đầy đủ (bcrypt, HTTPS, SQL injection prevention), Superset RBAC \+ RLS config chi tiết, Monitoring/Alerting (email \+ Slack), Backup & Recovery policy, cấu trúc thư mục dự án cập nhật.

## **Hướng phát triển tiếp theo**

* Tích hợp mô hình Machine Learning cho dự báo doanh thu và nhu cầu tồn kho (scikit-learn hoặc Azure ML).

* Nâng cấp lên kiến trúc Lambda (Batch \+ Streaming) với Apache Kafka cho xử lý dữ liệu gần thời gian thực.

* Triển khai Data Quality Framework tự động kiểm tra và báo cáo chất lượng dữ liệu sau mỗi chu kỳ ETL.

* Mở rộng tích hợp từ các kênh thương mại điện tử (Shopee, Lazada) thông qua REST API.

* Xây dựng tenant onboarding tự động: thêm tenant mới, hệ thống tự tạo Superset user, RLS role, ETL config mà không cần can thiệp thủ công.

* Xây dựng Test Plan đầy đủ: unit test cho ETL modules (pytest), integration test cho pipeline, performance test với dataset 5 triệu bản ghi.

[image1]: <data:image/png;base64,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CX761cibbr7tssuvGj91pjsgQJgPR3x+y223X3Pt9aDhBx969KEh/x766utXXnPtwuWrUO5jTz593wMPP/fiy5defsX0OfORbZfN/srrb1159bV33n0vzDtfRMzYnPPwvx+/8urrHnpkSFldy6x5i5567sX//Pd/r7z+dlAQ12Ztveqa65978VVkDjokK1Dip2UpoEN/OGxygebEv/3tkJVpmV021//e//DKq6655bY7NmRv9wnilryix554+rob/nnPfQ8UlNdEROGJp59/5/2P7rz7PhQBSkN3v/yqq9/437v3PvDQi6+8ZnB4aGIBYj7r7HNPO/X0B/71MDS2cFnK5Vdede8DD19y6T+ef/lV/FTSszY/9tTTtFoLJUjzg1hDkyetVGty+PpxS9qBAqfDZAenw1+GwHbQjJw+J21rrhyyc5T+wQCkQ9JkarGarBkyGiQ6FCU6JOsQY65kHZ50EvTy+FPP3nzr7Uannxb6MMR//MkXl19+ZbfN6wwJGG3BRmBK3EXCBUtWHXroYEaNvrvuuZ+yoiEYRXj8oX/ectugQYPmLlpu8YYDERHW0ogvv7a4A9WNzT9OmiYK4uDBh995z72FJeVHHHHUuedfOGfB0qeefeHKq69xeUkAiXdBhyhXlGyssDccevPtd01O75KVaxpU+q05eccdd4IoUUL24MGHGZ2BdRu3bisqv/9fD8OQ/Xn+IvDrZZdf0aTp+vcTTx/0x4OnzJz9+VejTjnl1E25hW+9M+y0007fnFv40KOPXfqPy7stVvBW1tbtVrv7uReG3nbHXWMnToHwr7/1bpu2s0VnPPe887VG+6JlK48++ljoR7YOQYd/P+vsMDOyveHIOeee98nnX3/86RcnnnhSetbWZ196+cyzz9F2G7ZuL4bCYSa++fZ7sHeR8A9/+H8vv/7f2sbmI444ct6SlQj585///OyLL1fW1B955FGz5i6S5xaPPv74vx4ZUlLTiDE+ZW0molXW1G3ZXnzkUUdBh/OXrLzk0svAmtDV408+wyzdMBmL1OIt3e71ZZqw1ObJDU6HyQ5Oh30BtQixzl1e22B1OPZ1vQYmHQIpheqgGH28FKVDQcjckrs2cxOMR3DY19/9cMqpp8H4ePaFl66+9voum4cNxILR6fvk85GX/OPyDovLGYy899EIGCW4i6H1lNNOG/bRJzBqiLeUG1UQAv7DgHTrbXc8+MiQf956hzsseATxw+Gfgcyee+nVF17+z4uvvo6W/scVV67dsNkdDj/2+JNvvv0OiHbN+g0gp+KqeuSwgw6HfwaBLe5QQBRgRxqsjgceevjue+//+vsfjznmWK9klQZ/GD/l4n9cDvNrS17xfQ889N6Hw+3+IDgDBuKa9RsfGfLYK6+9afEEIMnd9z/w+lvvHHPscQh3h0KVDa3XXnfjxKkzx0+ZccVVV38xavQjjz1x2ulnjJ0w5ebbbm9Sd3gikckzfj7vggs7re5gMDj80y+gASUdwjoMCQKEh40INX47ZtzJp5w6b/FykHejSn/zLbdDvbPmLrzi6mteevWNp1946djjT9Bb3Nff+M/qJpUvHH7imWeHvvY6srr2+htLaxoQ8sLLr4IXrUwDaJ0Xhr7y9PMv0iRm4bJV11x3A+LYfGEYkaK0WrsCavSKsA4jTz/3ok96qXr00Sy1hdriW13UHlJ8mSRJwekw2cHpcJegKqDjggg/HjOV/Pt0SWdg0iGua0s1ZCiQwwgL5isor8GQjbsYx197861/XH4VxnTYTwcffHBeSbW8U2PG7PlnnX1eZX0rCO++Bx967KlngoJYXl3/9vsfBMXo60wRzSctb0aHYKRFqRmbtq1Kz7TZHccffwK4EGP5N6N/bGjTNWs66tt0erMTnAzmS9+4BbTy78eefO2N/2LET8vcdMlllxZXNRAZ0GIpLFTI6RfFbpv72OOOX5OxGWTWqutG4IUXXSJxbUR60rk9P//2u+658+57H3r03/8b9qErJGYXlFx51dWgvYeHPH7XvfdDDLM7cO31Nwz7+JNjjz1+2qy5oNuSqvpzzj1/3uIVZ51zzlffjEaey1PXHnX0MWMnTv3nLbe36oyYSSxPTT/u+BOgKNx96eXXMEtQLpbCOoywx4HAIYccuiE7HyGjRv+IuUJ9m/b8Cy6ePP1nMNa7wz52+fwbcvIPHTy4y+aGGLUtaijz8aefGYrJAYj/2uvKapsQ8vzQV559YSgZeWZP6MWXX3t+6MvIH3EWLU+FcYk4joAA1kQIDGWwuE8QwBJ33nu/n01QZNMQrqHbualaz61DjgMOTod9gWoxYcGyhWkbiAv3ab0GIB2SSivV5q11Bvm4vTRcShwWvOyKK1u13WCyI48+ZvS4ST5pxc93y613nHveBe6IFPPHSdNNLs9ZZ53z7ocfZ2Xn/e1vh6xev7GsuuGU0/5e16Kpamgtr20GMZjdweGffQXzgzjMGxHa9d2X/eOKUDgCSli0IjW/tBrC5JVUjvxuTIh9HHFzXiFGtYsuuRTWIXju0SGPv/KfN5B8TcbGCy66qKiyntZdQVeXX3XNK/95U2+0zVu04oKLLjnzrHPSsrYcdvjhNU3tYyZI65ngwvL61i3bS1DEux98dP2NNz340KNvvzcMBhzo8LLLr0hNz3pkyOO/+93v1m3KnjVv8cknn7p+c87QV/9z4cWXtOoNL7/2JsTQGe3nX3jR+x8Ob9V1nXve+bB9fxg/+Yabbm7VGVAFGHlnsv0y24vLjz0OvCgtlkI8hMxbuuLkU04DN2fnl370yRf/e/9DTDY++OiTs84+p7ql/f0PR5zx9zORCSw/lIied8WVVx111NGYDYDVJDqUHqA+9cLQV5EVWE2iQ9joLw596tkXoAFpbuEOjvj0y6uuua5Vb0ScBUulZ4dBxr7PvfQyQvLLqlEWPGB9TGXYzp3oYinjRSGlsN3lC+7Tieb+AafDZAenw12CuvVnk2ZWNjbLgfu0XgOQDgFSaK3O4gpK+wxpQw1t3weRNLZ3FJTVeOhMITsyQYcOiysbWnQGtkNSimZ0+tVdFg/jSDg3200aO8UvhTBrKXqX7MXYBlH5DACzV3xCVWN7RX2rdAaD7QilW/CQn7Iij3xLPtVAG0YoTkOrXpYEt0AblY0qMAGd/2NJduRGlbJ4w+0dJmbICs6QlFWDSo8KErchq26bt8PigodyiIknVRPJi6oaumwer2SZRTOXzx1SlWVRHeykY5O6E7Yd3XWFRaPDX1rVSOLJgsl1J48yRFaCXAQVR5Epmo1pFSKh7qBPDzuSSFt8pclEWGw2eGLHbZIenA6THZwOewHJD7slGAotWbtBlKgx+s7h+Kj9igFIh5JKBenbWPCnlWqt3pA3NnbTQK8YancE0vDtZEe/KYQGZTmaHJmGb9mvvNXTQ0451isz7NXFJVfekrmKXaM5K+P09DsUtSDn3CmTnQRWpqU/lSXGRaOQuEBSoDJzxmTxme/K09MfV5zSo6y7gx0GRUPXd7iW57ex39q+XXfZP+B0mOzgdNg7pP4qCFsKS70+f/++mLQPDEA6FJl1KEiMKBS3GFKLVK0GF9smQ4+XehlelaNwzz/3xlEmcTnvmeuZjzKkp4urhRyt10yUEZg//u4vul5z6zXzvXRxspGzsK9UFreZVxe3ewKh38BwQeB0mOzgdBgPITZXnbJ41eL0DaGwtMtx/1RnYNKhGNujNGNp6tJ1WZuKKrPru9vM0sYPOh5Og2nPoZa7ZHESCwbYZ0l8EbMnklml31SjF+m3luTDhRKcDpMdnA57AQk/Yvz0QDC4PysycOiQtBrXYQoqa5778Jt/vz3iPyOnDJ+4YObqrdJn1ntsROw52nKXgE5haAqSjegTvBHpy8Dp5bparcXpDdDzh/iekczgdJjs4HS4E2TJXW5Pq1aawFLgTpH2GQYCHe7URXoo1uX2jpuz5KHXh/3r9WHPfDjqheGjUrcWyIcl9sVqHnf7yO00d5Fe2y1kVXWsKGg3OXzKFu/ZB5IXnA6THZwOd0CWubi6bsS4GULsVaX7Db8ZOlR2A7YOulNnCIZCbq/X5nBVN7Vm5RXOS1331qjx/x3546K0rE2Fpe0dXa989v39rw578v3PEDkUjviDocW5LZuqO3Q26V0w3rDokbYs7ngWFbdZhrv97GTag4faBW3kDIjdrlBpu2VBTktGhSYYirDHxKxv/LZYUAanw2QHp8MoSGB0U38g8MEPU6oam9kDxP1ai6SmQ9KVEOW/SFh668tOMJgtbdqOsrrGhWmZExes+HTcrC8nz56zat3mghKXxyNHg+bvHvrO8LHTYJ3HXpUuXTusnlVFqpJWS6vJ0272+gXRx05fyB+s4Cbj/nextVABrUCbRQOCtD211eip1TnSSjWVKrPcslJDxjqJMvA3A06HyQ5OhzsgsHeTzk9dP2flumBI2k8aH2MfIxnpkBpa4r9IhF5op7xlsTuKa+o3bi9akbnlxzmLPx0389PxMzfkFlU3t8E6jIscDIZ8fv/rn4+euXSNEFM+5S93p2q1eU1xe2a5tlprr+twGKX3oknfCqYRmfPi/nGkYdK51Sd9qikoSq6xy1Wts5eprauL2nMbuvzh6EfQlGOC3JS/PXA6THZwOowiwkbzQCC4flsB/RkfY98jKehQYPZfKBRWkp/BZC2pqU/ZsHXyopVTFq2cuiTlp5Vp67LzK+t3vMEAgLUXREp2coV6iNxPENii0U1bmtqi1oZCoZhduAMUM8IOKcqrr2qDo6CpK6+xe0t9V3adoc0kWY0Yl6XXhPoiVmayyGN3z2Gdu910NMmwSuQnvQAWGkbbqy2+3EbDptrO3Pqu/Mau7Y1dotya0RZOvnFgb8DpMNnB6VCCwOxCeLK2F7s8XjpouP+rkJh0KDeoZAKyYyfyLafbs2bztnFzlo6bu3TmijXzV6/PLatsUmmsDqcchyiQOJDS9lQsy1xo03Y63W45Qs9ocqDUXgpS9AXCDXprtdqS19SdUamHg+2IIRt69EuvQWFLeQrDkVNj304+7hlVHZtSuGImoCsgZlTo15Zpc+q6KtpN1Rqz3R3tsQIjwjBrF+ozsXYbEOB0mOwY6HRIctJ1yfqNU5akYOymzrr/cQDpUNJAn81nstpySso/Hjv9ne8mfv/Tws35pfUt7bouQ9wCKVl+ZBiIu6C0XqEs99elYpfIzt9kDoUjBrvH6PCqjc7UIlVKQfvy7aoKtdXoDDmlEV/AVeliNLBjuVV2FN6TM5LO9ayaXC9JCcGYi8YXdLZAYaslpVC9dHvrygJVbkOXwe412Dxm146toZLmB54VuCtwOkx2DHQ6FKM/6YhK1zFi3PQuo5kMoAMi//6nQ6om1TfOIMafHq+vTavLzCn436gJ74+eNGvZ6kaV1mJzur07dr6IMQVSJkROyru7A6UY8fd2D9HSY1De8vpDbl/Q4w/WaqyZFbpVhaplea3rK3SlKovZGza6QyZP2OKV1gBdQekLGORcjBh68oeSSGQ6SRAnS7Urh7vKOtIJFtQdGjC6QiZ3uM3oXluuW5TbsjSvdW2JpkJlwqwC2oMLKvZGCb+t4/P9BU6HyY6BTodCbCiftiR1edbm+Nv7F/uTDuVmCu/Mgv5AUN9tLKtvTMnK/u/IccPHz5i3OsNktcdFE3dmIPpTefdAQSkVIe4uW82LmFy+Wq204yOtRL2qSLWpqgPs2Gxwa61+nQ0u0O0MgSc8YekxpJddfRHp6mJvwQav2NihgjjXk4GIhOi6Z07OoafrKQDJQJwXFT4muYdtOOpyBrU2v8biQ03hClosGRX6JdtbF21rWbStOatCa3H50dQ9m5u016tWOQicDpMdnA4lBALBspoGQXqC2MsosN+w7+iQKiVEd8FI+/0IPr8/r6x61Yacn1emfzJh1oQFy2ALKlPtWPrcAemOHCcpIFc/DlQz5SqrDI8v1G5wbqrSZlRoMiu0GeXadeWajArttrqu/GZDcZu5XG0rV1vZNeqqdI7GLleLwaO3BzrsAbNH2ssDEqJHbnEupPDIThke59AnpJ1BfhGZw4HJGrpcFRp7mSyAJipPmcqa12DIru8Cx68v0zIHyTWbq3SV7SanNxhf1Zi1F9/OMVCE+DQcPcDpMNkx0OmQ+uUm9i26uNXC/Y99RIcCG+mkLZ3y6QVRbNPo56Wun7kkdczsxTOXr8kurpDjS5QZlh4CkjYOrE72NeQ6SnwgWUVRFx8vBrPL125wVLWbcuo6ttV34ppT15lT25ENV9cJspRcY3duQ/f2RkMeXJMxr8mE6/ZmE7m8qJNC4MlVXFlINHxH/FgOUm6NRmQuuQapIJS4tTYqQE59J8lT1NzdYXFb3P5dfVA3wl6YTk5JgfHxOH4lOB0mOwY0HQrM+nF5PO98N/GAc6HYr3RIdRHYjlnlbhe1vmv64lVj5yyZvGjlgjWZ2xQsCAJkpyCie0cPuDYOFGRLktGGtLJKuyXlPZN9AJ3IHwyZnT6Tw6sxOVUGe63WUtZmLG8zle1wRrhS6Sr9WbrDSSGx8OhdOJZWykHVbW/rskuZO702j393THSF5JJHaejHR+XYa3A6THYMUDok8dApO7pNH4yeZLbZE0HmPabDXak9FAzNSU3/YPSULyfPzsorqmps0XdLnyyP3g1LYGniE3L8WiibgBYeo05hce6li5DbeVUzXg6OAwdOh8mOAUqHIhu/YAyNmbMkbUuuGOugBxZ7QIc5OTlx2hbYELx2a97X0+a8/fW49Jz8RpXaZLHJEWijRCJYwxwcvyVwOkx2DFQ6FARaQgRnyKbhAZd5N+mQ5PT5fMrFUvzAPD5fQUXNTylp73w7fv6a9ZUNLU6Xm9b+KBVRICU/4JXl4PiNgdNhsmMg0qEQ48Lc0iqrwyHEeCI+3n7HruhQ1md45/eCPvz4Uz9O/3lZ1tZPxk1fum5DbYsqLokMCpHvcnBw9Ds4HSY7BiIdioxXvD7/j7OXSP6dXzx2ANGTDmVlQuBg7ICEvsuYU1yxKC3zX0Pf/GzctM0FpXJ8tgoaVX6CVIqDY4CALVarCAAAasFJREFU02GyY8DRoSzb1qLysbMX00vF4iMdICjpkIQUdj4m36TSrNqYM3nhyvHzlv20fPWNN/2zuqIc4WxDqFQTOSEHB8d+BqfDZMfAokMSDH1xa1HZqOnzAsFggnAhqau8vBx06Pf76REfQmDCbiks/WTCjGlLUldtyOk07vh6nNvtueuuu3Z10IKDg2M/g9NhsmNg0aHIOiJkG/PzovyKGlFhLB4oUOkkhkSHN90UCkrvDXF5PN/MmDfs+8mzlqe1avU2546vA1IV+j53yMHBsZ/B6TDZMbDoUBbsi0k/CeygRXyM/QVZEoEdI6PA6qqqf95884bcwu9mzn9r1PjCqlqzze4PRN+qRTHlhJwOOTgSCpwOkx0Djg5xLaisFdkh9P0vJJUoxD6vCNgczqZ2bVZu4fBxM98fNXbI08/HxZeTxEnL6ZCDI6HA6TDZMYDokKSCRfjJ+JkCe4IYH2NfghQSYRtEye90eyrqm6YtTvls/MxJC1YgpKmh/obrr/f5fLujQ06HHBwJBU6HyY4BRIci46T8ipqRU+fQ47f9IySVIsQOOxKWrd80ZXHKmJ8WltTUg5pFdt6jtLSMdpbujmCcDjk4EgqcDpMdA4gOw+FIYWXtd7PmhyP74wO/lH8kdnDe6/Wlbckb8/OiBaszckoUL86OnqOQIvc8d9gHOB1ycCQUOB0mO5KeDuNLjaFnHHTTj8ZMr25oEfbZSimV21OMBpXmox+mzlm1TtvZTSHSOUF6fbYiGqdDDo7kBafDZEcS06FcSnxZvQUS94ydswRW2j4STxZGmXlmXuH7308ZOXWurrNb3iMqn6yPE4PTIQdH8oLTYbIjWelQWYpXr7dkZ3evSuletcK0IdOjUVME5VUZX/b0C+Scw+GoxdllMn81afZHY6Zk5hbGRSOPHBgHToccHMkLTofJjmSlQ0D6jpEohlwuQ8ryYH2NaOiAC7c0mlJXBsxmYRfE02vgnkHOSt4jU9fSvixj02cTZzWpNHKcqDZ2QyecDjk4khecDpMdyUqH6E+RQMC8ebO7pCiibhX0arFDIzm9Gn/6qitMa9OFffOMUK6dfIp/ecbmCXOXjvl5sdfnoxDG1L+aejkdcnAkLzgdJjuSkg4pf29npzE1VbSZQIESHTIX9Tgs1rVryEDsX0koN1xDjAu1XYZZK9J+Xrl2e1k1RQBH7vEpDk6HHBzJC06HyY6kpEPqTJZtOcGm+ggokOzCmMOfCAy1NIRc0ns++8tAlCsVjmU4bv7Sr6bOXrJuQ1yEPQanQw6O5AWnw2RHUtIhZW5Ys1ro0u1YJlUyoq5dMHUFzNL3H/pLEqoU+vF3Mxd8+MPUjfnFylvydW/A6TBhITdx34hPti8RX/YuEJ+MY5+B02GyI1npEOhes1rs1kd07dLqqJIO9eqIViWau/0mcz9KQkugrRpdbmnVjmeE/VpZTocJglirSu9Mj3PxUXtDKBwJRyKBUNgfDHkDIZcvuPfO7Qv6giG4sPRiB6kvxpfaA3Hyy4iPx9FP4HSY7EhKOqTOZN6yOdzWDDrsdbE0om4NOhxy5L0H1UhZr36vI6fD/Q/qqdRjJdqIRN2uGhe3JIbzBrtt3m67p9vuJU+X1dtp9TZ3Our19sJmI9zWuq6sKn16qXbpdtWy/HaFU5Fbmt8Otzi/fUn0StGU16hbsl2VUqjOrNRnVuiQc0GzsbzdrDI6umyeTqun20ZieAx2yW91+X1BjMi9yy9VM1bH2DPu3mNy/FpwOkx2JCUdiqw/hX0+U2aGr66q587SQHODafVqoV93llKNlNd+B6fDfQQhes5FIoCw5GC9xbeg2x/SW9zlKlNFu7mszZjfZNhW35VZ2bG2TL+2XJteoV9bpksv7yhSWZoNXq01EBLFIHMhhfMLoj8iesKSc4VEZ1B0BESbT9h7Z/cLyA2OMveGxYCwU9EkD0Zii1do6HLnN1s21nSllevWlushfHq5fkNNV05Dd7nKXNlurtZYKtXmer3NF4gfu0k54dh+MHGf9fbfHjgdJjuSkg7l/AM2W1dqimg3wyIUtCrJdajxZ9fSxV6NJvaL3oeS9C84HfYj5HaPUWB8N/AFQ0Uthq21Hdl1nTl1XVvqurfUd2+q7dpY2wXmyGsy1ugcILMwY5pwzElsFxJdQdHqExQuQp4oe/klZ485ZELXPXNyDuQoc8ntKJpKj14dAQF86WdkKYsNh1tqiz+v2by5tntrvVTZzXXdOfXduQ3deY3dBU1gSpPWvOMr0yLTIalOtiOT58d0AMDpMNmRlHRIoGP4fpPJnJEebmkQzV2iuTuibrFmpHu1GiEJZ7WcDvsLgmLlUw4MhCKtXY7s2s7MCm1GhW5Ddee2RlNesymvyVSisjUbPAa3NJIRi8DS8kVEe2AHzZCH2E5BUfHsdQCdLFUPspQcbrlDUQuSrEnwemO3u7TdVthmKW6zFrSachoM6yu0Gyr1mZV6tcEZN4dQLiP/f/a+Oz6Kov//+eP5PV+/z9feGwqKiKJSpEoVRbAi0ouCvSNIlaICUqT33lsSIBAgkAAJIb33Xu4ul+u997vd32dm7pbLBRAxgSyZ9+uTzezszOzMZ2bnfZ/ZmVnePVw3AZQO+Q4e0yEBgxuW22Jx6XQOpdJtNvs9b2IeGguUDq8fpHKv1thcbm9UligspQYkW6gHqqtR28R6p8bmAw4gQ5p2L2aOIJPun1tyfJF6xBlQApyC1UuUA0fQFWhMoLHXqO1ZQt3pXMnhlJrjGaLCWjRhmw16NxlcCw3rouWA0iHfwWM65O7C3Yz8J03tJmSg0UHp8HpwudLrNzOn22u2u7OqNQeTq8PTRLV6p9zslplcJicyg4D8bPhlHjfqSITjBipEIeRngQG/qgRrkryqNLpYtdUL+gSCTK3W7k+qBmrUmJ2gc6cb7UfBVU0wOP8WAkqHfAeP6ZCA3Iu8JvTiD+cSd2g4PoDS4bXBNa3gIVCdxQGSX6s7kFgTkVabW2skY4Ng6BDhOnpKgdcpnIqCNWYO0ieYkjq773hm3YHkmvBUgcZk11ucZvvldtsyp+FQOuQ7+ESHJE3G620oPo8Hfc/Q4eDc9YQn9iKlw4YgtYanw/gnCSv0tlKJPrZQejRDfCZP6sLzOcHyuzx7xeXvwak0nRBVE527GPRKUmX1HM2oPZ1blynQCJVojROLPqyG5qk2UYfQ3EDpkO/gEx3e9qB02ACoGXETOsD+yKhSXSxRROdL1VaPD0944aa3BPro0I6bShMJ/s2BSRFP2wEfqBEwItNrdOcK5akVKqisQC36O4Tbu1ugdMh38IkOiZFnyMrSZ2bCMViIjy4treFVOHXIZFz05gxKhxxI++GMwkq5Ma5IFl+qSKnUKM1u8DIF5nySfpmy4C0Vfy1AjcDR6WPNLiZbqE8oU50vkGZVqcinQDkzsSk6h+YASod8B5/o8LYHpUMCBq+aB0dahTI8RZgt0GttXheD5nSQCZCk823QKVNpFuIfR8UmI5jvFjdbo7FH50qOZgiMVmdw93Cb9RKUDvkOPtEhSdO/mqy++PALQq/TybnrCU8Galo4HQZVE1o1WFiryxHqpQYn9K1mPH0DUaCTEmEzFcKCIT9WSK3Zvazc5K5W2U9kie0ud4Pqvk1A6ZDv4BMdXgPkdj43etJu8q0bES2ZDv01iLsJuc56MElwqUxtcDJWj7+rDe5kqfwT4ZTZiFoliRgcPiIBavRfMuJlG2Am6uy+g8k1yeVKh8vDjQHw94ENAaVDvoPSYTPC7U2HXL1ccWEoOVXobcfSRU4f6kO5maKmQH/N9bAGvMeKnUETN/R2r/+qiwEfoxNdImGsXtbmY3U2D9df1xNkaKK+m1wFB9li9O9KgFdQClqL66q3qxcFHaGauVee4HCyqEQNA/9dgaQc6N0qd4pyorW6oXSQPmQP8mnxskqjrVahM/59a5ukH/KyFmoB8n8+MT0+JbNGogTFhiQb0BKa+gT1KzW6MipVeODmZvcVTQdKh3wHpcNmhNubDtmgqnF7PMGkyKC9MX11GsvhZIFQYyczMggLooXzpEsl/a8b8RxcBaoTyrXgBmWh11R2L/iI5FroqcENPj5sZUpURrRdp93PkVzXjI4uBsjSjBJEPTVE1Fhcf58bcCZdaMNurtn50796UnBToKXsogqIRfgYfPJKqytr5deIdT0CPARpFlWJgukK0mSRlnxCuQYcUGq53nLs5Nmd+w5zGbhOgaQgSplAUt8TEW2dUr1j36HX33zr98XLtVaXAc9yahjdhBgR3fFckeJCodSHwd9nNhiUDvkOSofNCLc3HXKt4tCp85sPR4rq0HRfD+ZF6A81Zke12gH9tg5TF/SbGrPz94VLWrd+plQgRp2pm33vw2HAOWqz64tvvp/726J9h8I3bd8259eFkGhpjWjiZ1+GR0QMHT5KqtGDBn/5deGm7Tt37N/Xtt3zlbV1ZjcyIjmSAMq0uTztnm//45Rpdrdvxi/znnyyVbVQBP6k9ZD9a4A53NhoYzGL6O1oBxZvEOFB+MJKYavWrd96+515v/8x7uOJrZ56ysb4e3wCxDdOdPSfsywwd51S3/nVbuTUi30Gvjl41rxfiQ+XSfJdTUz58CMABSMAfwM2KJ1+D7TsMuBkR4wZx1m6YBe6feyjjz6+cMnKA+FHfpo2M7OglAQ7EB5pcHiNyBBHtyD3gmIGMxmhOnJbnJoHFPTtDz+RFIiWIGLEidNn4xKXr14PqmZwhh34yCJdIbObxWoM/qGgs3shQGyhnOXzMxsMSod8B6XD6wVJNqSMjYu8vDygQ+C50AtXgsPhADpMTEwMvdBcwWlPplRPW7r+4xkLMovKOPXmCTUebMYZA6NqWotr+ap1Xbp2LxdJSdc8fuKnkMy2Xfv+/e9/X45YWgXpzl+4RG1G1FAjVW/Zuc8b1Abuv/+B/eHHocuRac1g2XDpa6zu+OTMhx5+6MyFxLvvvudCYjpkQGl0rNm4ddTY8dV1CghcWCE8fPRkUnruhImfpWQXQCKjxozfsmMvcAwxquBYUi3u0rXb7oMRLN4X+/CxqMPHTjp9jNxg/eLr7yAisk3djMXLfvnt9+M+mTR15i8Ohq1V6vv0G7B1x64RI8ds233AwTBvv/vB/AWLh48cvXTlWpnOArHgdjEXk8dPnBR5OoYYsqU14vGffArpxCYkO30sHE+di5/0xddrNmwFllqweNlHI0cdPXEKFBUgM0ZjAbUwM3/xE60dKdm9cfuu0eM+/njS50BRwHAuHxt5KjY+KeOb7yen5RY5CYUHbMH4lMxd+w6PGDVGqgEFosmiM2bPPXLi1MIly0UKLWSsXCj5edac7yZPPXrqDNxCYXRAYjHxSZGnYub8ukBldoId/8mnX1xKyyX6JykjGsaGvgetIL0dQOmQ76B02IxQUFDQv39/Dy7FX8Ltcg0ZMiQ5mTfWYTDMFuvsVVsmzlo0c/nGC2mZRps7rkhucaP+kbNLgA6XrVjzSsfOZUI0NGd0MaPHfwxx3373/b79B5hdHo3FBbQEViPU93sffKizeSwej8Jg++zLb1g8ZErI4KmnW1fXqWQ608p1G31M0LtGbE79NG1G1249ps+ag96HuXwfjhgFLLVq/ZYXO3QAngOL5+nWz/Qb8AawWqunn/5xyoxfFy59uk2bRUuXA4uQDh2Cvdyx04q1GxUGq8mF2OL9YcMh5dScwt//WAZENXL0OLhTQmrOtNlzN2zb+ekXX8G9pFpzpy5dv508ZcHSFY898STEGvz2e3CvlWs3vNjhZbidw8ccOnL8sccfnzXvt8efbLVizUYwDbfs3Ltm47bps+Y+3/4FuMXMub+2eurpWXN/OxARqbM4XunUedWGrSNGjwfSNQV2p8N0yHZ5tXtmfgmkYHIy0Ft/++OUP1etX/Ln6plzfnXjBwbSGTTknQVLlj/3fPtyodTsRqQFpQPmbtOm7dgJE1eu3Th6/CdKI9Af2/rZZ8dM+ATyDzUCFvO23funTJu1cu2ml156Zdueg14f8/1PPz/1dJuRYyd079Hztd79vp887YtvvnviyVYF5TWEAkkVgNvsYjOqVPx9ZoNB6ZDvoHR4vSAtWCiVffPb8i/nL20KmTR74bBvp305L9T/yjJv6UffTZ84c0Gof/OXeUu/mLfk+wUrR02eM3rKvKHfzfrw+9mLd4RxdhsRDabDjp26lArqSM8+auwEqFpgLzCQyH4oICoTGuTrP2Ag9OBWH6u1ucHAAh9gxzJBXVpO4TPPts0priQzVEk63C0gtVVrNz311NMx8clgJ4GJBqzw68LFU2fO7tt/4IA33zoefa5Tl1fBLgRKGfTWkOm/zIWUd+0/1Kt338BLSkyHwEPrNwPxoP7dwwAHQMpgrb7z3tDeffv/5z//iUvOzCosff2NQQuW/JmaU2z3sWKVoWu3nl48UrrnYDgYte8NHfbjT9NJoV7u2Nnk8t19zz2J6XmQVFJGLugBbl0ukg0Y+Obrb7z52BNPAJvPnvfbG28NAYKCRIB6vfj1JwQD69YcVFiDE5ndYAr/sWzFAw+CNXxp4ZI/3xz8dp/+Ax597ImswnKI0rf/6wKpGlIYNnI0mHrwGHF0+N2PU914fBgs9UVLV0B+vv7+R7Ay0/OKerzWOzI6tlIs/2n6TCjdk61a9Xytr0Cu/fzr70aNHQfRU7MLXnrp5XMJyXCLd4cOnTZrTnAVIIebPZYuvPyY8RmUDvkOSofNCCXFRf379WWvL/+Mzzdk8FtpqSmhF3gCtU73zlc/j5k6f+byTdGpBReK5bqgkVITek3lWrdl+wsvdigXSHQ2F/StQ4eNAOV8+NHIzq92s/kY4BuwDtEcFoYdNnykzu61uF1gopE3W2S6io1huvXoRfp3/O7qMklobZ6iCtEjjzy6P+xYm2faqowWq9vzSqdOew5FALet37rzxJkLJ86c79ajZ2pOAdzurcFvz/19IbSu7XsP9Ordx8mCaYhmaQIdvtKx06r1m4AOnfidGdhSkKUNW3fuPxxeUCZ48MGHIk6chv4PDMGBbw668867nD4G6LB7z15AwGCc7TwQViNVAh1OmzlHZXZC3rp07aY1O++8666M3GKn252WU/TKK50hzd59+8YlpykN1j9Xr4NOFGy7D4Z9hAYwGWb+gsUMMjrR93tHjRsfPEuWvHTU43d1bds+N+fXBR07dT55Nra6TnH/Aw8Aq0HEgW++VVWncDHMsJGjpk6fxeA5rogOWXbKzzOhXJAxIL/fFi2BwD9OnWZyM/ArAYpwJCq6/+sDh3404kJS2uoNW59/4UWRQgsG+oSJnwI3J6bndO78alxSmo9h3v1g6NTps7kqDjiYY+mC0MbBT1A65DtuBzrk7ufFDauJbk2SZfAXM5oIufjdocPhCL1wJdjt9rfffvtSYmLoheYNsumaWCr7ZMbvv23YsS0iqlIktjq9l0pDB0t1NndCWs4DDz0UHnkSolSKFW3btYPIkadi/t+//x9XL3HJGWDlrVy3WSBTw2luSWVY5EmoJkvgu0OtWrVatGyVx8cKZBornvphwrNUTA7P4CHvDh85zmx3d3m16+dfoSHW555rL9WgT2ayaNWH9VRsHBiCabmFYIG98+778xcthlaw68BhsKXAbDI4/NZhl27dt+3eb/GyYqXut0VLzyWkQEP58tsfSDrAasejY7U2MlUFjK0pWrtXrrO81qcfJOJmWCBgoUwDdNi1ew8IAObak0+2AgeYrUA/4Fi3eVv79h2A9++6+26SyKgx4yHunF8XfjRylAl3p4ePnawQoWkpdqdrxNhxlsB6TSP6uAcD1iGJ2Pa5dvMWLJ732yJy+vAjj2Tkl0Ch3hryTrVE6WLYkWPHzZg9l6NDIEIge5J1MJ0PRhwHbQNfglWXllvUu2+/yNMx99x777mL6GfZuI8nAZEL5dqvvv1h4mdfwI+V5My8bt17xien+xh26EfDZ8yex/0cIemDFZsv1DbRM3uTQemQ77hN6NCHmyC6K58nbbeQmaVh0RfOXEqz2u1sYMWF18eYbK4yqdmF3u35J3HA0eL2SbWmNRu3fPDh8Omz5uaVVultXr0Dzbf84qvvwEwcP/FTMLPMHjRrcfLUGcNGjJk191cwXOwe5tsfp3z40YiRo8eVCSRu4DaDLS453YHXFRDSNTiZkzEX0JinAy0S330wfM+hsMpa+fzf/xgxevy02fPS80qKKoXAczVSFbDLvsNHzl9KgRQyCkp27D1oRbNCkDkr0Zg2bd81ffbcabPmrN20tahCiJYeuhkggzHjPh4/6XPIf1GVKKuwFNhi3Cefrli7EbKnMtq37TmAPijoYTMLyuR6K7D4qdgLH44YM2X6rIpaCfpGlYfdfSBsxJhxG7ftAlMY0iwXSqGMC5cuP3PhElyNvZh86MhxZAfbfaCBH6ZMHzpi1LJVa4GiODsYCmtzM1NnzBoxeizETcUDv0uXrxkxaux3k6eu3rClRqKCQu05GA55gMwcPhYFiTswm0JcqKSpM2YvXr4aMlYuEMNdIM/R5y7CVVDL9j0HCisE5SIJ1M6wEWNj4hI379wDBvrx6HNHT56B3xxggG7ZsbdCJIUED0REQspc5aK5QgwbnVd3k7uLpgOlQ76D93QIN/J5kCGgz87WYG7w8ZYRb3s6JEe90W9+kU6BRZs7I0dkurBaaSVr8ANdOSIqFAAHc+C5/uCvt6EaJ+afBX3UHvWtnA8mPHQvkjpae273Anl48eIEYpeQWzD4/R/p93FYtMyAi+gOWntgxAsaSAqkerg1G5wZSsBl0oS/8EBgx59A4gJy5cKr4FGCXCLkP0oEMxm4SVMmaUJOSAAfjkvUQnJCNEB8mKBl+Lh0/sfBhxc/QJHZoMxYvahQLM4DKaYvoChEh2CDzv+dDaydwFN//XcnugJPG07eE9AbGr7GDkiBhIFEyC1wRPJWEi3GjymQZlQq0SMcaAm8BqVDvoPHdBh8F1NhIXAhMKI+M5O7ejkoT3B70yEbVCkeL/q8AefD4GX4OovjWLqwWGIkb5XI6nvokcmqBjiSyaKEGHQ2NxhnZI8V0ukTt87qJqckFkQhhIdINOAgiZAoxAE+EJ6kELidy4BnynBrKnQ4AyhLdi+a0RpIisTVWFxkpmtwJnEGPFoLevGJxInyw8UlDpQgXvwHd/cXwebhTGSu7CRNMjxLQprwkG+gCOgqFz24XCQi5EGP45IiaG0oWQimDew8wN0C3T0QXY8XPs6a97vFg5RD4pIwODN+5RhwNvwJ4nRIHogGAgpEVUZSBi60uNlTOXWZ1egLUPz9/RoCSod8B1/pkNyCjJGq4+KcWi3x91it6vh4cHDDp0GRmjtuezq8Gkg1kaPH6zucXFOjtulsaPk216GTI5WbLMQK5EzhvyvY/L1cfVYPqzS7LxTKzuSKSY0HVz3fQemQ7+AnHZJHCDcpj81mq60lp+SmLo3GqdfjUDgPTZqTRkWLpUM2UFnIZGQYp8d7Jkd8Nh+9snN4UR9K9i9t2NtSaVIJZrIb0D+OQpbbo49agI9Y7whPramSG4MrvWn7ipsISod8By/pkOEeJI9HExeHHIEmSByqmBiv3U4GYZowH42NlkyHLFenAYfaZE8sU5TIzFKjy+FDjIg2D8PWxg10zVRupnAMqnegb5J4WLZcYckWak9kCbm69lc3nx7QvwClQ76Df3SIksZfMdRnZID4fbirgQfMVFLCfe/wcuTmjRZOhxxIDXK1qjXbk8rkieXKxHI1mQxiRp+PoKTYjIT8RiGGoN7hczJo1ozO7ksoVaaUKy8WS0lVkjlT9Z7Y2wiUDvkO/tEhG2hM/nmkpPFxt8MO4kmm1fBo6QWlQw5cKyIdKNR4SZ0uu0Z9Jk+aUKJUmD0uBn1HAjpfOo56ayWYCOHUibfISa/Sns2XxhXL8wRqvQXNz/Xi5TTk1yo/nsa/D0qHfAef6NCfLm5JVoEAffX+Svfyh/J6dcnJYCMGewYHa4agdBgCUmXBdVchM5TW6c8Xys7kS2q1dtCULbArd0Np2HdT+YdCtNpQ1RY36/CxaqsvoUx5LEOYL9RVygxkixwWcyGpv+b/DP4TUDrkO/hEhyx+nDw2m/LsWada7X81eKUbcZ4eq1UZHR3s05xB6fBqINUHR1LlxNPu8hhtznyRJjJTdDCpJl9s0Nq9aKc3tH4fCdmoLIQgKU1evzTkPCIm9HkmH2i7VGaJyhaHp9ZkVCk1ZofVcbnpcjXFi0evUUDpkO/gEx0S/lPGxtrr6ti/esyYwNpel8Hgtdu50+YMSofXg5AGBg63x+v2+HJqVNAvH06uTq3WirQOqdGlwh+dsHtZEGJEkpHVEIKkQoT7uUAURXQF5OdXoJcFfYJWZSZXZo02MkMUkSpIKlNoLQ6Xxxv8cHG1c+0n9PYDpUO+g090SIZJg7nw2nfhsmEqKkKnlA5vF1y7mZWKdadzROFpgrN50myBrlptq1JZa3VO6NCdDBLo3C14RSOZrUpm5bQ0agwlP6wHskAe9ONikIDG1FZvldIKOqxU2aLzpRFpQlBsgUjrdNXfjKf+z5Qr1EoLAKVDvuMm0SE5vdrV6wSXCDkShw+D8yfgfqsyfDAKOVA6/Cdg0JJF3CTw1GOv/3WVH9AM0qvQFMeLRbL4YsWlclVqlSa9Rpteo8sU6mUm9GUML97kzIv3G7PhTTv1Dp8eT5Ukws3cabb0yZEcYTgu56QUBmwru/DX7YmY3axE7yyRmRMr1MkV6pQqTUKZ8kKR/GxeXUyeOKlUXqP0rxEMqBEp1v+W4oae4tsYlA75jianQ+JgMC1BQ3G7yddG/8KwuzGQND14C1NySnzUanVWVpbBYGjm1EjpsHGBWx3qvtFUjqDm5vZ46zSWfJEmo0qVUaVOr1JfKlPFlyjiShQXSpQglyrU1Wq71uYj1MiRhwtvYG0OrKgLEb+B1QRDsqGWXJA91zAbZEdyMOwceJJnsAAXlissWUL9uSLFuULFuSL5hWJFXLE8oUSRWCpPLpOnlCvqtBZX/c/T40mheF5o0HNN0RCUDvmOJqdDUvGzZs3q0KFDnz593njjje7du3/wwQelpaUspi4AaUCEL4kPiQuJcAFIggymVeLpw68ShUKhWCwmYUgwkUgUHx/PZSM5OTkmJqZ3794pKSlAxiQ6lyDnIAmG+ABIIsHZI9kgOWxcUDpsCpAKZNCaDT81hoaAH0xGe7XcWCTWFdbq4AiSXK6KK5KfypWAnMxBcipXCsZTtcomN7stbv+W3ORIBI3E+vzvKQlrEuIMHoq8QcEpmPHkIPQRDHwLuBfQM3d3IiQ/MpOrTGbJERlO50qjckAkp/LqonLqTuZKgPWTypUFIl2BSFtQq4VSq012lzu0ByeKQoZgwMhuojZ/O4HSId/R5HQYjI0bNz7//PPBPl999dWgQYPmzZsH7tTU1AMHDowfP37EiBHkKthzw4cPf//99xcsWEASLCoqiouL+/LLL4FQ4dRisUyZMmXcuHHgk5OTA2Hc+AvA7dq1A5qEU0jhoYce0mq1u3fvlkrRWuDs7OxJkyYtWbLEZDLB6R9//CGXyyHk1KlTIXFwrFmzRiaTwaWxY8cOGTLE4XCQW588eXLnzp3vvfceiymTvWz4ksw2Aigd3mQEahCN/gX2bMBy9Uq1uzxmu0tncQKLqEx2OCqNdpURjrZqhblcYswWatOrNRfLFDH5kjN5kqPposOposNpojBOUoVIUgTgCZcOJosOpZCjEF1NEfjDBEVBKaQIz+ZJzuZKkitUkH5alRruJVJZFfjuWBxwVOMsme1upxvtkh6a+wBCCsvpITQcxd8BpUO+o8npkDiITQYk1KZNG2gu0ALAPzMzc+bMmWC6AQVCgL17995///179uwBz7KyMoiVm5sbHh5+5swZ6PdJOrGxsdCGtm7dCkmlpaVBrJUrVwJZ7tu3TyAQMNiahGPbtm2BusABx4cffhjswq5duwJzQHTIwMKFC4FiP/zwQ+BOIM6wsDCkiH/965dffoEoAwcO1Gg0UVFRwIunTp0CoiVtF2h14icfr1y3KSW7wO5A3+pjAvP+ucL+Q1A6vOUgVRmoVUyTAbnOWvZhM9Tt9QEhgdicHmuouAOCTx3ckfgEH+vFIgl6vMhou6KN2xAhRQhurtdZHIrrB6VDvqPJ6ZAD+CxbtuyZZ54hbmgEnTp1mj59Oph333///a5du06cONGnTx8Wt49p06aBQ6fTDR48+I033ujduzfp98FEI6OsgE8++QTSuXTpUgbeqo17KwkOYNDWrVsrFIr//ve/WVlZYHd2794djk899dS7774LiX/77bcvvvji5s2bt2/f3q9fP4lEAvwH7FJRUbFjxw5gmnvvvfenn34CkxHM2cjISBYbsv6SsKygTrpo897zqRlKrY7FxiIZuW1Y6r8FSod8BOaWywx6sxEYn/hHLY+iMUDpkO+4NXQIrQF68w4dOpw9ezYiIuLIkSNkPJO0D7gEHAkOMOOA7QwGg9lsjsNbdQMdEsMRMGHCBDgmJCSAlQlRSKuCu0BztNvtL7300rx587p16waeYEf26NEDbMTHHntszpw5p0+fPnr0KFAmsKBYLH7iiSfAJLVarcCRn332GRCMxWK5++67gZ4hb2BQAq1CIj/++CO5L9fcl+3Y/+eOg1FxieTUE/BvWPbrBKVDCgr+gtIh33FT6XDFihXt27dnAy1g1KhR3FXwAU4CW5C4wYCD8OPHjydXwYwDXgQHMBkYcMTz008/ZTHVZdb/5C85zp07F8gPTD1oeenp6X379gXmAEOQS5PFrx7hCIbjCy+8AI5NmzY98MADSqUS3C+//DIJA40byBjSJAxN4MOjsuAorhKs2x9x+PT5OgX6kKk7MB+nYfGvB5QOKSj4C0qHfMdNpUNgspiYGHJKGgQw0C+//AJWoM1mE4lEiYnI0oJLhYWFDKYcsPDApqyuriYsJZPJgJxICtnZ2cQRFha2ceNGCBNy9/PnzxMHmJ4XL17U4k8EQ7C1a9cuXrw4Ojqa0KFQKASjExxGozEyMpLB9iWcAnmDKXnhwgXIG3gCV5HbEZC7eDHgtFIoPhp7cdWesDKBiA2ankqO1wlKhxQU/AWlQ77j5tFhMMjVa7eba6fA4WrBiH/I1WvfkeCKebviXbhbkMYNiElMX7Rlz4JNu7kAweAiXg2UDiko+AtKh3zHzaNDJrBkkLhJAGJFkaMPL+wjVzkHcXPGFpmxQhLkmh1ZIBg8mYU4yCxTcsqtIPTitYMhaXK5Ig7iDs5b8O2CQdJkcOZJML3JnJxdMHfttqyiMpcLrfrggtWLeSVQOqSg4C8oHfIdN48Oby0Iq63cddiGt/Nuiuw1LLhEqZ62fMP+E2crBLXEB2+P4mdoLhgHSocUFPwFpUO+o0XQIcmP1+ubvXJLUQV6xcgNbzY6QjRgttgiYy/OWrklITNPrkYvL1lkzl75zSKlQwoK/oLSId/RIuiQAOgwvaBk2fYDxERr0hySxIPvsnTb/jV7w9EIqhuNx3q8Xg/aNqSerigdUlDwF5QO+Y4WRIcs5qfU3MLFW/YGv2hsUpBbMIG3oTa7Izm3MCz6/Ipdh6ITUg14liy5yuDJq5QOKSh4CkqHfEcLokOSK7fbPXfNVqYpx0tDwCkkeGOt5JyCgydjFm3aHZeeZbXZSLC8vDygQ+A5LgpzdTVSOqSgaFagdMh3tCA6ZAO2WkpuIRv0Au/mgNyLCZqq6nK76+TK3cejZ67YuHDTbqfHV1xU1L9fP7IL+V+qkdIhBUWzAqVDvqPF0SHJ2IJNe8DhDiyruJngtBOiJcjMhaS03u8O+239jtMXUwRiKWe/+jBIYC4KpUMKimYFSod8R8uiQzbQEP/cfjCnGG32dquyyt03WFsFBfkDBvQvqajeF3V22p8bIs8lFJRWKgLzUdnAXuEkFqVDCopmBUqHfEfLokMub+dTs5bvOOjx+NnlFoIoiuQqLy+v/4ABHo9/8f7BU7Hz1+5YuTssLi27UiS22h3EH01J9fkcDseQIUMoHVJQNBNQOuQ7WhYdskFm2fnkzDV7wxCx3GpG5EBmloLZx+J8kr1zyCWVVp+SW7jp0LH1+yMiz1+qEIq9Hs87Q4YkXEogL0FxqZqpzikoWgIoHfIdLY4OCYAFrXb78p0HWWxsNZPcBi+0IFligvauA9idzrIa0b6TZzccPPLruu39h7ybmZlFLhFe52L5U6SgoLhZoHTId7REOmTQ3qSoOV5IzTZb0dcqOCK5tbjiukOizGBShFOFWptXWjnqq8lfzV60ZNt+iVJdL3zQsDCXAheAgoKiKUDpkO9oiXRIQL7Wu3zHQaPZ0kzyfEU6DAbJIcmq3W4fPHhweloqi1f3y9XahKzcqYvXzV61ed+JMzq9AUzJ4CczsPFAsygpBcXtB0qHfEfLpUMGf79i0eY98ek5bKCB3lr8JR0SEPWSmaWJiYn1VM0wEoUqJilj8qLVy3bsPxITB6eI732XwwRGVemwKgVFY4LSId/RQumQZM/r81XV1s1ds9VksTaH8dLrpEMCoMMhQ9BCi6spvUpYd/zCpTmrtmw8FBl57lKNWKI3+b+cTOBftnGFqBQ3AqJDokwfER8Sb2MISYoky9UXrbVmBUqHfEcLpUMO0C41euPUJev4SIdXXHfI6R91xN7LhdIbzTnF5RFn4tcfOLo57PjWsKjk7AKxTMFFdOPvQPotR/7UYBOBFB+pEe2uB+LDgtx/MYGXYfQWh8Zk15gc1XKDQGHMrlYhqVGDZHFSrfILdxpyxIJiVatyBOpyqR5Sk+mskLLZ5oKKCr1vEBi8I2CwBI+Uh4amaCRQOuQ7WjQdMoGdS8PPxLO4jd7abDcKHXLgKgJ6Q/KilMBktZXWiM4lZ+44cnLjoWMbDhw9m5haKRJzAcgCD04bt1YnNwdcSYlJR6wxxHxXAqhGZ3EW1+mSy+QJJdKEYmlCiexisTQeiSyhVJ5UrkyqUMIxtVKdUq5Oq9KApMKxWptarU0jgj2RcKf1j6lcYBwspQIllVyuSqxQJpYqL5Uq4ovITWUJSKSXSmTplcrSOl2dxuK7SpVxpipHj2zLqN+bA0qHfEeLpkM2iALnr9vBkq8Ehwa5eWhcOgwBVym4x788T5VFu6d61Dp9al7RsdiLQJDTl63fdCgyJinjir1qvToOpNmcQXJ4fRlmSiX6uELpiQxhZIbwSLrgQpEsrUpdVGeoVFkrldYqlbVaZRNpHTKT2+hkHD7WyfjFFRDwtHr8YnKxZhdrcDD/VJyMyQXCWtwoWZuHtXsv35HLg83LQki11Qs5rFTaIMMoz0prhcKaXKGOyZdAoY7iol0qllXLjBaHf8OHhghR11/pjQKB0iHf0dLpkAmssli569DFDDSnhnjWD3WT0KR0GAxSQFJ2X5ANBE+yxWYTSGSXMvMORMV+v2Dl/LXb9kWdlSrVbjcaSr2cRANeJD7BAW4tuCwF55C7hCxmj9fm9NSqzMmlioOJVfsTqw4mVaVVaavkVqnBJTE4JQaXyurRO3xAQkA/nADrEKoDRjQ0EGMDgZAkMHHcgDRM82q3NmHKhBzafViwA051dp/S4pEaXXW4aOUKK1ir0TmSY5nAjoKobJFIZXK60WC5t8EYSbAKQzRJEQxKh3xHS6dDNsAKheXVc1ZvgaZJWuotyf9No0OC0AqrX2Qf2qnAUSOWnEvOmLViww8LV67eE5aeXypTaQ0mM9ESB7IJwD9/QUUiNkoKyAiun4jV4TbZnGa7K6VcGZkuOpBYfTRNeLFEWSw1a20+jdWrsfqAUczYAiMCbvPVCYnQTzORhnkLFnPAsuTKBZ7AkRqbVwtMafbElyrD0gSHkgUns8S5Ao3KaDPbXKAxd9BLSqLSG66a2x6UDvkOSoeXmU8okf++YSdLhkxvRf5vMh02RGgVBhDCKxqDMfL8pRU7D8IPiM2HIg+eOpecU1BaLZSrNMHBGPzNEPIakqRAUgsOEwJylYTwXt/vEn8UPOEl2NKtlhtBcoXacNzLn86TAiVwg5nX5g+T8x8Zc81ZjLho1xCTi7F4kE3pZFiLiy2XW49niU/lSM4XS6sVpiq5QaqzEA37sJFNdP6XNdsSQOmQ76B0iMAEevyImHgX/CDGT3looKbHLafDKwJXJapQ1P3hSTbBV4sqa84mpi3ddmDV7sNbDkceOBV78mJyekGJyWINDsYGZq6SsbirtRDib3M4KoVoas+1LXXij6eH+OkWoDXbs2rUaVXK6DzpyVxJUoXGw7IgoFPo68mruEC/H0oVLVyCmRKNvmJFwU8HN4sErOfofOnpfMm5QnmeUJMvCvrQCp5ze7U6bTmgdMh3UDr0Az3SXq/BZEnLL2Zv0SzT5kmHIWACvOjB9Mb5W632KpH40OnzW8JObA47vulw5IaDx7aFn8goKBFL5Xbn5UKBarlFHRw3Bl31OZyuyHOXjsag6b7kFiF1QU6JdcJ5JpbJL5UqLpbIYwvlqdVaiAYC5qDe4dMHWBB3+pQIr1cINYL2QOAUflWAukGTcSWK+FJFcqkysVReWOvnRdQwcHVyNdLSQOmQ76B0eBmQZ7fbs3pv2KmLiGNufhF4QYcNQaobvVjC81OCKQpgttrq5KrSGmFMUkbE2bhtESfnrNryy+ot28KjsovLFOp646ssGfbEHUp8WtbPS9cVVdQQT3JkgmZzCFWm4xmitCpNkcRUKrcQIwasGUJ+aMDTRa3AxhTu9wTRMPzUAII0u1jQf7ZQfyZXklPj3zuX1JF/VOGmP0e3CpQO+Q5Kh36QDEMz1ej005atlyjUN99A5CkdciDqIrXvw9Z2CDXCucliFUnlBeVVcWnZmw8fX7R510+L163eExYefaG6to77piOLln+43/ny5/HTfzsai8xEnDgR1uHyHEquTihV1qhservPid8IcgOhXMdNpemEG1AFN+jf7GLEOmeWUB+RJozMEOEK5NgQtwquXm9fUDrkOygdXgaX56gLSWv2hDO4T68fpGnBdzoMBlEmaQnEcGzYJBxOp8Vm0xnNWUWlp+KTl2zd98OilT/+sXrf8TPRCanlgtqpS9aN+fnXYd/NNBj90zckWuuxDFF4mlBhcWttXjIphltjQLrphn03laYQ7peHAU/AgboAdlSYPXV6555LVYW1OofbTwxcY+Cq/rYEpUO+g9JhPXA5r5UpzWYLabU3rSy3Ex1eDUSZwe2EIDQcy6bnF7339YzBn/80ftr8sbMW/7hsy4mMGqubNQV6YWoINh8h1REsZPnjwSRBRqVarrex6PX8bU6KlA75DkqHVwDJ/Oo9YeQk5GrToSXQ4TXAtRyJQrl2b/g7X079Y9Pujfsjlu6NOpUtNHn8s0ONDfpiKv9cCIdprW7ibhjg+sXoJEfG4PA5GDazRnc8q9biQK36OhfP8BSUDvkOSoehYAIje79t3JWaV+jFaxBvTnFaOB2ygW7iXErGlsOR0ZfS9GZ7scQaX6Z1owmNPr0dLZM34QkypLcl3a4JbYQGV73ETY5wCp4kJPGEbhp8gmMFuu/AoF/9BLkA1ylcmuQuDW90NYEwkFuQhj5c/m9MuLIEKQEVM1guF9+O+nHutGFqJqxVvc0TnLIu6JQT7lRn97kYNJodUyCpUhjZy8MD9Sv+tgClQ76D0uGVgWaC+Hxhpy8Q980pDqVDNtBdejxesdpcLjc7fP5O3ORmdVYPMl/wjipqs1Os1JOlchBBY3bmFFdYfWglAJpcw7KJGTkVIpk3qH+HqzKtRaI2kVj1+25GaXTUKvSB15A+gVRNrJzrl8CNWJFcJ1YZVEY7FMTsrnf1igKkcjI2/nxCarDPmbjEsxeS/GVvEOU6BdIBBablFYG6ICdwCooSybRipaFWgTJZpzJqLS6Dk5VqTEdPnZ37+yJgu6vd1OljE9JyjkefJ5vawGluSWVY5Gmr96q/HjjlQzbUVm9cCfqCCn6gQqr9dgClQ76D0uEVwOXfbLVdzMhlr7L6rdFB6ZBoGI46syMsVQB9qB6bL2CUeBg2I6845mISOIAU90dEdu/5mtnDqs2OWXN/e7JVq+49e7V59tk/lq1wM+z5S6k9X+vz3PPtp8+aRzp3MGLOJ6a+/ErHUWPHE2JAPTVajIE7a4YtF8n7DxgId1ebnDaG/W3RUitmYq5b53r24I4+cMnPPcTn6dbPPN/+hWfath0/cVJJdR033zWEIThPyNvYCRN/mPKzJbBdDhTws6++/fzrb0mwYAm5+xVPufS1Ng+UaOXaDXUqg80HN3Lv3HvooYcfad3mmWfbtnu6dZt2z7+w7/BRl4/5+rvvx30yadrMX4zOyyZ1SIKQ1NzfFg4bMdrqRSYmnO7Ye2jAwEEubLuTKA0zSXzgNwqo3eJmLxRKWTTHuGkfpVsCSod8B6XDq4I069837JQoVaHXmgaUDlnMhU6X52yupFhqJlxowoQB7eliSuaRk9HIFrS41m3Z/t//uxO6+G9/mPLIo49GnDhdJhCHRZ4aP/EzoVTVvUcviURyJi7p3vvuwzTgNTmZD4YNf+CBBwe+ORhYB5IFm4az/4xOr8vjWbJidU5RKeRh/oLFxdVi6PQtXpaYPpAI6dnh1ISZDxwWNJcSObh+H6XmZt8YNLiqqio9r2TIu+899tjjDgYzhBuNNEIAjmXBQYZDoXQjRo399sefgIbRjqleVMCPJ30+6YsviXFJbgpuG1pPgu4IgvZTxbwO2eDyQC4hSsN7ralMaOHKijXrwZK2Mygw8GJmQcnGbbv+9a9/wW8LMO/gEjS4qLMXRAr1oaMnzW6UW0LMgdL5tQTP9Mw589/94EObD+kBamrrrv29+/YD+xwKEpwHg91Lcks+xEGUA6mZXez5QnmhkKzc530XEQJKh3wHpcNrwccwLo974ebd8anZeBFd0667oHRINBydWycxOklPSnpY6G3hQmJ6zrHTMdCwtFbXxu27H3jwQXA//sST1XVKO6Yc6HD1Nu+KtRvav/Ci2QNdNvPbomVg+UH/FBufnFdS+cv83/v07Q+9uc7qGfLO+3AvncVFrDrgJLeP6d2n3x133DFt5hyTyweW1aB33h3y3vsp2QVPPtnq8JEopdHe9rnnN23defTE6Y6dukCw6Nj4F17sYHa59HY0xkjoEAxQaP9g4UH6fyxdrjDYVCb7ijUbiqtq167d+PTTbcA/u6jyvvseyCmqXL91e/iJaLAO773//ikzZg8dPrJbj14ihe6zL7+5447/fv3D5E+/+PrZts9lFpZt333g/gcePHcxsWfvvn37v34+IQXSTMrIGz5i9JuD33b4fDv3Hbrjjv8dNOSd+OR0ldHx9nsfJKTl/LFs5UMPPyzRmAivE/Y9GRP3f/93Z0WtDDIJZJZZUDrx86+SM3O+/n6yVGuC0wcfemj3/kPwI+Pe++63Yf4m5uCsub9+OHzE3sPHwLyE090Hwu+6++7jp8+u3rj17nvuAVMU4j73XLuUrNxvfpxy3/0P4u9bXX6HasSbiWdWa3OF6mt/wZiPoHTId1A6vCpIEeAIZscvq7YSd5OWi9Ih0XB4qgAvYvObhoir7Ghw7VJa9rHoWB+yDt2btu+GXt7HsB07dpbrrNimQVGgf/990bJXOnXGZhazfM0GsCvVZuuI0eMg/clTpw98cxCysey+2PgktHg/MAEHU6lrzLiPwWyCPh1uwbDMw488mpyZXyWWTJk2q2//AbUK3S+/LiBZferp1nI9Wg3ZqnXrSxm5QLocHY4eNwFzttvFMDv2HhDJtU68Y9ypc/GpqSltnm3rY5m4xDQgJKkGzS6B+h41Zny/AQPBkZKV37lrt6iz5yd+9kW759sDhylN9p69ek+fNffljh2nzvgFwucUVz7dujU4wPiDnwhbdu+7//77y4WynfsPP/jgQ1mFFcDDyVkF991/vx0zzoSJn0JWCauR3xanYuPvvPOuSrFca0FGH9h8epvbhXOycMmfhRWCRx57jBTzu8lTud8lLKLD3956+91OnbuePhcPNbX30JHHnngc/MGaBPbFSc3r2rW7C+8Q9Gq37m6WIVNvOEYE9i2UGC8WSz1N/OPy5oPSId9B6fBaYAIbhkVdTPJ4/F8xCg3UeKB0SFpOeLoAjWcGzc6ALhUs9aSM3CNR0T4fGF6u9Zu3P/TwI9DKnm3bTijTmN1oHFJn86qM9qXL17z40suQgsXjW/TnSgizdOW6Di93zM7NGz12QudXu+nt6OO9lqBhQOjxtTbEuF26dH2pY+cJEz+zuH12hr377nu++X7yx59++c77Q9969wOBVL1t9z4rHicYNnykRG2EPr3Dyy+fPnfRRUZE61uHLo971fpNUq3F7PIsWrbi/aHDRo77+K677gZm0pgdH0/6fMj7H/w845eiShEaLP1hMhBVel5xr959Dh09ARw2bsIktdlp9fqGjx4HgYGA9x0+avX5ygSSPn0GiGrrPho5ZtDb7/Yf+MZDDz2cmJG7cduu3v36F1eJIMyBiOOtn3lGabC53R5gOLHKYA8QdjAd6h0+aN9gm3p9XrCYQTOff/VtXmkV2L4Or8/u8837fREa5MQjqCx6d7iozTNtT+F9ggBbd+3v02+A04d+hYz9ZBKEgN8TYyd8orV6DA73l19/DzolU085IXSYUCyjdEjpsLmB0uFfg8FbRc9csbGwvIrzqR+kcUDpkEziLZfoL5UqHYHXdSZsuoG1prHYBg15G00OYdmXOnb87KtvXAw7cOCglzt2qhbWgWdhpWju73/kl9U891x7OFUYLY888qidYSpEsvOJaWkZGUCHXbv1gE7f4GCORp1x4bdciBo9PoeX+eTTL/QGE3RUK9dtqq5DL4wffviRsGMnWfyaSyCVg523Y+9BO9o3lR0+crRcZ4Hu/uVOnaLPJ7g469DFjv94EkQBJps8ffZ//vM/EPtM3KX77rsfPGMvJt1z771gtgrlWqEMvULbumtvu/YvTPr8q+8m/wRxwTDt3bff4aNRX3z9HZiPeWXV2BZ8ZvOOvR+NHN2vP+pAt+zYC+V674MPv/zmezj94uvv77//waTM3E3b97z+xpvlQgkYhWVC6WOPIbtNZ7ZBkeV6K/duD+gQ+Pvee+9D1qEVNbatO/flllaDo6RKHHX2IuTh1e490NZ3DPvrwsXcOCeU+pf5v48cM/ar737q8NLLKCc79/Z//U20lMLu/XjSZ6AmyNsTTz4Jl8pq6u677wE7ftkZXI9SozumQGqwOsmXoW4nUDrkOygd/gVIQaD5llYLfl66Xm+ykEniTVFASocMXvRpdbqPpQtVVhfXERvx1ETQy/PtX2zbrn2ffn269+xVWasAq66kWvze0GGPPdGqa7fubZ97How56IKhm+7Tt1+bZ54dOmy4Cc/pIJYIXO3avacDjWR6evbuCz5omYEDLcxYv2XX3ffcAz27yuS0e7wD33zL7PKt3bj10UcfA25o98KLi1esESl0G7buINuqvjHoLZnWDMk+/uQTx6NjycpIE57w8q9//QsYrm275/u//saho8dtHrZObRww8M3XevUaOXbCPffcA4R67lJqmzbP9hvQ//FWT67asGXIu+9/8tnnED01p/CFDh32HAgfPnLMCy926N1vwMOPPDL244las7W4urZz1269+vZ9+JHHlixffSAi8pFHH+ve8zUwOv/njjvikjOAxTt17lJSXWtweMGmXLdpW+/Xeg14462XXu5Yq9CRqTQm/JY0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>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAloAAADhCAIAAACfq4wiAAAp40lEQVR4Xu2dX4gl2X3f+01mHiK9hO6nxSBQ6yFiDFZoQ+OMwVgdvP2g0EtoBQYFNcYSBHpWL2kI6/HEmmWTTFjPJgtymkSLG60lYtzbySJHa5jVGmazNtm02aDpkdtC3tuwEpoH6cntp658t766P/36e6pv3/5Xdbvr++FwqTp1qurUqXPP5566954zdXBmfvjDH7/44n/tVcAlaykYY4y5zExphDHGGNM/VIeVMcYYcxUR3wnWoTHGmF4gvhOsQ2OMMb1AfCecQId7e3vr618fDH6K8OjR3trabU1hjDHGTCriO2FcHcKFFGEONqIxxpjLgvhOGFeHGxsbpQ4RdnZ2NKkxxhgzeYjvhHF1WIqQ4bnnvqJJjTHGmMlDfCdYh8YYY3qB+E4YV4ePH39QuhDh3r2XNakxxhgzeYjvhHF1eOfO86ULd3d/pOmMMcaYiUR8J4yrw6owIly4vb2tiYwxxpiJRHwnnECHYHd39+7dFxD8jNQYY8zlQnwnnEyHxhhjzCVFfCdYh8YYY3qB+E6wDo0xxvQC8Z1wjA43NzfvjYfsaIwxxkwU4jvhGB0aY4wxVwPxnWAdGmOM6QXiO8E6NMYY0wvEd4J1aIwxpheI7wTr0BhjTC8Q3wnWoTHGmF4gvhOsQ2OMMb1AfCdYh8YYY3qB+E6wDo0xxvQC8Z1gHRpjjOkF4jvhxDpcW7uNoLHGGGPMZCO+E06mw42NDS48fPjw8JY+cvfuC3k+5DbD5uam5qZruiqNV175pmalf6DwHz3aKwunnYBTa4ZMd+AdUd6jfoayZorvhBPocGdnJ6/ev38/r/aQ5577SnkD2gkTOGZ6h6WhWekfHRY+g2bIdEd5d/ocpHDEd8K4Otzf39eo+sGpRvWJDtsg6zAHzUr/6LDwGTRDpjvKu9PnIIUjvhPG1eHenvY6yZ07z2tUb+iwDbIOc9Cs9I8OC59BM2S6o7w7fQ5SOOI7YSwdPnjwQKMSE/g9VjtIG/T6628ylLfk7OHevZcPr066Dnd3f/TSS+tvv/1eeS3nHjQr/aOsit/+9sNYlbvwjW/8D/l6CQlYdR892uOh8Prii1/NaUYHzZDpDrk1uN35nfj48Qe4s3jlauM7lDWkcdOJwvvv/+Sdd74btWv8trGsogzHfuzDjhIjhSO+E47X4Tgt7+7urkb1ALk38/M3ytszIiwsLJSRR4Xl5Zt5dZyb0jJSGk8//Vm84s1QXssZwxe+8EWJ0az0j8aqODMzw9VnnvlcbJqdncUnFSx861tvRWROwPCZz/zm5z//W4Om0m4MmiHTHfm+xO3mO/HVV1/70pduYeHZZ9ewPGi69bLLWcJTT/3ioOkURwVWtsYqyoBqWe6VQ9T5CFI44jvhGB2ur69LTCON3yxeeaQN+vSnfwV3kTcSdwWfyLBw9+4LSIa7+N57P0AjBUmwIuKD0qc+9Uvr61/H53H0/JAG8fhEzzSIn5qaGtSfhnAERF46Hc7NzbEoEK5fv84FOhKXs7i4iPQsomvXrqFA4vJRVvhgOD09jQ96fOvm8kG54WMEyiefS7PSPxp1iELmam6PUDPLD+lIEFWXLQ51GKWdbwGPz9sUR9AMme7Id5a3O96JbFXycukqqSHSOvG+v/XWu6wJ1A/fwniNI/CtjSaRp2DtYjZwNNQobsLB8R5HYrxGZZMMID3OyPSsnJElnjG3Fdg9LpZBCkd8JxyjQzMCaYOmaiA5LH/iE58c1A8MP/rRj3EBdwuV6f33f4JVfu6O3iFuJxdgi0hz48av45W7Q5mXTof4YIjKyndFqUNeIz8Gxj808uXH+xYJcvkMmvormpX+URb+2trtKMPc5KGhQTxrVwQkYO0dHNbhYFjacgviNkXQDJnuyPeFtzveiePoMGoId2lsnQbDioGU8RaOQ7H1GwyfaUXtYtvIwLPHwfMxG6souhNvvvmXrJyxF8+YLwppEPKOUjjiO8E6PD2NH8kZ+FEFH6DiVmFrJOBNDR0iDQc3YEeQkWyMYvdLp0MG1G+8W0odchVXh6q/urpaXj4+AaCU0KzzvREJeEw5i2alfzRWRWk1JORGJCdo1KHcglzVGTRDpjvk1jDwnZhvOpcb64bsUr49ET7ykV/AmxS9sfwW5ia2foNhIyanQLsXDWPOz6B4a3MrJIreISSHc7FyRpZ4xmgrsIxuqzxilcIR3wlH6nBlZYULGxsb/XwWeiyNbRBDVAgI4N13v4fPWag0okPce2zCpy1UFz55ePXV10SH2B03GxXxcukQ76LNzTcGw8+JuFJ8uLt372XWb1wjavY773yXtZ/1WC6fD+Liu4con0H9GFb+cq5Z6R+NVRF3Ae9iFiA/NaPMl5aWEI9lFGOkH6FDlrbcAutwksn3hbd7MHwn4r7zEToaFphjcLhu5F0Qw10aW6dB/Q6Nj7l8n0a3LFo/fiDLtevx4w/u1kNGsCnAubBXNBesbLmKIj1TorMYOows8Yy5rXj22bU4F4MUjvhOGFeHOzs7yFxEbm1tYXV7e5sJUEzD/XpEY3+oDKhn8TuuowIqwVG/45K+P8OE63BQt8U55/nq+KbKMajc5eXn30aOKJ9BUeN7yJhVkQEleYohbHwLLgtya3DXpA1B/0meUpa75Boy+tYz4N1K7+Zw69atMiWOlg+OD8roFUgayUBuCuIgSBNnjATldUnhiO+EcXUIRccmnJJD0jANPiPEpl5xojbofMPk63BE4CPTcwyalf4xfuFfUNAMme4o706fgxSO+E44UofosXKB5oMRETM7O4tlqBHav3Pnef4HH8uxV6/osA261Do896BZ6R8dFj6DZsh0R3l3+hykcMR3wpE6hPPY5l67dq0a/hOfOlxevskFjmJqHbYfrMMcNCv9o8PCZ9AMme4o706fgxSO+E44UockD9stQ3jLag/psA0a8/+gbdJVabz77vc0K/0DhS//fGgz4NSaIdMd5VdxvQ1lzRTfCcfo0IzmXhe89NLEuZBoRltBM9FXNjc3tWjaorfDNE4seof6SlkzxXeCddgNnjAy49IwxrSA+E6wDrvhnrs1CZeGMaYFxHeCddgNFkDGpWGMaQHxnWAdGmOM6QXiO8E6NMYY0wvEd4J12A3+8UjGpWGMaQHxnWAddoO/Lcu4NIwxLSC+E6zDbrAAMi4NY0wLiO+E89Hh6uoqxy9dXFws//k4AuyFpnBvb083HCYfE6dIW8ZlZmYmljc2NnBevKbtY1FeWkx9VW4yxhgzUYjvhHPQ4fz8jdUaKOH69esn0gzSr6ysTE1NLS/f1G2JfMzTTaCRZ+RYWFhAbvE6+qQl5aXFYGnlJmOMMROF+E44qw7RPcrjZ1Jvc3NznAcDfTLEcHRTxM/OznJA8ABa4gIOgkMhDSyF3at6So2FGu4bx8QB83HyKWZrnjx5wmTYBEMjJSJFh1zgSbe3t3lMRuaD5POWq2trt5GSs1zlTRzuPJ/RGGNM54jvhLPq8OHDh/lRJ7xCJUAGu7u7lArFwHjE5PShQyTmzwuRjI9DeQRujWNWqXeISDkFPHTnzvO0HZNBk3ye2ahDnpSbsMyM5YPk85arVeod5k3j6NDflmVcGsaYFhDfCWfVYZUmCq5qCfGxIWVGwVAMjIecQnJV0iGfWzIlel2RADHYJY5ZJR1CRfkUWKb52LlkMvElCR3mk0KcOJQcJJ+3XK2Kh6XctLW1JclKLICMS8MY0wLiO+EcdLi5uTlVA5dkHVa1k6anp+m/Rh1yR2gppk7ELpxAETtGX1OOOTMzEw9L8yn4XDTrsKqfpgLRIVaRkifFK47AvarDBzlWhzjL/PwN2VSescT/tMu4NIwxLSC+E85Bh+ZYYM3t7W2NNcYY0yLiO8E6bAn0ONFlPOlvWY0xxpwX4jvhNDrkw0BzaqBGf1uWcWkYY1pAfCecRofmFPD/G/GzIwsg49IwxrSA+E6wDtvg4cOH6BTmP2haABmXhjGmBcR3gnV44Typ0VhjjDHtIr4TrENjjDG9QHwnWIfd4H/aZVwaxpgWEN8J1mE3+NuyjEvDGNMC4jvBOuwGCyDj0jDGtID4TrAOJ4L9/f3p6WlYIcaWu17PDRLkP2kQmRvkvIifv+L4+RdAHLWOs1oeBa4idsHlcCCepaUl5NwTYBljOkd8J1iHE0E5wGkMbk7EhVXdo8pzYHEajb29PQjp+uE5sLDMkV2rNO8VXmOYViSYn7+xtbWVp6xijy2SySvHE8j7VsMh0avaqchJHpcuNG+MMV0hvhOsw26QH49Qh5ydkTFwDLpi0RsTHXJ3DpvOGNEhIzkHFhJvD+EmJIsjRwKemr1DHj8nCxHGLCLlvnFeqDTrkDN2jcA/pTHGtID4TrAOu0G+LaMOYyqr6rjeISf9gALhIUiUy1WhQ/T2YBr2IAGWYxMUNVvPeJwTVEMd8vg5Wegwq0v25cxcyAk6i7iQmCc5uqFH4e8OjTEtIL4TrMNuEAFAaeyHhULgv/z/fdEhH1Sya0iVMsHS0hJ1CC/imOzGIZKTOFbDDhzjITPGI0E1FCpFyOPnZPlhKQ8o+3K2rCB6h7DpsQMRWIfGmBYQ3wnWYTc0Ph4Uo4yA39VVQyPKMp0XCuSyCCkmOiZy6nz8nCzA0SKe+x7bBSSNamwsDWOMOV/Ed4J1eAWRB62TBrqSMoKrMca0gPhOsA5NB9CI/FVq2Vk0xpiLQHwnWIfd0PNvyx7WU3zwXxzQYc9LwxjTDuI7wTrshj4LgC70dFfGmJYR3wnWYTf09scj/imNMaYrxHeCdWiMMaYXiO8E69AYY0wvEN8J1mE3+PFgxqVhjGkB8Z1gHXaDfzyScWkYY1pAfCdYh91gAWRcGsaYFhDfCdahmUTKGa9OAQc05zLn3Lh16xb/4IFNOzs7HHm8Go4wh9WYZrIaTjk5P3+j3JT3Oh3loDx5Lsmc8wwzszKc/xJsb2+vrq5yssyqvkwch8uIzMXIod6N6TPiO8E6NBMHxzHnuKmQ0PLyTWiATXxe3t3dzbMtwg3wE/eFFbC8Ug+DzmNyHFfEc3RyWq3UYR7fjss0imwiPEtV5+R6mlEyJpuktziIOVeZQ84rKTblapnzDHVYDUdOr9JcKFxgUYQFrUNjMuI7wTrsBv94JCOlwUacr7ALu020RV5GgodptkWKEJHo9nF4cWwNqVAG8BBEgp5ZSI6TStKRWM3TTE7VcKIP2UTChUgmM0rivJwPBLtjF3o3clg19Q5xtDLnO4mcWHRY1ZOQICdMxsvJW40xlXU4mfjbsoyUBtp6dMU4aTDswmkUqZm8jLY+JiIGnCpyqp4SmS7JOqzqfSEbCAO2oE7G6R2yz9fYO+ReyEO2TkwnQk1Sb0wZOayO0GGZczg4Qk4cOqT5cFE8bDZuXjDGVNbhZGIdZnJp0IIEBoJd8Do7O0t/5GV4iLMTl7LhgKjwX9ZhuAEuYS+q1OGH/cGaaqhD+Aynk00E0uIqcoIeajws5V5w261btxDfmEMky4eqhnlozHlJ6BAnwilwNE7vhQJBNmIiTJIP9aQmVo3pFeI7wTrsBj8szYwoDTT0sEg8KszLRFaDo+IviHJGSdIYOZqT5jx3kavDU2A2giLlzMzG9A3xnWAdmokGXTR+e0fy8hWAP7QBfAjcGpxLBGVrL5peIb4TrEPTPXxCaLriin3IMOYoxHeCddgN/u4w49JoGfRHYcHl5ZvuHZpeIb4TrMNusAAyLo02gQttQdNPxHeCddgNI3480kNcGsaYFhDfCdahMcaYXiC+E6xDY4wxvUB8J1iH3eBvyzIuDWNMC4jvBOuwGyyAjEvDGNMC4jvBOuwGCyDj0pgotra2VlZWYmQADlzOscvzPxRzfFUPmIDlnZ2diM/DnY8gJ74znJ2KbGxsICcRg9UYc0eSHXu6PHYPslqOe7C0tHTspB8cHRDXyKMxDxx7L7ZGZpjVfEWyicigQieCI+JmYvS+Ko3kPprylqF8ODUKiVWcjoPixo6xfFkQ3wnWoTHm56DJk3/ll8Oal8uzs7NciEHp8sSQoymPydFccYRo7jkS7MLCAgeGXVxc5DQmJMaerYYzWcYqxEPf4AhYiJmwgvhV89zcXIyrHpHYPf8phfsi5fLyzSoN786tMfJtpK+KacLyJsKMcTnOi2JEVsv4qr5BXEUaiFZGAeQqXjmCfN50FPwQEB7loMEwN0s4VvdrsiaP/fQwgYjvBOvQGHMINKNoZ0Mq19O8x1ldEQ9hlB2F8XUox+d46NXh6TgYA52wdwIbiQ7jCISNO/1EYhn7oolnhumbSEwdsuMI1e0M59sKePnz8zfY8WJm4uxhR65y33xFsolExuK82IoywSt9kzMZ6XnAxnlRquE8aKLD6USOJ+WUYUwWq+wEZx1eRsR3gnXYDf6nXcalMYGgj8gWsOy9yTI6IuUdzHIajRwTPRu26bk1z70r9syO6h3O1RMsM00+QlZjNbw6eBHmYGLqEBeyMKSq+0bR8a3qXhfcj31xinhGGmc/qncYVySbCDfl82I5z4uSM1mNMU1Y3AvR4WYix5NSh/KhhHtZh+b88bdlGZfG5BAzQKHh41NTiC0ij1qeqmd2BHErRYcRz4V8x0vFsnOD9pdNP9r3W7duVUOdsGPXqEM+KYVCoqPGXFXDh37ILQ/Oq2Nbz8TRO6QYsJXdMpw9d+aiaxULpQ6jWKrDVySbSMxoFuetilkzq3S6rEMWS4Z5YLzocDShQ04uBvtyis1Y5VacvbyES4T4TrAOu8ECyLg0Jor99K3V+PCbOY09M8fOVyVIS/2k/hIux1SHj9l4/Hj2i63l7hdH+cyZNGZyNGfJttz9YyvDJZoyTHwnWIfGGHNZgau6miYsM1vPcb068VOGie8E69AY4zm2zHkysVOGie8E69AYY8yZePjwIXqHdGH5jebkIL4TrMNu8LdlGZeGMZcXuHDCLRiI7wTrsBssgIxLw5hLyuX6oan4TrAOu6H8n1afcWkYY1pAfCdYh8YYY3qB+E6wDo0xxvQC8Z1gHXaDvy3LuDSMMS0gvhOsw26wADIujUmG0xKdaLBKjvgVo5nIjFFBOdwJ/8S9X49hHcOGbW5ulimPZWa86Y0aiTHJzBVDfCdYh93gH49kXBqTDMfk3N3djf9WQ1oxBljjH645cmbMqSRpYvc8txHhyJxwJ+Lj94rr6+tHzYIUP2uULMn0RjkPMWwKd+Rh+Zqnc3KdvJKI7wTr0BgzihiimoNHz87OQk70FjpwnIShGnqRGotJiLCA1dyzhHJidyaITdWwW4mtczWMhA4jJc4+P3+DB8Rx0AVE3zEfk/8HR7KsQ/iVuyM9UnKSCnYfY4BsnBoxcdI8sLi5MojvBOvQGDMK2G6qphrO5bQ9BJExunSpw1AL7BV+wmvsLi6shjMWUUVZh1yOs3M6C077UB0+Zlgw65BP47E7e4S79ZzA0CpW6fj79+8jPeedII2TAprLjvhOsA67wY9iMi6NSYadv/39fWhpr0YSUDzssUFIpQ4D+CZbqjFBdbQO5exZhxHZqEM6jxas6okjsIBaxxPlLzXhRT50LfNmrgDiO8E67Ab/eCTj0pg0ottUpYel7DAtLi6ic8ZlvMJJnBSe41XCZ6FD+AZOwipekZJdur16avh4sJmlVQ1nMSx1GCk5Hy83hQ7zMeFj5qTUIXfhk1iuchemxDL2ik7h9mTPzGBOh/hOsA67wQLIuDQmB7gHVuiqv36Kif0ugksx/KY5BeI7wTo0xnzYHZyfv4HQoQuNuWjEd4J1aIz58HkjnzHCiNahuaqI7wTrsBvc4mRcGpPDysqKO4jmqiK+E6zDbvC3ZRmXxqSRf0pjzJVBfCdYh91gAWRcGsaYFhDfCdZhN/hhVMalYYxpAfGdYB0aY4zpBeI7wTo0xhjTC8R3gnXYDf62LOPSMMa0gPhOsA67wQLIjC6NhYWFlZpqOKYlB3rm6/jIeGBHRXqwSmOuKuI7wTrsBv94JDO6NGLMzGroKohwbe12jF2ZJ/3hVD67u7s58tq1azLjj0TO1nC6gzyXUEQaY64A4jvBOjSTDnSITiH7haHDeJVJf9jRhOQicmdnh3MUZB1K5IMHD3B8ejd6hznSGHMFEN8J1qGZdBp7h/Eqk/7wz+OQXETGLHdZhzkSy3lOH75KpDHmCiC+E6zDbhj9eLBvjC6No3QY0w5wCnVOP0sdYpccyZTysDQiIU50FuE/HnxxcbGqLZsjjTFXAPGdYB12w+gfj/SNsjSe1EjkCKAujTocya6eEJGN52qMNMZcXsR3gnXYDaUA+kwuDQ8hbYy5IMR3gnVoJoK9vb3Z2VlPMGSMuTjEd4J1aCYCTj87NzfnrqEx5oIQ3wnWYTe4xc/k0lhfX7cRjTEXgfhOsA67wd8dZsrSOOlPaYwx5ljEd4J12A2lAPqMS8MY0wLiO8E6NMYY0wvEd4J1aIwxpheI7wTr0BhjTC8Q3wnWYTcc+20ZRxdbXV1dW7sdkZzniL8x2djY4KAqR81zxMHGRpCH+szMzMxIzFEpz4tjS8MYY86O+E6wDrvhWAFAhDLG5uzsLBc4GufCwgLncCgH1eS/FK5fvw5fhsk4CCeXEQ/dIgEi8w84sby7u8vzYlP824EpGdk4HNoZObY0jDHm7IjvBOuwG479Xx10uLx8Ez086md7ezt7CP6ADhFZjjHNaXIhPOpwc3Mzb2VfE5uqJo9yEqWsYapXUuYO67lwbGkYY8zZEd8J1uGEAh1yAd24jY0NzuoXWxHDeR6gruyqnIbOgxGxb1Ur7f79+0zMaR9EcrEvdYitsCOUnFPmgxhjzOVCfCdYhxMKdMi+2tbWFr9HjE4bv9ujDvf29vjINGB/DvFZhzJdEXVYfrkocx5heXp6OlJ6ziNjzKVGfCdYh91Qflsm47CgE1bVk9D+PEW9KjGNNKYZc5CXPOdReZwxD3JSytIwxphzR3wnWIfdkAWA5TxKJ0R47l/OTTjWoTGmBcR3gnXYDSGApaUluDB+NdpPrENjTAuI7wTrsBsePHjA6f3MTPE3R2OMuQjEd4J12DGrq6vz8zesBGOMuWjEd4J12A3yT7vt7W3+ELSf+H+HxpgWEN8J1mE3+NuyjEvDGNMC4jvBOuwGCyDj0jDGtID4TrAOjTHG9ALxnXCJdbi/v38Rw0kbY4y5kojvhPPX4cbGxp07z29tbemGJmQolkbyWGIcgayqR5GGDjmo2FHEwVdWVjgsmTDO2YNySLOYLKLcdCz+8UjGpWGMaQHxnXD+OlxYWFhdXeVYl8ciEww1kn9yyWE8q1qHy8s3RzSjHFozhuhsHOdlnLMH5S8/Y+jOctOx+NuyjEvDGNMC4jvhQnTIBXbIZmdn5+dvsLMIbWCVQ07DZNAJJ7OFunIyROZBovNejEd6RMK4TC8jXAMkjoPzPwwy7Es+uySYrYluJedwqA5ng/As5aYyPyUWQMalYYxpAfGdcCE6nKqpam9BPPANVcFeFEyDbhkTYCtWsZyTSeMYfa+YWgjpt2uYXvSzs7PDcajj4FWdkzylu5w9J8DR0Ael1ClCJsiZ50GkdxibxtHhiH5tD3FpGGNaQHwnXIgOq/p3Luvr63s1sYna4JRDIqScTL7nCx3igKHDnIB9xIjEwdm3y7aDI0frkAmwL1UaT1kjcc48DyI6jE2SH2OMMZOA+E64KB1Waaq82dnZeKhYDbWBvt3MzMza2m12qnKyUodImR+W7tWT/OH4XOW4l1k/jOHB4blIGeSzSwIcWXJylA5h08ZNZX6MMcZ0jvhOOAcdrqys+GHXSfG3ZRmXhjGmBcR3wul1yA4W4Fdl5kRYABmXhjGmBcR3wml06JmJzo770xmXhjGmBcR3wml0SNA75H8SGv/hbowxxkwU4jvh9Dqs6r8WeK4+Y4wxlwLxnXAmHQbuIJ4UPx7MuDSMMS0gvhPOR4fmpPjHIxmXhjGmBcR3gnXYDRZAxqVhjGkB8Z1gHRpjjOkF4jvBOjTG/Ix79+46OExaiHn9zo74TrAOu8E/Hsm4NCaE/3Dv3xxU33dwmKiAarm4+LOxP8+I+E6wDrvB35ZlXBoTgnXoMIGB1fJcjCi+E6zDbrAAMi6NCcE6PGN4+3//cRnpcMYQ1fLsRhTfCdZhN/jxYMalMSFkHX791d//t7/35de2/oCrb/zZH8amzdf+YGXln//p//pabrPQVJV7HRuQvowcHf7oGy/l1dXVf/ncc/+qTHZs4HH+bv9RuSlf7GDvYZlAwszMDF5/8Ld//slPfrzc2hg++9nfKCMlxKn/ZPOr5dajQuMVjRnKfXNp8zIZximWEQEl/J23/ojLqDAf/PCdg1p7WI4QiaNa/uSnf5Xn6TsF4jvBOjTG/Iysw4WFf4LXv959QDfAOoyfmprKtmB47//96f7f75R7IWz/1esHdTv74yf/52DYjEZjyvQ5sIPFxAxso6Pj9V/Wn49NyEze9/9u/8/coL/5nVe5wLzxpDgyA7OES+YqUzJNbvevX7+OSCRgk31w2Bm4zL/5/nciG7xYpkFzH5eJVSTLCpmbm+MC8hyRKLechqfGwh9u/MeQB3eJPOTdD+qr4xVJMuYnkkXJ5E1537yVm/JlHqS8RXkepMvHKtQV18J7ly8N1QlpGL+8vHjz5j/DwvT0NLfiw1akPEg6PDizEcV3gnVojPkZokM0WF/+8gpbsdAhWi40iy/8u3+dG6ywmuyFBbz+8i//I7SqbEzZf1pa+qeyIwP7eWgWkZ5tJY8Q8QeHdYjMoFcKGWP5V3/1H+MVHVO24GxS0XoeDHt7zADacbbdPM5/+9q/jyMfDDOWT4HMc4GOhBRja/QFeeS42Hj973/8MhOwYLNOqEMe4Ytf/Bexy8EwzzmGC9euXTs4fJl59wi8IimNfATemuie5k3cNwdeLPtqOf+RtyhPXj4zg0icl5f/8Y8/dTCsNrE7qxPuPh8kzMz8Q7z+/v3f4VbRoYSzfLcivhOsw244yx29erg0JoSydxjeCh1GyK1biCHvFV0QpoTS0D6y34BuUE7PgD4KVhmw+rGP/QO0lRCVxGdXMcB26D/hLEwDj+aeEBMcJB0yMusQXR9kLGQQGjto0mH0n6iQg/rIcrHIz0HdtcKVRmZKHTIGyd75iz/JWxni1DwaEuBo+TLz7rEXryIny0c4qB9r3/7dVfTJ5OCxbw4oJbk0hqzDg3SvmRlG8vJZStK5ZHVCDLX9n/7z7zIbDNZhvzjLHb16uDQmhFKHB0MN/PZvf47PxNBR+OGP/uLgcOMY3/SUex0MeyoHQ3+ERZg+P22jR2kv6BMp+TAwx2cd8rywJjbhUPFs8GDY+2FPiM0rMyw6ZJ/moO4gxhXx2R0DvxM9GOYBFgkdhhK4Y77YrEPu+4O//fNcYtQhj8Aj/9qvzSE9QjxUjFNnHebLzLtH4BVJaWTn8TU6xHlTlEaEXEo5/5G3KE9ePjOTdchbjGIpdYiuZJQhPv3EVuuwX/jHIxmXxoQw5i9L0cyhcZdIfMAvUx7U3akyckR4tPNGGTkiPjqaB+kbSoadx3+WN5X75gD1RjcupC4hd8IYkKt4tnlw3C9L81eSEfJ1/bj+RrNMIyFfZv5CbkQyCbnQxgz5Mo8KI+41Otz58uO56CmCdWiMuXDG1OHVC+hK/s33v1PGSyh1KOGoVh69K3aeyjDaoO0H+JUT2YLT/WRXAnyPLmP+sfEZD2sdGmMunN7q0OESBevwqnGWO3r1cGlMCNahw+SHszQX4jvBOuyGs9zRq4dLY0KwDh0mP5yluRDfCdZhN5zljl49XBrGmBYQ3wnWoTHGmF4gvhOsQ2OMMb1AfCdYh93gf9plXBrGmBYQ3wnWYTf427KMS8MY0wLiO8E67AYLIOPSMMa0gPhOsA6NMcb0AvGdYB2eHvRpBoOfdhI2Nzc1N13TVWm88so3NSv9A4X/6NFeWTjthMePP9AMme7AO6K8R/0MeFNI4YjvhCN1GFMsPnnyJCJN5rnnvlLegHbCnTvPa266Blkq89lO0Kz0jw6rIoNmyHRHeXf6HKRwxHfCkTpcWVnhwsbGxv7+fsSboMM2aAK/bOuwNDQr/aPDwmfQDJnuKO9On4MUjvhOGFeH09PTDx48WFu7jZj19fVr165hFa9YnZmZmcBndy3QYRtkHeagWekfHRY+g2bIdEd5d/ocpHDEd8K4Orx+/fqtW7cYMzU1tbq6CjUuLCxgFcuxV6/osA2yDnPQrPSPDgufQTNkuqO8O30OUjjiO+FIHcJ/XMi2YyR0mLuDocm+IW0QiuVaTXlLGsPnP/9bZeRRYXn5Zl6dfB1OT898+tO/gjIpr+WMoWz6NSv9o7Eqovy5+swzn4tNm5tvTE9P11PZ/XwXJGDVxdann/4sYj7zmd9k/SxLuzFohkx35PvC253fiVzFK1dz3ci7oIac/c17797Lg1S7jm0bWdkaqygDqmW5Vw6f+MQnJUYKR3wnHKnD+/fvI0/sCGIVyzMzM0tLS1hGZxF9x+mayjochvn5G7H80kvrc3NzEc869+yza6gfbKTu3n0BJYqm5913v4dV9LPZDDEN9mVNev/9n3zqU7/04otfvVw63N39EUogVr/0pVtcwFXzGrEQ5fPKK9/Ex6y4fGxCcX372w8RGe/VKB9sxfuEyxE0K/2jsSrincvV3OQ1tnE5AQ9FHebSjlswSLcp9tIMme7Id1ZuNxoTWS51WNaQ3Drxvn/ta9/gJjZTfAt/61tvMTJaP/pPToFVbI0fQqOmobrisFHZJAOwI9J/4QtfZGJGMks8Y24rmCwHKRzxnXCkDs2xlB/JASsZP6TACh/96Me4ACXgrkNvg2G/EHeUO8YnNdzgSHPjxq/jlbuj6lwuHSI89dQv4s1AKaKyxgUO6saa14jaj5KhI7k1NsVbAgly+QzGqPE9pCz8tbXbUYa5PXr99TcRz9oVAQlYewfDFid6hyxtuQVxmyJohkx35PvC2x3vxGwaLpc6jBrCXRpbp8GwYiBlvIXjUNFFY6sVtSvLmGePg+djNlbR9977wZtv/iUrp3Rt80UhDULeUQpHfCdYh6en8SM5A/tD+NgStwpbIwFvaugQadB4IaBWRRo2RrH7pdMhA+o33i2lDrmKq0PV5/fQcvn4BIBSQrPO90Yk4DHlLJqV/tFYFUc8EBscbkRygkYdyi3IVZ1BM2S6Q24NA9+J+aZzubFuyC7l2xPhIx/5BbxJ19e/nt/C3BRPg1iF5BRo96JhzPkZFG9tboVE0fuE5HAuVs7IEs8YbQWW33rr3eikMkjhiO+EE+hwb28vnoAhB2v1r0z7TGMbxBAV4un6cSjKDZVGdIh7j034tPVM/WwQMa+++proELujqFERL5cO8S7a3HxjMPyciCvFh7t7915m/cY1oma/8853WftZj+Xy+Vdibsrlg9f8pIVBs9I/Gqsi7sLKygoLkJ+aUeZLS0uIx3I8rGaCWBYdsrTlFliHk0y+L7zdg+E7Efd9cXFxUDcsMMfgcN3IuyCGuzS2ToPhA1Iu830a3bJo/fiBLNeux48/QGuGGsWmAOfCXtFcsLLlKor0TInOYugwssQz5rbi2WfX4lwMUjjiO+EEOpS3HHKMAtVEfaKxDWKICgHhTdUPK3IC3tS3334P8bijvOVYLnuH3B2Rl06H/OacTzx4FYs1LAe8kRBDq6Fy420jl8/vqllQuXywWv5CR7PSP46qitEDmKrB7cBncy6j+kX6ETpkacstsA4nmXxfeLvjnTiolYPVMFmuG3mXiGlsnQb1e3xq+DbkWzieRozQ4aCuk2wcBnW3iudirWNlkyp698OfWUyjhocOI0s8fm4r4roiSOGI74Rxddg45ghKRNP1icbHg+2ECdfh6FA2pmcMmpX+MX7hX1DQDJnuKO9OGfDxmr3GCw3wVnQ62wn8aU8OUjjiO2FcHeLCynPz9Jq0N3TYBl1qHZ570Kz0jw4Ln0EzZLqjvDt9DlI44jthXB2Wp2HA+1CT9oYO2yDrMAfNSv/osPAZNEOmO8q70+cghSO+E8bV4VE9a/cOOwnWYQ6alf7RYeEzaIZMd5R3p89BCkd8J4yrQ393WMKfFXQSJnCQWE/w1CH8tV5ZOO2Echod0yGe4ClCWTPFd8K4OqwKI8KF29vbmsgYY4yZSMR3wgl0WH34yHT3Xs39+/d1mzHGGDPBiO+Ek+nQGGOMuaSI7wTr0BhjTC8Q3wnWoTHGmF4gvhOsQ2OMMb1AfCdYh8YYY3qB+E6wDo0xxvQC8Z1gHRpjjOkF4jvBOjTGGNMLxHeCdWiMMaYXiO8E69AYY0wvEN8J/x+WU5rTX2BNoAAAAABJRU5ErkJggg==>

[image3]: <data:image/png;base64,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>

[image4]: <data:image/png;base64,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>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,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>