# Product

## Register

product

## Users

Superadmin và admin là nhóm vận hành hệ thống. Khi mở sản phẩm, họ cần thấy ngay nơi upload file nguồn, chạy ETL, kiểm tra sức khỏe hệ thống, độ tươi dữ liệu và phạm vi tenant đang tác động.

Viewer là nhóm xem dữ liệu hằng ngày. Họ cần vào đúng tenant, mở đúng dashboard và thấy chart nhanh, rõ, đáng tin mà không bị nhiễu bởi các thao tác vận hành.

## Product Purpose

Sản phẩm này là một operations console cho hệ thống Data Warehouse multi-tenant của chuỗi bán lẻ thiết bị công nghệ. Nó gom xác thực, vận hành ETL, quản trị tenant và truy cập dashboard phân tích vào cùng một bề mặt để hệ thống có thể được vận hành, giải thích và tin cậy từ một điểm vào.

Thành công của sản phẩm là hai việc xảy ra nhanh và rõ: người vận hành có thể nạp dữ liệu và chạy ETL với sự tự tin, còn người xem có thể đi thẳng tới chart đúng phạm vi dữ liệu mà không phải nghi ngờ tenant, quyền hay độ mới của dữ liệu.

## Brand Personality

Hiện đại, cá tính, hệ thống.

Giọng điệu của giao diện phải cho cảm giác kiểm soát, rõ ràng và có năng lực kỹ thuật. Sản phẩm không được phô trương như landing page, nhưng cũng không được vô danh hoặc vô hồn như một admin template mặc định.

## Anti-references

- Dashboard SaaS xanh dương kiểu template, nơi toàn bộ bảng màu và cảm giác thị giác đều đi theo một phản xạ quen thuộc, an toàn và nhạt.
- Hero metrics theo công thức số lớn, nhãn nhỏ, card giống nhau lặp đi lặp lại.
- Auth split-screen mặc định chỉ để trang trí, không truyền tải được tín hiệu hệ thống hay giá trị vận hành thực.
- Giao diện mà mọi trạng thái đều bị nén thành cùng một kiểu pill, hoặc chỉ dùng màu để truyền tải cảnh báo, lỗi, thành công.
- Bề mặt enterprise chung chung, nhiều card nhưng không có nhịp điều hướng rõ, không bộc lộ ưu tiên vận hành và không giúp người dùng biết nên làm gì tiếp theo.

## Design Principles

- Ưu tiên vận hành trước. Admin phải thấy ngay upload, ETL, health và bước tiếp theo mà không cần đi tìm.
- Hiện phạm vi trước khi hiện insight. Tenant, vai trò, độ tươi dữ liệu và trạng thái hệ thống phải rõ ràng trước khi người dùng tin vào chart hoặc thao tác.
- Viewer phải vào chart nhanh. Luồng cho người xem cần giảm nhiễu vận hành và đưa họ tới bề mặt phân tích sớm nhất có thể.
- Trạng thái phải đọc được, không chỉ nhìn màu. Lỗi, cảnh báo, tiến trình và quyền hạn phải có tín hiệu rõ ràng bằng cấu trúc, nhãn và hình thái.
- Hệ thống phải có cá tính nhưng không lạ lẫm. Giao diện nên quen thuộc với người dùng tool, nhưng không được rơi về cảm giác template có sẵn.

## Accessibility & Inclusion

WCAG AA là ngưỡng mặc định cho toàn bộ sản phẩm.

Ưu tiên keyboard-first navigation, focus-visible rõ ràng, HTML semantic và nhãn thân thiện với screen reader.

Tôn trọng reduced motion cho mọi chuyển động không thiết yếu.

Không dùng màu là tín hiệu duy nhất cho trạng thái, mức độ nghiêm trọng hay kết quả thao tác.

Chart, bảng và control phải vẫn hiểu được với người dùng có khác biệt về nhận biết màu sắc.
