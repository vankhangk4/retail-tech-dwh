# Product

## Register

product

## Users

Người dùng chính là admin toàn hệ thống của nền tảng Data Warehouse multi-tenant cho chuỗi bán lẻ thiết bị công nghệ. Họ dùng giao diện này để kiểm tra sức khỏe hệ thống, theo dõi hiệu quả từng tenant, xác nhận ETL đang vận hành đúng, và dẫn dắt phần trình bày khi demo trên laptop hoặc màn hình chiếu.

Người dùng phụ là giảng viên và hội đồng, những người đánh giá mức độ hoàn thiện, tính tin cậy, và khả năng điều hành của hệ thống qua những gì giao diện thể hiện trong vài phút đầu tiên.

## Product Purpose

Frontend này là lớp điều hành và thuyết minh cho toàn bộ hệ thống DWH multi-tenant: xác thực người dùng, cung cấp điểm nhìn tổng quan, cho phép truy cập các dashboard BI, theo dõi tenant, và quản lý những tác vụ quản trị liên quan đến dữ liệu và ETL.

Thành công của sản phẩm là: trong vài giây đầu, người dùng có thể hiểu hệ thống hiện có ổn định không, tenant nào đáng chú ý, dữ liệu có đang tươi và đáng tin cậy không, và nên đi tiếp vào dashboard hoặc tác vụ nào để giải thích hệ thống một cách mạch lạc.

## Brand Personality

Người điều hành, cao cấp, tin cậy, sắc bén, trực quan.

Giọng điệu của giao diện phải dứt khoát, bình tĩnh, có thẩm quyền, tránh khoa trương. Nó phải tạo cảm giác đây là một bàn điều khiển vận hành thật, không phải một mẫu admin dựng sẵn hay một bài trình diễn nặng hiệu ứng.

## Anti-references

- Superset mặc định hoặc bất kỳ bề mặt nào trông như lớp nhúng nguyên bản không qua thiết kế lại.
- Dashboard SaaS xanh dương kiểu template với sidebar quen tay, lưới KPI giống nhau, và các thẻ thông tin lặp lại vô hồn.
- Giao diện đồ án sinh viên quá nhiều gradient, hiệu ứng phô, hoặc trang trí không phục vụ việc đọc và ra quyết định.

## Design Principles

- Ưu tiên tín hiệu điều hành trước số lượng thông tin: trạng thái hệ thống, độ tươi dữ liệu, và tenant cần chú ý phải hiện ra trước khi người dùng đi sâu vào dashboard.
- Mỗi màn hình phải hỗ trợ kể chuyện khi demo: nhìn tổng quan, phát hiện điểm đáng nói, rồi drill-down vào bằng chứng.
- Tạo sự tin cậy bằng cấu trúc rõ, timestamp, trạng thái, nhãn chính xác, và phân cấp thông tin chặt chẽ thay vì trang trí.
- Một ngôn ngữ thiết kế thống nhất phải bao phủ toàn bộ frontend: đăng nhập, đăng ký, shell dashboard, quản lý tenant, ETL, và các trạng thái lỗi/rỗng/tải.
- Mọi lựa chọn thị giác phải phục vụ khả năng đọc nhanh trên laptop và màn hình chiếu: tương phản chắc, nhịp khoảng trắng tốt, và phân biệt trạng thái không chỉ dựa vào màu.

## Accessibility & Inclusion

Chuẩn cơ sở là WCAG AA, với tương phản đủ mạnh để trình chiếu trong phòng học hoặc phòng họp. Giao diện cần có focus state rõ ràng, hỗ trợ reduced motion, và tránh dùng màu là tín hiệu duy nhất cho trạng thái hệ thống.

Thiết kế ưu tiên desktop và laptop vì đây là bối cảnh trình bày chính, nhưng vẫn cần responsive hợp lý để không vỡ bố cục trên màn hình hẹp.
