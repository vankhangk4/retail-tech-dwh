const APP_DATASET = document.body.dataset;
const APP_CONTEXT = {
    userRole: APP_DATASET.userRole || '',
    userTenant: APP_DATASET.userTenant || '',
    userId: APP_DATASET.userId || '',
    defaultPage: APP_DATASET.defaultPage || 'overview',
    defaultAnalysis: APP_DATASET.defaultAnalysis || 'revenue',
    supersetUrl: APP_DATASET.supersetUrl || '',
    accessToken: APP_DATASET.accessToken || '',
};

const COPY = {
    vi: {
        page: {
            browserTitle: 'DWH Operations Console',
            skipLink: 'Bỏ qua thanh điều hướng, tới nội dung chính',
            closeNavigation: 'Đóng thanh điều hướng',
            toggleNavigation: 'Thu gọn hoặc mở thanh điều hướng',
            languageLabel: 'Ngôn ngữ',
            languageSelectAria: 'Chọn ngôn ngữ giao diện',
            scopeChip: 'Phạm vi',
            roleChip: 'Quyền',
            timestampChip: 'Thời điểm',
            timestampLoading: 'Đang cập nhật...',
        },
        pages: {
            overview: {
                eyebrow: 'Điều hành',
                title: 'Tổng quan điều hành',
                subtitle: 'Đọc tín hiệu hệ thống trước, sau đó đi sâu vào phân tích hoặc quản trị.',
            },
            analysis: {
                eyebrow: 'Phân tích',
                title: 'Phòng phân tích',
                subtitle: 'Chọn đúng góc nhìn phân tích, rồi mở báo cáo tương ứng trong cùng một giao diện.',
            },
            etl: {
                eyebrow: 'Vận hành',
                title: 'Vận hành ETL',
                subtitle: 'Tải file, kích hoạt pipeline và kiểm tra lịch sử upload trong cùng một luồng.',
            },
            manage: {
                eyebrow: 'Quản trị',
                title: 'Quản lý tenant',
                subtitle: 'Tạo user mới và kiểm soát người dùng trong tenant hiện tại.',
            },
            admin: {
                eyebrow: 'Quản trị',
                title: 'Quản trị hệ thống',
                subtitle: 'Quản lý tenant, user và log ETL trong cùng một giao diện điều hành.',
            },
        },
        overview: {
            mission: {
                eyebrow: 'Nhịp điều hành',
                title: 'Hệ thống Phân tích Dữ liệu Bán lẻ.',
                description: 'Nền tảng hỗ trợ theo dõi hiệu năng hệ thống, giám sát luồng dữ liệu và phân tích chỉ số kinh doanh đa chi nhánh.',
            },
            actions: {
                openAnalysis: 'Mở phân tích',
                openEtl: 'Giám sát ETL',
                openAdmin: 'Quản trị hệ thống',
                openManage: 'Quản trị hệ thống',
            },
            health: {
                eyebrow: 'Tuyến vận hành',
                loadingLabel: 'Đang kiểm tra Auth Gateway',
                loadingCopy: 'Hệ thống đang nạp tín hiệu vận hành ban đầu.',
            },
            session: {
                eyebrow: 'Phiên hiện tại',
                scopeLabel: 'Phạm vi dữ liệu',
                userLabel: 'Tài khoản đang dùng',
                lastSyncLabel: 'Lần cập nhật giao diện',
                lastSyncWaiting: 'Đang chờ log ETL',
            },
            kpi: {
                revenueLabel: 'Tổng doanh thu',
                revenueLoading: 'Đang nạp chỉ số doanh thu.',
                profitLabel: 'Lợi nhuận gộp',
                profitLoading: 'Đang nạp biên lợi nhuận.',
                ordersLabel: 'Đơn hàng',
                ordersLoading: 'Đang nạp tín hiệu vận hành đơn hàng.',
                customersLabel: 'Khách hàng',
                customersLoading: 'Đang nạp độ phủ khách hàng.',
            },
            attention: {
                title: 'Cần xử lý ngay',
                description: 'Chỉ giữ lại các tín hiệu có thể làm yếu buổi demo hoặc ảnh hưởng tính tin cậy của dashboard.',
            },
            roadmap: {
                title: 'Lộ trình phiên này',
                description: 'Đọc nhanh dữ liệu có đủ tin cậy không, rồi chọn đúng giao diện phân tích hoặc quản trị.',
            },
            freshness: {
                loadingLabel: 'Đang tính toán độ tươi dữ liệu',
                loadingCaption: 'Khi log ETL xuất hiện, hệ thống sẽ nhắc thời điểm đồng bộ gần nhất ở đây.',
            },
            nextAction: {
                eyebrow: 'Bước tiếp theo',
                loading: 'Đang xây dựng gợi ý cho bước demo tiếp theo.',
            },
            focus: {
                analysis: {
                    title: 'Đi vào phân tích',
                    description: 'Một điểm vào cho toàn bộ báo cáo nghiệp vụ.',
                    meta: '5 góc nhìn',
                },
                etl: {
                    title: 'Kiểm tra ETL',
                    description: 'Dùng khi cần thống kê dữ liệu vừa được nạp và log đang sạch.',
                    meta: 'Pipeline',
                },
                admin: {
                    title: 'Mở quản trị hệ thống',
                    description: 'Kiểm tra tenant, user và log ETL từ cùng một giao diện điều hành.',
                    meta: 'Governance',
                },
                manage: {
                    title: 'Mở quản trị tenant',
                    description: 'Đi thẳng vào user trong cửa hàng hiện tại khi cần giải thích phân quyền.',
                    meta: 'Tenant',
                },
            },
            foundation: {
                title: 'Tình trạng nền',
                description: 'Gom tenant, user và lỗi ETL về một hàng để biết hệ thống đang ở trạng thái nào trước khi đi sâu hơn.',
                tenantLabel: 'Tenant',
                tenantLoading: 'Đang nạp danh sách tenant.',
                userLabel: 'User',
                userLoading: 'Đang nạp danh sách user.',
                issueLabel: 'Lỗi ETL',
                issueLoading: 'Đang kiểm tra log ETL lỗi.',
            },
        },
        analysis: {
            picker: {
                title: 'Góc nhìn phân tích',
                description: 'Chỉ chọn một trục phân tích tại một thời điểm để tránh mở quá nhiều dashboard song song.',
            },
            options: {
                revenue: {
                    label: 'Doanh thu',
                    summary: 'Toàn cảnh doanh thu, cùng kỳ và chênh lệch giữa các tenant.',
                },
                products: {
                    label: 'Sản phẩm',
                    summary: 'Sản phẩm bán chạy, biên lợi nhuận và danh mục chủ lực.',
                },
                inventory: {
                    label: 'Tồn kho',
                    summary: 'Thiếu hàng, lệch tồn và rủi ro ảnh hưởng doanh thu.',
                },
                customers: {
                    label: 'Khách hàng',
                    summary: 'Phân khúc, hành vi mua và chân dung khách hàng trong DWH.',
                },
                employees: {
                    label: 'Nhân viên',
                    summary: 'Hiệu suất bán hàng và mức đóng góp theo đội ngũ.',
                },
            },
            dashboard: {
                revenue: {
                    title: 'Phòng phân tích doanh thu',
                    description: 'Dùng khi cần thống kê toàn cảnh doanh thu, theo thời gian, theo tenant hoặc theo danh mục.',
                },
                products: {
                    title: 'Phòng phân tích sản phẩm',
                    description: 'Mở khi cần giải thích tăng trưởng đến từ mặt hàng nào, lợi nhuận nằm ở đâu và đâu là danh mục chủ lực.',
                },
                inventory: {
                    title: 'Phòng phân tích tồn kho',
                    description: 'Dùng khi hội đồng hỏi về rủi ro vận hành, mức tồn tối thiểu và dòng chảy hàng hóa.',
                },
                customers: {
                    title: 'Phòng phân tích khách hàng',
                    description: 'Phù hợp khi cần trình bày cách warehouse hỗ trợ đọc chân dung khách hàng, cụm RFM và giá trị vòng đời.',
                },
                employees: {
                    title: 'Phòng phân tích nhân viên',
                    description: 'Dùng cho doanh số, hiệu suất và mức đóng góp của nhân sự bán hàng.',
                },
            },
            stage: {
                eyebrow: 'Trục phân tích',
                embedPill: 'Nhúng từ Superset',
                openModal: 'Mở dạng tập trung',
                contextLoading: 'Trục đang xem: Doanh thu',
                frameLoading: 'Đang chuẩn bị dựng dashboard nhúng.',
                iframeTitle: 'Dashboard phân tích',
            },
            scope: {
                label: 'Phạm vi báo cáo',
                loading: 'Đang tải danh sách chi nhánh...',
            },
        },
        etl: {
            hero: {
                eyebrow: 'Nạp vào staging',
                title: 'Kéo file nguồn vào đúng tenant rồi kích hoạt pipeline.',
                description: 'Màn hình ETL ưu tiên thao tác vận hành trước. Chọn phạm vi, nạp file, rồi xác minh staging đang chứa đúng dữ liệu cho lần chạy kế tiếp.',
            },
            scope: {
                label: 'Tenant đang vận hành',
                loading: 'Đang tải tenant...',
            },
            upload: {
                eyebrow: 'Upload source',
                title: 'Kéo thả file nguồn hoặc chọn thủ công.',
                description: 'Chấp nhận `.xlsx`, `.xls` và `.csv`. Sau khi nạp, lịch sử file gần đây sẽ được cập nhật ngay ở phía dưới để bạn xác minh lại staging.',
                chooseFiles: 'Chọn file nguồn',
                runNow: 'Chạy ETL ngay',
            },
            guide: {
                title: 'Hướng dẫn file nguồn',
                description: 'Giữ nhịp đặt tên ổn định để ETL phân loại nhanh và để lúc demo bạn giải thích nguồn dữ liệu không bị khựng.',
                revenueLabel: 'Doanh thu',
                revenueExample: 'Ví dụ: `BaoCaoDoanhThu_HN_20260101.xlsx`',
                inventoryLabel: 'Tồn kho',
                inventoryExample: 'Ví dụ: `QuanLyKho_HCM_20260101.xlsx`',
                catalogLabel: 'Danh mục',
                catalogExample: 'Dùng `DanhMucSanPham.csv`, `DanhMucKhachHang.csv`, `DanhMucNhaCungCap.csv`.',
                inboundLabel: 'Nhập hàng',
                inboundExample: 'Dùng `PhieuNhapHang.csv` cho luồng nhập kho và nhà cung cấp.',
            },
            library: {
                title: 'File đã nạp gần đây',
                description: 'Dùng để xác minh nhanh staging đang chứa đúng nguồn dữ liệu cho tenant đang vận hành.',
                loading: 'Đang tải lịch sử upload.',
            },
        },
        manage: {
            create: {
                title: 'Tạo user trong tenant',
                description: 'Dùng cho manager hoặc viewer mới trong tenant {tenant}.',
            },
            form: {
                usernameLabel: 'Tên đăng nhập',
                usernamePlaceholder: 'ví dụ: manager_cn1',
                passwordLabel: 'Mật khẩu',
                passwordPlaceholder: 'Ít nhất 6 ký tự',
                submit: 'Tạo user tenant',
            },
            users: {
                titleWithTenant: 'User trong tenant {tenant}',
                description: 'Danh sách này giúp kiểm soát trạng thái truy cập trong phạm vi cửa hàng hiện tại.',
                roleHeader: 'Vai trò',
                statusHeader: 'Trạng thái',
                createdAtHeader: 'Ngày tạo',
                actionsHeader: 'Thao tác',
                loading: 'Đang tải danh sách user...',
            },
        },
        admin: {
            createTenant: {
                title: 'Tạo tenant mới',
                description: 'Thiết lập tenant, đường dẫn dữ liệu và thời hạn hiệu lực cho hệ thống multi-tenant.',
                idLabel: 'Mã tenant',
                idPlaceholder: 'ví dụ: STORE_DN',
                nameLabel: 'Tên tenant',
                namePlaceholder: 'ví dụ: Cửa hàng Đà Nẵng',
                pathLabel: 'Đường dẫn dữ liệu',
                expiresAtLabel: 'Ngày hết hạn',
                submit: 'Tạo tenant',
            },
            createUser: {
                title: 'Tạo user hệ thống',
                description: 'Gắn user với tenant cụ thể hoặc để trống khi cần cấp quyền rộng hơn trong hệ thống.',
                usernameLabel: 'Tên đăng nhập',
                usernamePlaceholder: 'ví dụ: manager_dn',
                passwordLabel: 'Mật khẩu',
                passwordPlaceholder: 'Nhập mật khẩu',
                tenantLabel: 'Tenant',
                roleLabel: 'Vai trò',
                roleViewer: 'Viewer',
                roleAdmin: 'Admin',
                submit: 'Tạo user',
            },
            tenants: {
                title: 'Danh sách tenant',
                description: 'Kiểm tra hiệu lực, trạng thái và đường dẫn dữ liệu của từng tenant.',
                searchLabel: 'Tìm tenant',
                searchPlaceholder: 'Tìm theo mã, tên hoặc đường dẫn',
                idHeader: 'Mã',
                nameHeader: 'Tên',
                pathHeader: 'Đường dẫn',
                statusHeader: 'Trạng thái',
                expiresAtHeader: 'Hiệu lực',
                actionsHeader: 'Thao tác',
                loading: 'Đang tải tenant...',
            },
            users: {
                title: 'Danh sách user',
                description: 'Kiểm soát quyền và phạm vi truy cập của toàn bộ user trong hệ thống.',
                searchLabel: 'Tìm user',
                searchPlaceholder: 'Tìm theo username, tenant hoặc vai trò',
                tenantHeader: 'Tenant',
                roleHeader: 'Vai trò',
                statusHeader: 'Trạng thái',
                actionsHeader: 'Thao tác',
                loading: 'Đang tải user...',
            },
            etl: {
                title: 'Giám sát ETL gần đây',
                description: 'Dùng để giải thích độ tươi dữ liệu, tình trạng pipeline và khả năng truy vết của hệ thống.',
                loading: 'Đang tải log ETL...',
            },
        },
        modals: {
            editTenant: {
                eyebrow: 'Chỉnh tenant',
                title: 'Chỉnh tenant',
                closeAria: 'Đóng modal chỉnh tenant',
                nameLabel: 'Tên tenant',
                pathLabel: 'Đường dẫn dữ liệu',
                expiresAtLabel: 'Ngày hết hạn',
                statusLabel: 'Trạng thái',
                submit: 'Lưu thay đổi tenant',
            },
            editUser: {
                eyebrow: 'Chỉnh user',
                title: 'Chỉnh user',
                closeAria: 'Đóng modal chỉnh user',
                passwordLabel: 'Mật khẩu mới',
                passwordPlaceholder: 'Để trống nếu không đổi',
                tenantLabel: 'Tenant',
                roleLabel: 'Vai trò',
                roleViewer: 'Viewer',
                roleAdmin: 'Admin',
                statusLabel: 'Trạng thái',
                submit: 'Lưu thay đổi user',
            },
            viewUser: {
                eyebrow: 'Thông tin user',
                title: 'Thông tin user',
                closeAria: 'Đóng modal thông tin user',
                loading: 'Đang tải thông tin user...',
                usernameLabel: 'Tên đăng nhập',
                displayNameLabel: 'Tên hiển thị',
                emailLabel: 'Email',
                phoneLabel: 'Số điện thoại',
                tenantLabel: 'Tenant',
                roleLabel: 'Vai trò',
                statusLabel: 'Trạng thái',
                createdAtLabel: 'Ngày tạo',
            },
            focus: {
                eyebrow: 'Chế độ tập trung',
                title: 'Bảng phân tích tập trung',
                closeAria: 'Đóng modal bảng phân tích',
                iframeTitle: 'Bảng phân tích Superset',
            },
            confirm: {
                eyebrow: 'Xác nhận',
                title: 'Xác nhận thao tác',
                closeAria: 'Đóng hộp thoại xác nhận',
                detail: 'Thao tác này không thể hoàn tác.',
            },
        },
        runtime: {
            analysis: {
                context: 'Trục đang xem: {label}',
                scope: 'Phạm vi báo cáo: {scope}',
                tokenLoading: 'Đang xin dashboard token và dựng phiên nhúng.',
                frameReady: 'Đang hiển thị dashboard nhúng qua Superset.',
                frameError: 'Không thể dựng dashboard nhúng ở thời điểm này.',
                frameFallback: 'Không thể tải bảng phân tích nhúng. Vui lòng đăng nhập lại hoặc kiểm tra dịch vụ Superset.',
            },
            health: {
                stable: 'API ổn định',
                check: 'API cần kiểm tra',
                stableLabel: 'Tuyến xác thực đang phản hồi ổn định',
                stableCopy: 'Có thể tiếp tục đọc tín hiệu vận hành, mở dashboard phân tích hoặc kiểm tra ETL.',
                failedLabel: 'Auth Gateway đang mất phản hồi hoặc trả về trạng thái lỗi',
                failedCopy: 'Ưu tiên kiểm tra dịch vụ nền trước khi trình bày dashboard phân tích cho hội đồng.',
            },
            kpi: {
                revenueMeta: 'Dùng để mở câu chuyện doanh thu theo tenant và danh mục.',
                profitMeta: 'Biên lợi nhuận gộp: {value}%',
                ordersMetaWithAlerts: '{count} cảnh báo tồn kho đang mở.',
                ordersMetaEmpty: 'Chưa ghi nhận cảnh báo tồn kho khẩn.',
                customersMeta: 'Theo dõi phạm vi khách hàng đang hiện diện trong hệ thống.',
            },
            freshness: {
                noLogLabel: 'Chưa có log ETL gần đây',
                noLogCaption: 'Cần chạy ETL hoặc xác nhận kênh log trước khi trình bày độ tươi dữ liệu.',
                noLogTimestamp: 'Chưa có mốc đồng bộ',
                freshLabel: 'Dữ liệu đang ở vùng tươi',
                remindLabel: 'Dữ liệu cần được nhắc lại khi demo',
                staleLabel: 'Dữ liệu đã lâu chưa được làm tươi',
                latestRunAt: 'Lần ETL gần nhất chạy lúc {time}.',
                latestRunWas: 'Lần ETL gần nhất là {time}.',
            },
            attention: {
                expiredTitle: '{tenant} đã hết hạn',
                expiredDetail: 'Tenant cần được gia hạn hoặc giải thích rõ trạng thái trước khi cấp dashboard.',
                inactiveTitle: '{tenant} đang tắt',
                inactiveDetail: 'Tenant hiện không active. Cần xác minh đây là chủ ý quản trị hay sự cố.',
                failingLogTitle: 'ETL lỗi tại {tenant}',
                failingLogDetail: '{source} trả về trạng thái {status} lúc {time}.',
                cleanTitle: 'Chưa có tenant cần can thiệp ngay',
                cleanDetail: 'Có thể dùng overview làm điểm mở đầu rồi chuyển thẳng sang phòng phân tích phù hợp.',
            },
            governance: {
                tenantLoaded: '{count} tenant đang active trong hệ thống.',
                tenantLoading: 'Sẽ hiển thị khi danh sách tenant được nạp.',
                userLoaded: 'Bao gồm admin hệ thống và các user theo tenant.',
                userLoading: 'Chưa nạp danh sách user quản trị.',
                issueLoaded: 'Có log ETL lỗi cần được giải thích hoặc xử lý.',
                issueLoading: 'Chưa ghi nhận log ETL lỗi trong dữ liệu đang có.',
            },
            nextAction: {
                default: 'Mở Phòng phân tích và bắt đầu từ trục doanh thu.',
                checkAuth: 'Kiểm tra Auth Gateway trước, sau đó mới trình bày phần dashboard.',
                checkEtl: 'Đi tới Vận hành ETL hoặc Giám sát ETL để giải thích lỗi pipeline mới nhất.',
                checkTenant: 'Mở Quản trị hệ thống để xử lý tenant đã hết hạn rồi mới đi tiếp.',
                checkFreshness: 'Nhắc rõ thời điểm ETL gần nhất trước khi đi sâu vào các chỉ số phân tích.',
            },
            tables: {
                emptyTenants: 'Chưa có tenant nào trong hệ thống.',
                emptyTenantsFiltered: 'Không có tenant phù hợp với bộ lọc hiện tại.',
                emptyUsers: 'Chưa có user nào trong hệ thống.',
                emptyUsersFiltered: 'Không có user phù hợp với bộ lọc hiện tại.',
                emptyTenantUsers: 'Tenant này chưa có user nào.',
                emptyLogs: 'Chưa có log ETL.',
                emptyLogsDetail: 'Khi pipeline chạy, các bản ghi gần nhất sẽ xuất hiện ở đây.',
                timeHeader: 'Thời gian',
                tenantHeader: 'Tenant',
                sourceHeader: 'Nguồn',
                statusHeader: 'Trạng thái',
                rowsHeader: 'Số dòng',
                usernameHeader: 'Username',
                pathHeader: 'Đường dẫn',
                roleHeader: 'Vai trò',
                actionsHeader: 'Thao tác',
                expiresAtHeader: 'Hiệu lực',
                createdAtHeader: 'Ngày tạo',
                fileNameHeader: 'Tên file',
                fileTypeHeader: 'Loại',
                fileSizeHeader: 'Kích thước',
                uploadedAtHeader: 'Thời điểm',
                tenantIdLabel: 'Mã tenant',
                tenantNameLabel: 'Tên tenant',
                pathLabel: 'Đường dẫn',
                statusLabel: 'Trạng thái',
                expiresAtLabel: 'Hiệu lực',
                actionsLabel: 'Thao tác',
                usernameLabel: 'Username',
                tenantLabel: 'Tenant',
                roleLabel: 'Vai trò',
                timeLabel: 'Thời gian',
                sourceLabel: 'Nguồn',
                rowsLabel: 'Số dòng',
                createdAtLabel: 'Ngày tạo',
                fileNameLabel: 'Tên file',
                fileTypeLabel: 'Loại',
                fileSizeLabel: 'Kích thước',
                uploadedAtLabel: 'Thời điểm',
                editTenant: 'Chỉnh tenant',
                viewUser: 'Xem thông tin',
                editUser: 'Chỉnh user',
                deleteFile: 'Xóa file',
                unknownType: 'Chưa rõ',
            },
            upload: {
                previewUpload: 'Nạp file vào staging',
                previewRunEtl: 'Chạy ETL ngay',
                selectFile: 'Chọn ít nhất một file trước khi nạp vào staging.',
                runningTitle: 'Đang nạp {count} file lên staging',
                runningDetail: 'Hệ thống đang gửi file tới API upload và kiểm tra phản hồi.',
                successTitle: 'Đã nạp {successful}/{total} file vào staging',
                successLine: '{marker} {filename}{type}{error}',
                failedTitle: 'Không thể nạp file vào staging',
            },
            etlRun: {
                selectTenant: 'Chọn tenant trước khi kích hoạt ETL.',
                runningTitle: 'Đang kích hoạt ETL cho {tenant}',
                runningDetail: 'Pipeline sẽ nạp dữ liệu vào warehouse và tạo log tương ứng.',
                successTitle: 'ETL đã được kích hoạt cho {tenant}',
                successDetail: 'Theo dõi log ETL để kiểm tra tiến trình nạp dữ liệu.',
                failedTitle: 'ETL không thể khởi chạy',
            },
            files: {
                noTenantTitle: 'Chưa có tenant đang được chọn.',
                noTenantDetail: 'Chọn tenant trước khi xem lịch sử upload.',
                emptyTitle: 'Chưa có file nào được nạp gần đây.',
                emptyDetail: 'Sau khi upload, lịch sử file sẽ hiển thị ở đây.',
                loadErrorTitle: 'Lỗi tải file.',
                deleteTitle: 'Xóa file khỏi staging',
                deleteDetail: 'File "{filename}" sẽ bị xóa khỏi tenant {tenant}. Thao tác này không thể hoàn tác.',
                deleteConfirm: 'Xóa file',
                deleteSuccess: 'Đã xóa file {filename} khỏi staging.',
            },
            forms: {
                invalidTenantId: 'Vui lòng nhập mã tenant hợp lệ.',
                creatingTenant: 'Đang tạo tenant...',
                tenantCreated: 'Đã tạo tenant {tenant}.',
                saveTenantError: 'Không thể tạo tenant',
                viewerNeedsTenant: 'Viewer cần gắn với một tenant cụ thể.',
                creatingUser: 'Đang tạo user...',
                userCreated: 'Đã tạo user {username}.',
                saveUserError: 'Không thể tạo user',
                loadUsersError: 'Không tải được danh sách user',
                creatingTenantUser: 'Đang tạo user tenant...',
                savingChanges: 'Đang lưu thay đổi...',
                tenantSaved: 'Đã lưu thay đổi tenant.',
                userSaved: 'Đã lưu thay đổi user.',
                saveTenantUpdateError: 'Không thể lưu tenant',
                saveUserUpdateError: 'Không thể lưu user',
                loadUserDetailError: 'Không tải được thông tin user',
                editTenantTitle: 'Chỉnh tenant {tenant}',
                editUserTitle: 'Chỉnh user {username}',
            },
            scope: {
                currentTenant: 'Tenant hiện tại: {tenant}',
            },
        },
    },
    en: {
        page: {
            browserTitle: 'DWH Operations Console',
            skipLink: 'Skip navigation and go to the main content',
            closeNavigation: 'Close the navigation panel',
            toggleNavigation: 'Collapse or open the navigation panel',
            languageLabel: 'Language',
            languageSelectAria: 'Choose interface language',
            scopeChip: 'Scope',
            roleChip: 'Role',
            timestampChip: 'Timestamp',
            timestampLoading: 'Updating...',
        },
        pages: {
            overview: {
                eyebrow: 'Executive',
                title: 'Executive Overview',
                subtitle: 'Review system signals first, then move into analytics or administration.',
            },
            analysis: {
                eyebrow: 'Analytics',
                title: 'Analytics Room',
                subtitle: 'Choose the right analytical angle, then open the corresponding report in the same workspace.',
            },
            etl: {
                eyebrow: 'Operations',
                title: 'ETL Operations',
                subtitle: 'Upload files, trigger the pipeline, and review upload history in one workflow.',
            },
            manage: {
                eyebrow: 'Administration',
                title: 'Branch Management',
                subtitle: 'Create new users and control access within the current branch.',
            },
            admin: {
                eyebrow: 'Administration',
                title: 'System Administration',
                subtitle: 'Manage branches, users, and ETL logs in one operational workspace.',
            },
        },
        overview: {
            mission: {
                eyebrow: 'Operational rhythm',
                title: 'Retail Data Analytics Platform.',
                description: 'The platform supports system performance monitoring, data pipeline supervision, and multi-branch business analytics.',
            },
            actions: {
                openAnalysis: 'Open analytics',
                openEtl: 'Monitor ETL',
                openAdmin: 'System administration',
                openManage: 'Branch administration',
            },
            health: {
                eyebrow: 'Operational lane',
                loadingLabel: 'Checking Auth Gateway',
                loadingCopy: 'The platform is loading the initial operational signals.',
            },
            session: {
                eyebrow: 'Current session',
                scopeLabel: 'Data scope',
                userLabel: 'Active account',
                lastSyncLabel: 'Interface refresh point',
                lastSyncWaiting: 'Waiting for ETL logs',
            },
            kpi: {
                revenueLabel: 'Total revenue',
                revenueLoading: 'Loading revenue indicators.',
                profitLabel: 'Gross profit',
                profitLoading: 'Loading margin signals.',
                ordersLabel: 'Orders',
                ordersLoading: 'Loading order operation signals.',
                customersLabel: 'Customers',
                customersLoading: 'Loading customer coverage.',
            },
            attention: {
                title: 'Immediate attention',
                description: 'Keep only the signals that could weaken the demo or reduce trust in the dashboards.',
            },
            roadmap: {
                title: 'Session route',
                description: 'Quickly confirm whether the data is reliable enough, then move to the right analytical or administrative surface.',
            },
            freshness: {
                loadingLabel: 'Calculating data freshness',
                loadingCaption: 'Once ETL logs are available, the platform will display the latest sync point here.',
            },
            nextAction: {
                eyebrow: 'Next step',
                loading: 'Preparing the next demo recommendation.',
            },
            focus: {
                analysis: {
                    title: 'Go to analytics',
                    description: 'One entry point for the full set of business reports.',
                    meta: '5 views',
                },
                etl: {
                    title: 'Review ETL',
                    description: 'Use this when you need to show that data was loaded recently and the logs are clean.',
                    meta: 'Pipeline',
                },
                admin: {
                    title: 'Open system administration',
                    description: 'Review branches, users, and ETL logs from one control surface.',
                    meta: 'Governance',
                },
                manage: {
                    title: 'Open branch administration',
                    description: 'Go directly to users in the current branch when you need to explain access scope.',
                    meta: 'Branch',
                },
            },
            foundation: {
                title: 'Platform baseline',
                description: 'Bring branches, users, and ETL issues into one row to understand platform status before going deeper.',
                tenantLabel: 'Branches',
                tenantLoading: 'Loading branch inventory.',
                userLabel: 'Users',
                userLoading: 'Loading user inventory.',
                issueLabel: 'ETL issues',
                issueLoading: 'Checking ETL failure logs.',
            },
        },
        analysis: {
            picker: {
                title: 'Analytical perspective',
                description: 'Select one analytical axis at a time to avoid opening too many dashboards in parallel.',
            },
            options: {
                revenue: {
                    label: 'Revenue',
                    summary: 'Revenue overview, period comparison, and variance across branches.',
                },
                products: {
                    label: 'Products',
                    summary: 'Best sellers, profit margins, and leading categories.',
                },
                inventory: {
                    label: 'Inventory',
                    summary: 'Stock shortages, inventory gaps, and revenue risks.',
                },
                customers: {
                    label: 'Customers',
                    summary: 'Segments, purchase behavior, and customer profiles in the DWH.',
                },
                employees: {
                    label: 'Employees',
                    summary: 'Sales performance and contribution by team.',
                },
            },
            dashboard: {
                revenue: {
                    title: 'Revenue Analytics Room',
                    description: 'Use this when you need to present the full revenue view by time, branch, or category.',
                },
                products: {
                    title: 'Product Analytics Room',
                    description: 'Open this when you need to explain which items drive growth, where profit sits, and which categories are leading.',
                },
                inventory: {
                    title: 'Inventory Analytics Room',
                    description: 'Use this when stakeholders ask about operational risk, minimum stock, and goods movement.',
                },
                customers: {
                    title: 'Customer Analytics Room',
                    description: 'Best suited for presenting how the warehouse supports customer profiling, RFM clusters, and lifetime value.',
                },
                employees: {
                    title: 'Employee Analytics Room',
                    description: 'Use this for sales, performance, and contribution analysis by sales staff.',
                },
            },
            stage: {
                eyebrow: 'Analytical axis',
                embedPill: 'Embedded from Superset',
                openModal: 'Open focus mode',
                contextLoading: 'Viewing axis: Revenue',
                frameLoading: 'Preparing the embedded dashboard.',
                iframeTitle: 'Analytical dashboard',
            },
            scope: {
                label: 'Reporting scope',
                loading: 'Loading branch list...',
            },
        },
        etl: {
            hero: {
                eyebrow: 'Load into staging',
                title: 'Move source files into the right branch and trigger the pipeline.',
                description: 'The ETL screen prioritizes operational actions first. Choose the scope, upload files, then verify that staging contains the correct data for the next run.',
            },
            scope: {
                label: 'Operating branch',
                loading: 'Loading branches...',
            },
            upload: {
                eyebrow: 'Source upload',
                title: 'Drag and drop source files or choose them manually.',
                description: 'Accepts `.xlsx`, `.xls`, and `.csv`. After upload, the recent file history is refreshed below so you can validate staging immediately.',
                chooseFiles: 'Choose source files',
                runNow: 'Run ETL now',
            },
            guide: {
                title: 'Source file guide',
                description: 'Keep naming consistent so ETL can classify files quickly and your demo explanation stays smooth.',
                revenueLabel: 'Revenue',
                revenueExample: 'Example: `BaoCaoDoanhThu_HN_20260101.xlsx`',
                inventoryLabel: 'Inventory',
                inventoryExample: 'Example: `QuanLyKho_HCM_20260101.xlsx`',
                catalogLabel: 'Catalog',
                catalogExample: 'Use `DanhMucSanPham.csv`, `DanhMucKhachHang.csv`, and `DanhMucNhaCungCap.csv`.',
                inboundLabel: 'Inbound',
                inboundExample: 'Use `PhieuNhapHang.csv` for the inbound inventory and supplier flow.',
            },
            library: {
                title: 'Recently uploaded files',
                description: 'Use this to confirm that staging contains the correct source data for the operating branch.',
                loading: 'Loading upload history.',
            },
        },
        manage: {
            create: {
                title: 'Create branch user',
                description: 'Use this for a new manager or viewer in branch {tenant}.',
            },
            form: {
                usernameLabel: 'Username',
                usernamePlaceholder: 'example: manager_cn1',
                passwordLabel: 'Password',
                passwordPlaceholder: 'At least 6 characters',
                submit: 'Create branch user',
            },
            users: {
                titleWithTenant: 'Users in branch {tenant}',
                description: 'This list helps control access status within the current branch scope.',
                roleHeader: 'Role',
                statusHeader: 'Status',
                createdAtHeader: 'Created on',
                actionsHeader: 'Actions',
                loading: 'Loading users...',
            },
        },
        admin: {
            createTenant: {
                title: 'Create new branch',
                description: 'Set up the branch, data path, and validity period for the multi-tenant platform.',
                idLabel: 'Branch code',
                idPlaceholder: 'example: STORE_DN',
                nameLabel: 'Branch name',
                namePlaceholder: 'example: Da Nang Store',
                pathLabel: 'Data path',
                expiresAtLabel: 'Expiry date',
                submit: 'Create branch',
            },
            createUser: {
                title: 'Create system user',
                description: 'Assign the user to a specific branch or leave it empty when wider access is required.',
                usernameLabel: 'Username',
                usernamePlaceholder: 'example: manager_dn',
                passwordLabel: 'Password',
                passwordPlaceholder: 'Enter the password',
                tenantLabel: 'Branch',
                roleLabel: 'Role',
                roleViewer: 'Viewer',
                roleAdmin: 'Admin',
                submit: 'Create user',
            },
            tenants: {
                title: 'Branch list',
                description: 'Review validity, status, and data paths for each branch.',
                searchLabel: 'Search branches',
                searchPlaceholder: 'Search by code, name, or path',
                idHeader: 'Code',
                nameHeader: 'Name',
                pathHeader: 'Path',
                statusHeader: 'Status',
                expiresAtHeader: 'Validity',
                actionsHeader: 'Actions',
                loading: 'Loading branches...',
            },
            users: {
                title: 'User list',
                description: 'Control rights and access scope for all users across the platform.',
                searchLabel: 'Search users',
                searchPlaceholder: 'Search by username, branch, or role',
                tenantHeader: 'Branch',
                roleHeader: 'Role',
                statusHeader: 'Status',
                actionsHeader: 'Actions',
                loading: 'Loading users...',
            },
            etl: {
                title: 'Recent ETL monitoring',
                description: 'Use this to explain data freshness, pipeline status, and system traceability.',
                loading: 'Loading ETL logs...',
            },
        },
        modals: {
            editTenant: {
                eyebrow: 'Edit branch',
                title: 'Edit branch',
                closeAria: 'Close the branch edit modal',
                nameLabel: 'Branch name',
                pathLabel: 'Data path',
                expiresAtLabel: 'Expiry date',
                statusLabel: 'Status',
                submit: 'Save branch changes',
            },
            editUser: {
                eyebrow: 'Edit user',
                title: 'Edit user',
                closeAria: 'Close the user edit modal',
                passwordLabel: 'New password',
                passwordPlaceholder: 'Leave blank to keep the current password',
                tenantLabel: 'Branch',
                roleLabel: 'Role',
                roleViewer: 'Viewer',
                roleAdmin: 'Admin',
                statusLabel: 'Status',
                submit: 'Save user changes',
            },
            viewUser: {
                eyebrow: 'User details',
                title: 'User details',
                closeAria: 'Close the user details modal',
                loading: 'Loading user details...',
                usernameLabel: 'Username',
                displayNameLabel: 'Display name',
                emailLabel: 'Email',
                phoneLabel: 'Phone number',
                tenantLabel: 'Branch',
                roleLabel: 'Role',
                statusLabel: 'Status',
                createdAtLabel: 'Created on',
            },
            focus: {
                eyebrow: 'Focus mode',
                title: 'Central analytics view',
                closeAria: 'Close the analytics modal',
                iframeTitle: 'Superset analytics view',
            },
            confirm: {
                eyebrow: 'Confirmation',
                title: 'Confirm action',
                closeAria: 'Close the confirmation dialog',
                detail: 'This action cannot be undone.',
            },
        },
        runtime: {
            analysis: {
                context: 'Viewing axis: {label}',
                scope: 'Reporting scope: {scope}',
                tokenLoading: 'Requesting the dashboard token and building the embedded session.',
                frameReady: 'Displaying the embedded dashboard through Superset.',
                frameError: 'Unable to build the embedded dashboard at this time.',
                frameFallback: 'Unable to load the embedded analytical report. Please sign in again or verify the Superset service.',
            },
            health: {
                stable: 'API stable',
                check: 'Check API',
                stableLabel: 'The authentication lane is responding normally',
                stableCopy: 'You can continue reviewing operational signals, opening analytics dashboards, or checking ETL.',
                failedLabel: 'The Auth Gateway is not responding or is returning an error state',
                failedCopy: 'Prioritize checking the platform services before presenting analytical dashboards.',
            },
            kpi: {
                revenueMeta: 'Use this to open the revenue narrative by branch and category.',
                profitMeta: 'Gross margin: {value}%',
                ordersMetaWithAlerts: '{count} inventory alerts are currently open.',
                ordersMetaEmpty: 'No urgent inventory alerts are recorded.',
                customersMeta: 'Monitor the customer coverage currently present in the platform.',
            },
            freshness: {
                noLogLabel: 'No recent ETL logs',
                noLogCaption: 'Run ETL or confirm the logging channel before presenting data freshness.',
                noLogTimestamp: 'No sync point available',
                freshLabel: 'Data is in a fresh window',
                remindLabel: 'Data freshness should be mentioned during the demo',
                staleLabel: 'Data has not been refreshed for a long time',
                latestRunAt: 'The latest ETL run started at {time}.',
                latestRunWas: 'The latest ETL run was at {time}.',
            },
            attention: {
                expiredTitle: '{tenant} has expired',
                expiredDetail: 'The branch should be renewed or its status explained clearly before providing dashboards.',
                inactiveTitle: '{tenant} is disabled',
                inactiveDetail: 'The branch is currently inactive. Confirm whether this is an intentional administrative state or an issue.',
                failingLogTitle: 'ETL failure at {tenant}',
                failingLogDetail: '{source} returned status {status} at {time}.',
                cleanTitle: 'No branch requires immediate action',
                cleanDetail: 'You can use the overview as the opening point and then move directly to the right analytical room.',
            },
            governance: {
                tenantLoaded: '{count} branches are active in the platform.',
                tenantLoading: 'This will appear once the branch list is loaded.',
                userLoaded: 'Includes system administrators and branch-level users.',
                userLoading: 'The administrative user list has not been loaded yet.',
                issueLoaded: 'There are failing ETL logs that should be explained or resolved.',
                issueLoading: 'No failing ETL logs are currently recorded in the available data.',
            },
            nextAction: {
                default: 'Open the Analytics Room and start with the revenue axis.',
                checkAuth: 'Check the Auth Gateway first, then continue with the dashboard presentation.',
                checkEtl: 'Go to ETL Operations or ETL Monitoring to explain the latest pipeline failure.',
                checkTenant: 'Open system administration to address the expired branch before continuing.',
                checkFreshness: 'State the latest ETL time clearly before moving deeper into analytical indicators.',
            },
            tables: {
                emptyTenants: 'No branches are available in the platform.',
                emptyTenantsFiltered: 'No branches match the current filter.',
                emptyUsers: 'No users are available in the platform.',
                emptyUsersFiltered: 'No users match the current filter.',
                emptyTenantUsers: 'This branch has no users yet.',
                emptyLogs: 'No ETL logs are available.',
                emptyLogsDetail: 'Recent records will appear here when the pipeline runs.',
                timeHeader: 'Time',
                tenantHeader: 'Branch',
                sourceHeader: 'Source',
                statusHeader: 'Status',
                rowsHeader: 'Rows',
                usernameHeader: 'Username',
                pathHeader: 'Path',
                roleHeader: 'Role',
                actionsHeader: 'Actions',
                expiresAtHeader: 'Validity',
                createdAtHeader: 'Created on',
                fileNameHeader: 'File name',
                fileTypeHeader: 'Type',
                fileSizeHeader: 'Size',
                uploadedAtHeader: 'Uploaded at',
                tenantIdLabel: 'Branch code',
                tenantNameLabel: 'Branch name',
                pathLabel: 'Path',
                statusLabel: 'Status',
                expiresAtLabel: 'Validity',
                actionsLabel: 'Actions',
                usernameLabel: 'Username',
                tenantLabel: 'Branch',
                roleLabel: 'Role',
                timeLabel: 'Time',
                sourceLabel: 'Source',
                rowsLabel: 'Rows',
                createdAtLabel: 'Created on',
                fileNameLabel: 'File name',
                fileTypeLabel: 'Type',
                fileSizeLabel: 'Size',
                uploadedAtLabel: 'Uploaded at',
                editTenant: 'Edit branch',
                viewUser: 'View details',
                editUser: 'Edit user',
                deleteFile: 'Delete file',
                unknownType: 'Unknown',
            },
            upload: {
                previewUpload: 'Upload to staging',
                previewRunEtl: 'Run ETL now',
                selectFile: 'Choose at least one file before uploading to staging.',
                runningTitle: 'Uploading {count} file(s) to staging',
                runningDetail: 'The platform is sending files to the upload API and checking the response.',
                successTitle: 'Uploaded {successful}/{total} file(s) to staging',
                successLine: '{marker} {filename}{type}{error}',
                failedTitle: 'Unable to upload files to staging',
            },
            etlRun: {
                selectTenant: 'Choose a branch before triggering ETL.',
                runningTitle: 'Triggering ETL for {tenant}',
                runningDetail: 'The pipeline will load data into the warehouse and create the related log.',
                successTitle: 'ETL was triggered for {tenant}',
                successDetail: 'Monitor ETL logs to review data loading progress.',
                failedTitle: 'ETL could not be started',
            },
            files: {
                noTenantTitle: 'No branch is currently selected.',
                noTenantDetail: 'Choose a branch before reviewing upload history.',
                emptyTitle: 'No files were uploaded recently.',
                emptyDetail: 'Uploaded files will appear here after the operation completes.',
                loadErrorTitle: 'File loading error.',
                deleteTitle: 'Delete file from staging',
                deleteDetail: 'File "{filename}" will be removed from branch {tenant}. This action cannot be undone.',
                deleteConfirm: 'Delete file',
                deleteSuccess: 'File {filename} was removed from staging.',
            },
            forms: {
                invalidTenantId: 'Enter a valid branch code.',
                creatingTenant: 'Creating branch...',
                tenantCreated: 'Branch {tenant} has been created.',
                saveTenantError: 'Unable to create branch',
                viewerNeedsTenant: 'A Viewer must be assigned to a specific branch.',
                creatingUser: 'Creating user...',
                userCreated: 'User {username} has been created.',
                saveUserError: 'Unable to create user',
                loadUsersError: 'Unable to load the user list',
                creatingTenantUser: 'Creating branch user...',
                savingChanges: 'Saving changes...',
                tenantSaved: 'Branch changes have been saved.',
                userSaved: 'User changes have been saved.',
                saveTenantUpdateError: 'Unable to save the branch',
                saveUserUpdateError: 'Unable to save the user',
                loadUserDetailError: 'Unable to load the user details',
                editTenantTitle: 'Edit branch {tenant}',
                editUserTitle: 'Edit user {username}',
            },
            scope: {
                currentTenant: 'Current branch: {tenant}',
            },
        },
    },
};

const DASHBOARD_MAP = {
    revenue: {
        id: 1,
        labelKey: 'analysis.options.revenue.label',
        titleKey: 'analysis.dashboard.revenue.title',
        descriptionKey: 'analysis.dashboard.revenue.description',
    },
    products: {
        id: 2,
        labelKey: 'analysis.options.products.label',
        titleKey: 'analysis.dashboard.products.title',
        descriptionKey: 'analysis.dashboard.products.description',
    },
    inventory: {
        id: 3,
        labelKey: 'analysis.options.inventory.label',
        titleKey: 'analysis.dashboard.inventory.title',
        descriptionKey: 'analysis.dashboard.inventory.description',
    },
    customers: {
        id: 4,
        labelKey: 'analysis.options.customers.label',
        titleKey: 'analysis.dashboard.customers.title',
        descriptionKey: 'analysis.dashboard.customers.description',
    },
    employees: {
        id: 5,
        labelKey: 'analysis.options.employees.label',
        titleKey: 'analysis.dashboard.employees.title',
        descriptionKey: 'analysis.dashboard.employees.description',
    },
};

const languageSelect = document.getElementById('languageSelect');
const i18n = window.DWHI18n.createPageI18n({
    copy: COPY,
    documentTitleKey: 'page.browserTitle',
    languageSelect,
});

const initialAnalysisTenantId = APP_CONTEXT.userRole === 'superadmin'
    ? (window.sessionStorage.getItem('dashboardAnalysisTenant') || '')
    : (APP_CONTEXT.userTenant || '');

const appState = {
    health: 'checking',
    kpi: {},
    tenants: [],
    users: [],
    etlLogs: [],
    tenantUsers: [],
    analysisTenantId: initialAnalysisTenantId,
    tenantSearchTerm: '',
    userSearchTerm: '',
    uploadedFiles: [],
    uploadedFilesTenant: APP_CONTEXT.userTenant || '',
    uploadedFilesError: '',
    activePage: APP_CONTEXT.defaultPage,
    activeAnalysis: DASHBOARD_MAP[APP_CONTEXT.defaultAnalysis] ? APP_CONTEXT.defaultAnalysis : 'revenue',
    uploadStatus: null,
    editingTenantId: '',
    editingUserName: '',
    viewingUser: null,
    viewingUserName: '',
    viewingUserError: '',
    userDetailCache: {},
    confirmDialog: null,
};

let confirmResolver = null;
const pendingRequests = {
    tenants: null,
    users: null,
    etlLogs: null,
};
let activeEmbedController = null;

function byId(id) {
    return document.getElementById(id);
}

const t = (path, params) => i18n.t(path, params);

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function getDashboardConfig(key) {
    const config = DASHBOARD_MAP[key];
    if (!config) return null;
    return {
        id: config.id,
        label: t(config.labelKey),
        title: t(config.titleKey),
        description: t(config.descriptionKey),
    };
}

function canSwitchAnalysisTenant() {
    return APP_CONTEXT.userRole === 'superadmin' && !APP_CONTEXT.userTenant;
}

function getAnalysisTenantRecord(tenantId) {
    return appState.tenants.find((tenant) => tenant.tenant_id === tenantId) || null;
}

function getActiveAnalysisTenantId() {
    if (canSwitchAnalysisTenant()) {
        return appState.analysisTenantId || '';
    }
    return APP_CONTEXT.userTenant || '';
}

function getAnalysisScopeLabel() {
    const tenantId = getActiveAnalysisTenantId();
    if (!tenantId) {
        return t('common.systemWide');
    }
    const tenant = getAnalysisTenantRecord(tenantId);
    if (tenant?.tenant_name) {
        return `${tenant.tenant_id} — ${tenant.tenant_name}`;
    }
    return tenantId;
}

function normalizeSearchTerm(value) {
    return String(value || '').trim().toLowerCase();
}

function includesSearch(haystack, needle) {
    return normalizeSearchTerm(haystack).includes(needle);
}

function tenantSearchIndex(tenant) {
    return [
        tenant.tenant_id,
        tenant.tenant_name,
        tenant.file_path,
        tenant.is_active ? t('common.active') : t('common.inactive'),
    ].join(' ');
}

function userSearchIndex(user) {
    return [
        user.username,
        user.tenant_id || t('common.systemWide'),
        i18n.roleLabel(user.role === 'superadmin' ? 'superadmin' : user.role === 'admin' ? 'admin' : 'viewer'),
        user.is_active ? t('common.active') : t('common.inactive'),
    ].join(' ');
}

function fetchTenants(options = {}) {
    return fetchCollection('/api/tenants', 'tenants', 'tenants', options);
}

function fetchUsers(options = {}) {
    return fetchCollection('/api/users', 'users', 'users', options);
}

function fetchEtlLogs(options = {}) {
    return fetchCollection('/api/etl/logs', 'etlLogs', 'etlLogs', { ...options, responseKey: 'logs' });
}

async function fetchUserDetail(userId, { force = false } = {}) {
    if (!force && appState.userDetailCache[userId]) {
        return appState.userDetailCache[userId];
    }

    const response = await authFetch(`/api/users/${userId}`);
    const data = await response.json();
    if (!response.ok || !data.user) {
        throw new Error(data.detail || data.error || t('runtime.forms.loadUserDetailError'));
    }

    appState.userDetailCache[userId] = data.user;
    return data.user;
}

function formatCurrency(value) {
    return i18n.formatCurrency(value);
}

function formatInteger(value) {
    return i18n.formatInteger(value);
}

function formatDateTime(value) {
    return i18n.formatDateTime(value);
}

function sortLogs(logs) {
    return [...logs].sort((left, right) => {
        const leftTime = new Date(left.start_time || 0).getTime();
        const rightTime = new Date(right.start_time || 0).getTime();
        return rightTime - leftTime;
    });
}

function isFailStatus(status) {
    return /fail|error|cancel|timeout|stopped/i.test(status || '');
}

function isSuccessStatus(status) {
    return /success|done|ok|completed|complete|finished/i.test(status || '');
}

function statusToneByBool(condition) {
    return condition ? 'tone-success' : 'tone-danger';
}

function toneVariant(toneClass) {
    return String(toneClass || 'tone-neutral').replace(/^tone-/, '');
}

function authFetch(url, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (APP_CONTEXT.accessToken) {
        headers.Authorization = `Bearer ${APP_CONTEXT.accessToken}`;
    }
    return fetch(url, { ...options, headers });
}

async function fetchCollection(url, stateKey, pendingKey, { force = false, fallback = [], responseKey = stateKey } = {}) {
    if (!force && pendingRequests[pendingKey]) {
        return pendingRequests[pendingKey];
    }

    if (!force && Array.isArray(appState[stateKey]) && appState[stateKey].length) {
        return appState[stateKey];
    }

    pendingRequests[pendingKey] = (async () => {
        const response = await authFetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        appState[stateKey] = Array.isArray(data[responseKey]) ? data[responseKey] : fallback;
        return appState[stateKey];
    })();

    try {
        return await pendingRequests[pendingKey];
    } finally {
        pendingRequests[pendingKey] = null;
    }
}

function setFormMessage(element, toneClass, translationKey = '', params = {}, fallbackMessage = '') {
    if (!element) return;
    element.textContent = translationKey ? t(translationKey, params) : fallbackMessage;
    element.className = `microcopy form-msg ${toneClass}`;
    i18n.setRuntimeCopy(element, translationKey, params);
}

function clearFormMessage(element) {
    if (!element) return;
    element.textContent = '';
    element.className = 'microcopy form-msg';
    i18n.setRuntimeCopy(element);
}

function showAlert(el, message = '', tone = 'danger', timeoutMs = 0, translationKey = '', params = {}) {
    if (!el) return;
    window.clearTimeout(el._hideTimer);
    el.textContent = translationKey ? t(translationKey, params) : message;
    const shellClass = el.classList.contains('shell-alert') ? 'shell-alert ' : '';
    el.className = `${shellClass}alert alert--${tone}`;
    el.classList.add('is-visible');
    el.classList.remove('is-hidden');
    i18n.setRuntimeCopy(el, translationKey, params);
    if (timeoutMs > 0) {
        el._hideTimer = window.setTimeout(() => hideAlert(el), timeoutMs);
    }
}

function hideAlert(el) {
    if (!el) return;
    window.clearTimeout(el._hideTimer);
    el.classList.remove('is-visible');
    el.classList.add('is-hidden');
    el.textContent = '';
    i18n.setRuntimeCopy(el);
}

function showShellAlert(message = '', tone = 'danger', timeoutMs = 5000, translationKey = '', params = {}) {
    showAlert(byId('shellAlert'), message, tone, timeoutMs, translationKey, params);
}

function setEmbedFallback({ iframeId, fallbackId, message = '' }) {
    const iframe = byId(iframeId);
    const fallback = byId(fallbackId);
    if (!iframe || !fallback) return;

    if (message) {
        iframe.classList.add('is-hidden');
        fallback.textContent = message;
        fallback.classList.remove('is-hidden');
        return;
    }

    fallback.textContent = '';
    fallback.classList.add('is-hidden');
    iframe.classList.remove('is-hidden');
}

function renderShellContext() {
    const tenant = APP_CONTEXT.userTenant || '';
    const scopeValue = tenant || t('common.systemWide');
    const roleValue = i18n.roleLabel(APP_CONTEXT.userRole);

    if (byId('sessionScope')) {
        byId('sessionScope').textContent = scopeValue;
    }
    if (byId('sessionRole')) {
        byId('sessionRole').textContent = roleValue;
    }
    if (byId('sidebarRoleLabel')) {
        byId('sidebarRoleLabel').textContent = roleValue;
    }
    if (byId('sidebarScopeText')) {
        byId('sidebarScopeText').textContent = `${t('sidebar.scopePrefix')}: ${scopeValue}`;
    }
    if (byId('sidebarScopeModeChip')) {
        byId('sidebarScopeModeChip').textContent = tenant ? t('sidebar.scopeBranchMode') : t('sidebar.scopeAll');
    }
    if (byId('tenantCreateUserDescription')) {
        byId('tenantCreateUserDescription').textContent = t('manage.create.description', { tenant: tenant || t('common.systemWide') });
    }
    if (byId('tenantUsersTitle')) {
        byId('tenantUsersTitle').textContent = t('manage.users.titleWithTenant', { tenant: tenant || t('common.systemWide') });
    }
    if (byId('etlCurrentTenantPill')) {
        byId('etlCurrentTenantPill').textContent = t('runtime.scope.currentTenant', { tenant });
    }
}

function renderAnalysisScope() {
    const scopePill = byId('analysisScopePill');
    if (scopePill) {
        scopePill.textContent = t('runtime.analysis.scope', { scope: getAnalysisScopeLabel() });
    }

    const scopeSelect = byId('analysisTenantSelect');
    if (!scopeSelect) return;

    const availableTenantIds = new Set(appState.tenants.map((tenant) => tenant.tenant_id));
    if (appState.analysisTenantId && !availableTenantIds.has(appState.analysisTenantId)) {
        appState.analysisTenantId = '';
        window.sessionStorage.setItem('dashboardAnalysisTenant', '');
    }

    const options = [
        `<option value="">${escapeHtml(t('common.systemWide'))}</option>`,
        ...appState.tenants.map((tenant) => (
            `<option value="${escapeHtml(tenant.tenant_id)}">${escapeHtml(`${tenant.tenant_id} — ${tenant.tenant_name || tenant.tenant_id}`)}</option>`
        )),
    ];

    scopeSelect.innerHTML = options.join('');
    scopeSelect.value = appState.analysisTenantId || '';
}

function setSidebarState() {
    document.body.classList.remove('sidebar-collapsed');
    if (window.innerWidth > 1024) {
        document.body.classList.remove('sidebar-open');
    }
    syncSidebarChrome();
}

function toggleSidebar() {
    if (window.innerWidth > 1024) {
        syncSidebarChrome();
        return;
    }
    document.body.classList.toggle('sidebar-open');
    syncSidebarChrome();
}

function closeSidebarOnMobile() {
    if (window.innerWidth <= 1024) {
        document.body.classList.remove('sidebar-open');
        syncSidebarChrome();
    }
}

function syncSidebarChrome() {
    const toggleButton = byId('toggleSidebar');
    const isExpanded = window.innerWidth > 1024 || document.body.classList.contains('sidebar-open');

    if (toggleButton) {
        toggleButton.setAttribute('aria-expanded', String(isExpanded));
    }
}

function updatePageChrome(page) {
    const target = document.querySelector(`.page[data-page="${page}"]`);
    if (!target) return;
    byId('pageTitle').textContent = target.dataset.pageTitleKey ? t(target.dataset.pageTitleKey) : target.querySelector('h2')?.textContent || t('pages.overview.eyebrow');
    byId('pageSubtitle').textContent = target.dataset.pageSubtitleKey ? t(target.dataset.pageSubtitleKey) : '';
    byId('pageEyebrow').textContent = target.dataset.pageEyebrowKey ? t(target.dataset.pageEyebrowKey) : t('pages.overview.eyebrow');
}

function setActiveAnalysis(key, { loadIframe = false } = {}) {
    const dashboardKey = DASHBOARD_MAP[key] ? key : appState.activeAnalysis;
    const config = getDashboardConfig(dashboardKey);
    if (!config) return;

    appState.activeAnalysis = dashboardKey;

    document.querySelectorAll('[data-dashboard-key]').forEach((button) => {
        const active = button.dataset.dashboardKey === dashboardKey;
        button.classList.toggle('is-active', active);
        button.setAttribute('aria-pressed', String(active));
    });

    if (byId('analysisTitle')) {
        byId('analysisTitle').textContent = config.title;
    }
    if (byId('analysisDescription')) {
        byId('analysisDescription').textContent = config.description;
    }
    if (byId('analysisContextPill')) {
        byId('analysisContextPill').textContent = t('runtime.analysis.context', { label: config.label });
    }
    renderAnalysisScope();

    const modalButton = byId('analysisOpenModalBtn');
    if (modalButton) {
        modalButton.dataset.openDashboard = String(config.id);
    }

    if (loadIframe) {
        loadSupersetIframe(dashboardKey, {
            iframeId: 'iframe-analysis',
            frameStateId: 'frameState-analysis',
        });
    }
}

function navigateTo(requestedPage) {
    let page = requestedPage;
    if (DASHBOARD_MAP[requestedPage]) {
        appState.activeAnalysis = requestedPage;
        page = 'analysis';
    }

    const target = document.querySelector(`.page[data-page="${page}"]`);
    if (!target) return false;

    appState.activePage = page;

    document.querySelectorAll('.nav-link[data-page]').forEach((link) => {
        link.classList.toggle('is-active', link.dataset.page === page);
    });
    document.querySelectorAll('.page').forEach((section) => {
        section.classList.toggle('is-active', section.dataset.page === page);
    });
    updatePageChrome(page);
    closeSidebarOnMobile();

    if (page === 'analysis') {
        setActiveAnalysis(appState.activeAnalysis, { loadIframe: true });
    }

    return true;
}

function bindNavigation() {
    document.querySelectorAll('.nav-link[data-page]').forEach((link) => {
        link.addEventListener('click', () => navigateTo(link.dataset.page));
    });

    document.querySelectorAll('[data-open-page]').forEach((button) => {
        button.addEventListener('click', () => navigateTo(button.dataset.openPage));
    });

    document.querySelectorAll('[data-dashboard-key]').forEach((button) => {
        button.addEventListener('click', () => {
            const key = button.dataset.dashboardKey;
            appState.activeAnalysis = key;
            if (appState.activePage !== 'analysis') {
                navigateTo('analysis');
                return;
            }
            setActiveAnalysis(key, { loadIframe: true });
        });
    });

    document.querySelectorAll('[data-open-dashboard]').forEach((button) => {
        button.addEventListener('click', () => openSupersetDashboard(Number(button.dataset.openDashboard)));
    });
}

function renderEmbeddedDashboard(iframe, data) {
    if (!data.guest_token) {
        throw new Error('Missing guest token');
    }

    const fallbackUrl = data.embedded_dashboard_uuid
        ? `${APP_CONTEXT.supersetUrl}/embedded/${data.embedded_dashboard_uuid}`
        : null;
    const dashboardUrl = data.dashboard_url || fallbackUrl;
    if (!dashboardUrl) {
        throw new Error('Missing embedded dashboard URL');
    }

    const url = new URL(dashboardUrl, window.location.origin);
    url.searchParams.set('standalone', '2');

    iframe.onload = function () {
        const channel = new MessageChannel();
        const messageId = `guest_token_${Date.now()}_${Math.random().toString(16).slice(2)}`;

        channel.port1.onmessage = function (event) {
            const message = event.data || {};
            if (message.messageId !== messageId) return;
        };
        channel.port1.start();

        iframe.contentWindow.postMessage(
            { type: '__embedded_comms__', handshake: 'port transfer' },
            url.origin,
            [channel.port2]
        );

        window.setTimeout(() => {
            channel.port1.postMessage({
                switchboardAction: 'get',
                method: 'guestToken',
                messageId,
                args: { guestToken: data.guest_token },
            });
        }, 120);
    };

    iframe.src = url.toString();
}

async function loadSupersetIframe(dashboardKey, { iframeId = 'iframe-analysis', frameStateId = 'frameState-analysis' } = {}) {
    const config = getDashboardConfig(dashboardKey);
    const iframe = byId(iframeId);
    if (!config || !iframe) return;

    setEmbedFallback({ iframeId, fallbackId: iframeId === 'modalIframe' ? 'modalFallback' : 'frameFallback-analysis' });
    const frameState = byId(frameStateId);
    if (frameState) frameState.textContent = t('runtime.analysis.tokenLoading');

    if (activeEmbedController) {
        activeEmbedController.abort();
    }

    const controller = new AbortController();
    activeEmbedController = controller;

    try {
        const params = new URLSearchParams({ dashboard_id: String(config.id) });
        const analysisTenantId = getActiveAnalysisTenantId();
        if (canSwitchAnalysisTenant() && analysisTenantId) {
            params.set('tenant_id', analysisTenantId);
        }

        const response = await fetch(`/api/dashboard-token?${params.toString()}`, { signal: controller.signal });
        if (!response.ok) throw new Error('Token error');
        const data = await response.json();
        if (activeEmbedController !== controller) return;
        renderEmbeddedDashboard(iframe, data);
        if (frameState) frameState.textContent = t('runtime.analysis.frameReady');
    } catch (error) {
        if (error?.name === 'AbortError') {
            return;
        }
        setEmbedFallback({
            iframeId,
            fallbackId: iframeId === 'modalIframe' ? 'modalFallback' : 'frameFallback-analysis',
            message: t('runtime.analysis.frameFallback'),
        });
        if (frameState) frameState.textContent = t('runtime.analysis.frameError');
    } finally {
        if (activeEmbedController === controller) {
            activeEmbedController = null;
        }
    }
}

function toggleModal(id, visible) {
    const modal = byId(id);
    if (!modal) return;
    modal.classList.toggle('is-visible', visible);
}

async function openSupersetDashboard(dashboardId) {
    const dashboardKey = Object.keys(DASHBOARD_MAP).find((key) => DASHBOARD_MAP[key].id === dashboardId) || appState.activeAnalysis;
    const currentConfig = getDashboardConfig(dashboardKey);
    byId('modalTitle').textContent = currentConfig ? currentConfig.title : t('modals.focus.title');
    toggleModal('modalOverlay', true);
    await loadSupersetIframe(
        dashboardKey,
        { iframeId: 'modalIframe', frameStateId: null }
    );
}

function closeModal() {
    toggleModal('modalOverlay', false);
    byId('modalIframe').src = 'about:blank';
    setEmbedFallback({ iframeId: 'modalIframe', fallbackId: 'modalFallback' });
}

function closeConfirmModal(confirmed = false) {
    toggleModal('modalConfirm', false);
    if (confirmResolver) {
        confirmResolver(confirmed);
        confirmResolver = null;
    }
    if (confirmed || !document.querySelector('#modalConfirm.is-visible')) {
        appState.confirmDialog = null;
    }
}

function renderConfirmDialog() {
    if (!appState.confirmDialog) return;
    const { titleKey, detailKey, confirmLabelKey, params } = appState.confirmDialog;
    byId('confirmTitle').textContent = t(titleKey, params);
    byId('confirmDetail').textContent = t(detailKey, params);
    byId('confirmActionBtn').textContent = t(confirmLabelKey, params);
}

function requestConfirmation({ titleKey, detailKey, confirmLabelKey = 'common.confirm', params = {} }) {
    appState.confirmDialog = { titleKey, detailKey, confirmLabelKey, params };
    renderConfirmDialog();
    toggleModal('modalConfirm', true);
    return new Promise((resolve) => {
        confirmResolver = resolve;
    });
}

async function checkHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        appState.health = data.api === 'ok' ? 'ok' : 'error';
    } catch (error) {
        appState.health = 'error';
    }
    renderHealthState();
    renderOverviewIntel();
}

function renderHealthState() {
    const indicator = byId('healthIndicator');
    const healthLabel = byId('overviewHealthLabel');
    const healthCopy = byId('overviewHealthCopy');
    if (!indicator || !healthLabel || !healthCopy) return;

    if (appState.health === 'checking') {
        indicator.innerHTML = `<span class="status-pill status-pill--plain tone-neutral">${escapeHtml(t('sidebar.healthLoading'))}</span>`;
        healthLabel.textContent = t('overview.health.loadingLabel');
        healthCopy.textContent = t('overview.health.loadingCopy');
        return;
    }

    const liveStatus = appState.health === 'ok';

    indicator.innerHTML = `
        <span class="status-pill status-pill--plain ${liveStatus ? 'tone-success' : 'tone-danger'}">
            <span class="health-dot ${liveStatus ? 'is-live' : 'is-danger'}"></span>
            ${liveStatus ? escapeHtml(t('sidebar.healthHealthy')) : escapeHtml(t('sidebar.healthCheck'))}
        </span>
    `;

    healthLabel.textContent = liveStatus
        ? t('runtime.health.stableLabel')
        : t('runtime.health.failedLabel');
    healthCopy.textContent = liveStatus
        ? t('runtime.health.stableCopy')
        : t('runtime.health.failedCopy');
}

async function loadKPIs() {
    try {
        const response = await fetch('/api/kpi');
        if (!response.ok) return;
        const data = await response.json();
        appState.kpi = data.kpi || {};
        renderKPIs();
    } catch (error) {}
}

function renderKPIs() {
    const kpi = appState.kpi;
    byId('kpi-revenue').textContent = formatCurrency(kpi.total_revenue || 0);
    byId('kpi-profit').textContent = formatCurrency(kpi.total_profit || 0);
    byId('kpi-orders').textContent = formatInteger(kpi.total_orders || 0);
    byId('kpi-customers').textContent = formatInteger(kpi.total_customers || 0);
    byId('kpi-revenue-change').textContent = t('runtime.kpi.revenueMeta');
    byId('kpi-profit-change').textContent = t('runtime.kpi.profitMeta', { value: kpi.profit_margin_pct || 0 });
    byId('kpi-orders-change').textContent = (kpi.low_stock_alerts || 0) > 0
        ? t('runtime.kpi.ordersMetaWithAlerts', { count: kpi.low_stock_alerts || 0 })
        : t('runtime.kpi.ordersMetaEmpty');
    byId('kpi-customers-change').textContent = t('runtime.kpi.customersMeta');
    renderOverviewIntel();
}

function getFreshnessInfo() {
    const latestLog = sortLogs(appState.etlLogs)[0];
    if (!latestLog?.start_time) {
        return {
            tone: 'tone-warning',
            label: t('runtime.freshness.noLogLabel'),
            caption: t('runtime.freshness.noLogCaption'),
            timestamp: t('runtime.freshness.noLogTimestamp'),
        };
    }

    const latestDate = new Date(latestLog.start_time);
    const diffHours = (Date.now() - latestDate.getTime()) / 36e5;
    if (diffHours <= 8) {
        return {
            tone: 'tone-success',
            label: t('runtime.freshness.freshLabel'),
            caption: t('runtime.freshness.latestRunAt', { time: formatDateTime(latestLog.start_time) }),
            timestamp: formatDateTime(latestLog.start_time),
        };
    }
    if (diffHours <= 24) {
        return {
            tone: 'tone-warning',
            label: t('runtime.freshness.remindLabel'),
            caption: t('runtime.freshness.latestRunAt', { time: formatDateTime(latestLog.start_time) }),
            timestamp: formatDateTime(latestLog.start_time),
        };
    }
    return {
        tone: 'tone-danger',
        label: t('runtime.freshness.staleLabel'),
        caption: t('runtime.freshness.latestRunWas', { time: formatDateTime(latestLog.start_time) }),
        timestamp: formatDateTime(latestLog.start_time),
    };
}

function renderAttentionList() {
    const container = byId('tenantAttentionList');
    if (!container) return;

    const items = [];
    const now = new Date();
    const expired = appState.tenants.filter((tenant) => tenant.expires_at && new Date(tenant.expires_at) < now);
    const inactive = appState.tenants.filter((tenant) => !tenant.is_active);
    const latestFailingLogs = sortLogs(appState.etlLogs).filter((log) => isFailStatus(log.status)).slice(0, 2);

    expired.forEach((tenant) => {
        items.push({
            tone: 'tone-danger',
            title: t('runtime.attention.expiredTitle', { tenant: tenant.tenant_id }),
            detail: t('runtime.attention.expiredDetail'),
        });
    });

    inactive.forEach((tenant) => {
        items.push({
            tone: 'tone-warning',
            title: t('runtime.attention.inactiveTitle', { tenant: tenant.tenant_id }),
            detail: t('runtime.attention.inactiveDetail'),
        });
    });

    latestFailingLogs.forEach((log) => {
        items.push({
            tone: 'tone-danger',
            title: t('runtime.attention.failingLogTitle', { tenant: log.tenant_id || t('common.unknown') }),
            detail: t('runtime.attention.failingLogDetail', {
                source: log.source_table || t('runtime.tables.sourceHeader'),
                status: log.status || t('common.unknown'),
                time: formatDateTime(log.start_time),
            }),
        });
    });

    if (!items.length) {
        items.push({
            tone: 'tone-success',
            title: t('runtime.attention.cleanTitle'),
            detail: t('runtime.attention.cleanDetail'),
        });
    }

    container.innerHTML = items.slice(0, 4).map((item) => `
        <article class="attention-item attention-item--${toneVariant(item.tone)}">
            <div class="attention-item__head">
                <span class="status-pill status-pill--plain ${item.tone}">${item.title}</span>
            </div>
            <p>${escapeHtml(item.detail)}</p>
        </article>
    `).join('');
}

function renderGovernanceStats() {
    const tenantCount = appState.tenants.length;
    const activeTenantCount = appState.tenants.filter((tenant) => tenant.is_active).length;
    const etlIssues = appState.etlLogs.filter((log) => isFailStatus(log.status)).length;
    const users = appState.users.length;

    if (byId('tenantInventoryCount')) {
        byId('tenantInventoryCount').textContent = formatInteger(tenantCount);
        byId('tenantInventoryNote').textContent = tenantCount
            ? t('runtime.governance.tenantLoaded', { count: activeTenantCount })
            : t('runtime.governance.tenantLoading');
    }

    if (byId('userInventoryCount')) {
        byId('userInventoryCount').textContent = formatInteger(users);
        byId('userInventoryNote').textContent = users
            ? t('runtime.governance.userLoaded')
            : t('runtime.governance.userLoading');
    }

    if (byId('etlIssueCount')) {
        byId('etlIssueCount').textContent = formatInteger(etlIssues);
        byId('etlIssueNote').textContent = etlIssues
            ? t('runtime.governance.issueLoaded')
            : t('runtime.governance.issueLoading');
    }
}

function renderNextAction() {
    const freshness = getFreshnessInfo();
    let nextAction = t('runtime.nextAction.default');

    if (appState.health !== 'ok') {
        nextAction = t('runtime.nextAction.checkAuth');
    } else if (appState.etlLogs.some((log) => isFailStatus(log.status))) {
        nextAction = t('runtime.nextAction.checkEtl');
    } else if (appState.tenants.some((tenant) => tenant.expires_at && new Date(tenant.expires_at) < new Date())) {
        nextAction = t('runtime.nextAction.checkTenant');
    } else if (freshness.tone === 'tone-warning' || freshness.tone === 'tone-danger') {
        nextAction = t('runtime.nextAction.checkFreshness');
    }

    if (byId('nextActionText')) {
        byId('nextActionText').textContent = nextAction;
    }
}

function renderOverviewIntel() {
    const freshness = getFreshnessInfo();
    if (byId('freshnessTone')) {
        byId('freshnessTone').className = `status-pill ${freshness.tone}`;
        byId('freshnessTone').textContent = freshness.label;
    }
    if (byId('freshnessCaption')) {
        byId('freshnessCaption').textContent = freshness.caption;
    }
    if (byId('lastSyncTime')) {
        byId('lastSyncTime').textContent = freshness.timestamp;
    }
    if (byId('overviewTimestamp')) {
        byId('overviewTimestamp').textContent = formatDateTime(new Date());
    }

    renderShellContext();
    renderAttentionList();
    renderGovernanceStats();
    renderNextAction();
}

function tableEmpty(message, colspan) {
    return `<tr><td colspan="${colspan}"><div class="empty-state"><strong>${escapeHtml(message)}</strong></div></td></tr>`;
}

function actionIcon(icon) {
    if (icon === 'view') {
        return `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true">
                <path d="M2 12s3.6-6 10-6 10 6 10 6-3.6 6-10 6-10-6-10-6Z"/>
                <circle cx="12" cy="12" r="3"/>
            </svg>
        `;
    }

    return `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" aria-hidden="true">
            <path d="M12 20h9"/>
            <path d="M16.5 3.5a2.12 2.12 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5Z"/>
        </svg>
    `;
}

function renderTenants(tenants) {
    const container = byId('tenant-list');
    if (!container) return;
    const searchTerm = normalizeSearchTerm(appState.tenantSearchTerm);
    const filteredTenants = searchTerm
        ? tenants.filter((tenant) => includesSearch(tenantSearchIndex(tenant), searchTerm))
        : tenants;

    if (!filteredTenants.length) {
        container.innerHTML = tableEmpty(
            t(searchTerm ? 'runtime.tables.emptyTenantsFiltered' : 'runtime.tables.emptyTenants'),
            6
        );
        return;
    }
    const now = new Date();
    container.innerHTML = filteredTenants.map((tenant) => {
        const expired = tenant.expires_at && new Date(tenant.expires_at) < now;
        return `
            <tr>
                <td data-label="${escapeHtml(t('runtime.tables.tenantIdLabel'))}"><strong>${escapeHtml(tenant.tenant_id)}</strong></td>
                <td data-label="${escapeHtml(t('runtime.tables.tenantNameLabel'))}">${escapeHtml(tenant.tenant_name)}</td>
                <td data-label="${escapeHtml(t('runtime.tables.pathLabel'))}">${escapeHtml(tenant.file_path || '—')}</td>
                <td data-label="${escapeHtml(t('runtime.tables.statusLabel'))}"><span class="status-pill ${statusToneByBool(tenant.is_active)}">${tenant.is_active ? t('common.active') : t('common.inactive')}</span></td>
                <td data-label="${escapeHtml(t('runtime.tables.expiresAtLabel'))}">
                    <span class="status-pill ${expired ? 'tone-danger' : tenant.expires_at ? 'tone-warning' : 'tone-neutral'}">
                        ${tenant.expires_at ? formatDateTime(tenant.expires_at) : t('common.noLimit')}
                    </span>
                </td>
                <td data-label="${escapeHtml(t('runtime.tables.actionsLabel'))}">
                    <div class="table-actions">
                        <button
                            class="icon-button table-action-icon"
                            type="button"
                            data-edit-tenant="${escapeHtml(tenant.tenant_id)}"
                            title="${escapeHtml(t('runtime.tables.editTenant'))}"
                            aria-label="${escapeHtml(t('runtime.tables.editTenant'))}"
                        >
                            ${actionIcon('edit')}
                            <span class="visually-hidden">${escapeHtml(t('runtime.tables.editTenant'))}</span>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

function renderUsers(users) {
    const container = byId('user-list');
    if (!container) return;
    const searchTerm = normalizeSearchTerm(appState.userSearchTerm);
    const filteredUsers = searchTerm
        ? users.filter((user) => includesSearch(userSearchIndex(user), searchTerm))
        : users;

    if (!filteredUsers.length) {
        container.innerHTML = tableEmpty(
            t(searchTerm ? 'runtime.tables.emptyUsersFiltered' : 'runtime.tables.emptyUsers'),
            5
        );
        return;
    }
    container.innerHTML = filteredUsers.map((user) => {
        return `
        <tr>
            <td data-label="${escapeHtml(t('runtime.tables.usernameLabel'))}"><strong>${escapeHtml(user.username)}</strong></td>
            <td data-label="${escapeHtml(t('runtime.tables.tenantLabel'))}">${escapeHtml(user.tenant_id || '—')}</td>
            <td data-label="${escapeHtml(t('runtime.tables.roleLabel'))}"><span class="status-pill ${user.role === 'admin' ? 'tone-warning' : 'tone-neutral'}">${escapeHtml(i18n.roleLabel(user.role === 'superadmin' ? 'superadmin' : user.role === 'admin' ? 'admin' : 'viewer'))}</span></td>
            <td data-label="${escapeHtml(t('runtime.tables.statusLabel'))}"><span class="status-pill ${statusToneByBool(user.is_active)}">${user.is_active ? t('common.active') : t('common.inactive')}</span></td>
            <td data-label="${escapeHtml(t('runtime.tables.actionsLabel'))}">
                <div class="table-actions">
                    <button
                        class="icon-button table-action-icon"
                        type="button"
                        data-view-user
                        data-user-id="${Number(user.user_id)}"
                        data-username="${escapeHtml(user.username || '')}"
                        title="${escapeHtml(t('runtime.tables.viewUser'))}"
                        aria-label="${escapeHtml(t('runtime.tables.viewUser'))}"
                    >
                        ${actionIcon('view')}
                        <span class="visually-hidden">${escapeHtml(t('runtime.tables.viewUser'))}</span>
                    </button>
                    <button
                        class="icon-button table-action-icon"
                        type="button"
                        data-edit-user
                        data-user-id="${Number(user.user_id)}"
                        data-username="${escapeHtml(user.username || '')}"
                        data-tenant="${escapeHtml(user.tenant_id || '')}"
                        data-role="${escapeHtml(user.role || 'viewer')}"
                        data-active="${Boolean(user.is_active)}"
                        title="${escapeHtml(t('runtime.tables.editUser'))}"
                        aria-label="${escapeHtml(t('runtime.tables.editUser'))}"
                    >
                        ${actionIcon('edit')}
                        <span class="visually-hidden">${escapeHtml(t('runtime.tables.editUser'))}</span>
                    </button>
                </div>
            </td>
        </tr>
    `;
    }).join('');
}

function renderETLLogs(logs) {
    const container = byId('etl-logs');
    if (!container) return;
    if (!logs.length) {
        container.innerHTML = `<div class="empty-state"><strong>${escapeHtml(t('runtime.tables.emptyLogs'))}</strong><span class="microcopy">${escapeHtml(t('runtime.tables.emptyLogsDetail'))}</span></div>`;
        return;
    }

    container.innerHTML = `
        <div class="table-shell table-shell--scroll table-shell--tall">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>${escapeHtml(t('runtime.tables.timeHeader'))}</th>
                        <th>${escapeHtml(t('runtime.tables.tenantHeader'))}</th>
                        <th>${escapeHtml(t('runtime.tables.sourceHeader'))}</th>
                        <th>${escapeHtml(t('runtime.tables.statusHeader'))}</th>
                        <th>${escapeHtml(t('runtime.tables.rowsHeader'))}</th>
                    </tr>
                </thead>
                <tbody>
                    ${sortLogs(logs).slice(0, 20).map((log) => `
                        <tr>
                            <td data-label="${escapeHtml(t('runtime.tables.timeLabel'))}">${formatDateTime(log.start_time)}</td>
                            <td data-label="${escapeHtml(t('runtime.tables.tenantLabel'))}"><strong>${escapeHtml(log.tenant_id || '—')}</strong></td>
                            <td data-label="${escapeHtml(t('runtime.tables.sourceLabel'))}">${escapeHtml(log.source_table || '—')}</td>
                            <td data-label="${escapeHtml(t('runtime.tables.statusLabel'))}"><span class="status-pill ${isFailStatus(log.status) ? 'tone-danger' : isSuccessStatus(log.status) ? 'tone-success' : 'tone-neutral'}">${escapeHtml(log.status || '—')}</span></td>
                            <td data-label="${escapeHtml(t('runtime.tables.rowsLabel'))}" class="tabular">${formatInteger(log.rows_inserted || 0)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function loadAdminData({ force = false } = {}) {
    if (force) {
        appState.userDetailCache = {};
    }

    await Promise.allSettled([
        fetchTenants({ force }),
        fetchUsers({ force }),
        fetchEtlLogs({ force }),
    ]);

    renderTenants(appState.tenants);
    renderUsers(appState.users);
    renderETLLogs(appState.etlLogs);
    populateTenantDropdown();
    populateETLTenantSelect();
    renderAnalysisScope();

    renderOverviewIntel();
}

function renderUploadStatus() {
    const status = byId('uploadStatus');
    const iconEl = byId('statusIcon');
    const titleEl = byId('statusText');
    const detailEl = byId('statusDetail');
    if (!status || !iconEl || !titleEl || !detailEl) return;

    if (!appState.uploadStatus) {
        status.hidden = true;
        iconEl.innerHTML = '';
        titleEl.textContent = '';
        detailEl.innerHTML = '';
        return;
    }

    const state = appState.uploadStatus;
    let toneClass = 'is-running';
    let icon = '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" fill="none"></circle><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path>';
    let title = '';
    let detail = '';

    if (state.kind === 'upload-running') {
        toneClass = 'is-running';
        title = t('runtime.upload.runningTitle', { count: state.fileCount });
        detail = `<p>${escapeHtml(t('runtime.upload.runningDetail'))}</p>`;
    } else if (state.kind === 'upload-success') {
        toneClass = 'is-success';
        icon = '<path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"></path>';
        title = t('runtime.upload.successTitle', {
            successful: state.successfulUploads,
            total: state.totalFiles,
        });
        detail = state.uploadedFiles.map((file) => {
            const marker = file.success ? '✓' : '✕';
            const type = file.file_type ? ` · ${escapeHtml(file.file_type)}` : '';
            const error = file.error ? ` · ${escapeHtml(file.error)}` : '';
            return `<p>${escapeHtml(t('runtime.upload.successLine', { marker, filename: file.filename }))}${type}${error}</p>`;
        }).join('');
    } else if (state.kind === 'upload-error') {
        toneClass = 'is-error';
        icon = '<path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>';
        title = t('runtime.upload.failedTitle');
        detail = `<p>${escapeHtml(state.message)}</p>`;
    } else if (state.kind === 'etl-running') {
        toneClass = 'is-running';
        title = t('runtime.etlRun.runningTitle', { tenant: state.tenant });
        detail = `<p>${escapeHtml(t('runtime.etlRun.runningDetail'))}</p>`;
    } else if (state.kind === 'etl-success') {
        toneClass = 'is-success';
        icon = '<path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"></path>';
        title = t('runtime.etlRun.successTitle', { tenant: state.tenant });
        detail = `<p>${escapeHtml(state.message || t('runtime.etlRun.successDetail'))}</p>`;
    } else if (state.kind === 'etl-error') {
        toneClass = 'is-error';
        icon = '<path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>';
        title = t('runtime.etlRun.failedTitle');
        detail = `<p>${escapeHtml(state.message)}</p>`;
    }

    status.className = `workflow-status ${toneClass}`;
    status.hidden = false;
    iconEl.innerHTML = icon;
    titleEl.textContent = title;
    detailEl.innerHTML = detail;
}

function setUploadStatus(nextStatus) {
    appState.uploadStatus = nextStatus;
    renderUploadStatus();
}

function currentTenant() {
    const select = byId('etlTenantSelect');
    return select ? select.value : (APP_CONTEXT.userTenant || '');
}

async function populateETLTenantSelect() {
    const select = byId('etlTenantSelect');
    if (!select) return;
    try {
        const tenants = await fetchTenants();
        if (!tenants.length) return;
        const selectedValue = select.value || '';
        select.innerHTML = tenants.map((tenant) => `<option value="${tenant.tenant_id}">${tenant.tenant_id} — ${tenant.tenant_name}</option>`).join('');
        select.value = selectedValue || tenants[0].tenant_id;
    } catch (error) {}
}

function showFilePreview() {
    const input = byId('fileInput');
    const preview = byId('uploadPreview');
    if (!input || !preview || !input.files.length) return;

    preview.innerHTML = `
        <div class="preview-list">
            ${Array.from(input.files).map((file) => `
                <article class="preview-item">
                    <strong>${escapeHtml(file.name)}</strong>
                    <span>${escapeHtml(i18n.formatFileSize(file.size))}</span>
                </article>
            `).join('')}
        </div>
        <div class="inline-actions">
            <button class="button button--primary" id="btnUploadSubmit" type="button">${escapeHtml(t('runtime.upload.previewUpload'))}</button>
            <button class="button button--secondary" type="button" id="btnRunEtl">${escapeHtml(t('runtime.upload.previewRunEtl'))}</button>
        </div>
    `;

    byId('btnUploadSubmit').addEventListener('click', uploadFile);
    byId('btnRunEtl').addEventListener('click', () => triggerETL(currentTenant()));
}

async function uploadFile() {
    const input = byId('fileInput');
    if (!input?.files.length) {
        showShellAlert('', 'danger', 5000, 'runtime.upload.selectFile');
        return;
    }

    const formData = new FormData();
    for (const file of input.files) {
        formData.append('files', file);
    }

    const submitButton = byId('btnUploadSubmit');
    if (submitButton) submitButton.disabled = true;

    setUploadStatus({ kind: 'upload-running', fileCount: input.files.length });

    try {
        const response = await authFetch(`/api/upload/${currentTenant()}`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.detail || data.message || t('runtime.upload.failedTitle'));
        }

        setUploadStatus({
            kind: 'upload-success',
            successfulUploads: data.successful_uploads,
            totalFiles: data.total_files,
            uploadedFiles: data.uploaded_files || [],
        });

        input.value = '';
        byId('uploadPreview').innerHTML = '';
        await loadUploadedFiles();
    } catch (error) {
        setUploadStatus({ kind: 'upload-error', message: error.message });
    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}

async function triggerETL(tenant) {
    if (!tenant) {
        showShellAlert('', 'danger', 5000, 'runtime.etlRun.selectTenant');
        return;
    }

    setUploadStatus({ kind: 'etl-running', tenant });

    try {
        const response = await authFetch(`/api/upload/${tenant}/etl`, { method: 'POST' });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.detail || data.message || t('runtime.etlRun.failedTitle'));
        }

        setUploadStatus({
            kind: 'etl-success',
            tenant,
            message: data.message || t('runtime.etlRun.successDetail'),
        });

        if (APP_CONTEXT.userRole === 'superadmin') {
            await loadAdminData({ force: true });
        }
    } catch (error) {
        setUploadStatus({ kind: 'etl-error', message: error.message });
    }
}

function renderUploadedFiles() {
    const container = byId('uploadedFilesList');
    if (!container) return;
    const tenant = appState.uploadedFilesTenant;

    if (!tenant) {
        container.innerHTML = `<div class="empty-state"><strong>${escapeHtml(t('runtime.files.noTenantTitle'))}</strong><span class="microcopy">${escapeHtml(t('runtime.files.noTenantDetail'))}</span></div>`;
        return;
    }

    if (appState.uploadedFilesError) {
        container.innerHTML = `<div class="empty-state"><strong>${escapeHtml(t('runtime.files.loadErrorTitle'))}</strong><span class="microcopy">${escapeHtml(appState.uploadedFilesError)}</span></div>`;
        return;
    }

    const files = appState.uploadedFiles;
    if (!files.length) {
        container.innerHTML = `<div class="empty-state"><strong>${escapeHtml(t('runtime.files.emptyTitle'))}</strong><span class="microcopy">${escapeHtml(t('runtime.files.emptyDetail'))}</span></div>`;
        return;
    }

    container.innerHTML = `
            <div class="table-shell table-shell--scroll table-shell--compact">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>${escapeHtml(t('runtime.tables.fileNameHeader'))}</th>
                            <th>${escapeHtml(t('runtime.tables.fileTypeHeader'))}</th>
                            <th>${escapeHtml(t('runtime.tables.fileSizeHeader'))}</th>
                            <th>${escapeHtml(t('runtime.tables.uploadedAtHeader'))}</th>
                            ${['admin', 'superadmin'].includes(APP_CONTEXT.userRole) ? `<th>${escapeHtml(t('runtime.tables.actionsHeader'))}</th>` : ''}
                        </tr>
                    </thead>
                    <tbody>
                        ${files.map((file) => `
                            <tr>
                                <td data-label="${escapeHtml(t('runtime.tables.fileNameLabel'))}"><strong>${escapeHtml(file.filename)}</strong></td>
                                <td data-label="${escapeHtml(t('runtime.tables.fileTypeLabel'))}"><span class="status-pill tone-neutral">${escapeHtml(file.file_type || t('runtime.tables.unknownType'))}</span></td>
                                <td data-label="${escapeHtml(t('runtime.tables.fileSizeLabel'))}">${escapeHtml(i18n.formatFileSize(file.size_bytes))}</td>
                                <td data-label="${escapeHtml(t('runtime.tables.uploadedAtLabel'))}">${formatDateTime(file.uploaded_at)}</td>
                                ${['admin', 'superadmin'].includes(APP_CONTEXT.userRole)
                                    ? `<td data-label="${escapeHtml(t('runtime.tables.actionsLabel'))}"><button class="button button--danger button--compact" type="button" data-delete-file data-tenant="${escapeHtml(tenant)}" data-filename="${escapeHtml(file.filename)}">${escapeHtml(t('runtime.tables.deleteFile'))}</button></td>`
                                    : ''}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
}

async function loadUploadedFiles() {
    const tenant = currentTenant();
    appState.uploadedFilesTenant = tenant;
    appState.uploadedFilesError = '';
    appState.uploadedFiles = [];

    if (!tenant) {
        renderUploadedFiles();
        return;
    }

    try {
        const response = await authFetch(`/api/upload/${tenant}/files`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        appState.uploadedFiles = data.files || [];
    } catch (error) {
        appState.uploadedFilesError = error.message;
    }

    renderUploadedFiles();
}

async function deleteFile(tenant, filename) {
    const decodedTenant = tenant;
    const decodedFilename = filename;
    const confirmed = await requestConfirmation({
        titleKey: 'runtime.files.deleteTitle',
        detailKey: 'runtime.files.deleteDetail',
        confirmLabelKey: 'runtime.files.deleteConfirm',
        params: {
            filename: decodedFilename,
            tenant: decodedTenant,
        },
    });
    if (!confirmed) return;
    try {
        const response = await authFetch(`/api/upload/${encodeURIComponent(decodedTenant)}/files/${encodeURIComponent(decodedFilename)}`, { method: 'DELETE' });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || t('runtime.files.deleteTitle'));
        await loadUploadedFiles();
        showShellAlert('', 'success', 4000, 'runtime.files.deleteSuccess', { filename: decodedFilename });
    } catch (error) {
        showShellAlert(error.message);
    }
}

function tenantOptionsMarkup(tenants, includeSystemWide = true) {
    const options = [];
    if (includeSystemWide) {
        options.push(`<option value="">${escapeHtml(t('common.systemWide'))}</option>`);
    }
    tenants.forEach((tenant) => {
        options.push(`<option value="${tenant.tenant_id}">${tenant.tenant_id} — ${escapeHtml(tenant.tenant_name)}</option>`);
    });
    return options.join('');
}

async function populateTenantDropdown() {
    const select = byId('adminNewUserTenant');
    if (!select) return;
    try {
        const tenants = await fetchTenants();
        const selectedValue = select.value || '';
        select.innerHTML = tenantOptionsMarkup(tenants);
        select.value = selectedValue;
    } catch (error) {}
}

function autoFillTenantPath() {
    const tenantId = byId('newTenantId').value.trim().replace(/[^a-zA-Z0-9_]/g, '_');
    byId('newTenantFilePath').value = tenantId ? `./data/${tenantId}/` : '';
}

async function createTenant(event) {
    event.preventDefault();
    const message = byId('tenantCreateMsg');
    const tenantId = byId('newTenantId').value.trim().replace(/[^a-zA-Z0-9_]/g, '_');
    const tenantName = byId('newTenantName').value.trim();
    const filePath = byId('newTenantFilePath').value;
    const expiresAt = byId('newTenantExpiresAt').value;

    if (!tenantId) {
        setFormMessage(message, 'is-error', 'runtime.forms.invalidTenantId');
        return;
    }

    setFormMessage(message, 'is-running', 'runtime.forms.creatingTenant');

    const body = { tenant_id: tenantId, tenant_name: tenantName, file_path: filePath };
    if (expiresAt) body.expires_at = expiresAt;

    try {
        const response = await authFetch('/api/tenants', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || t('runtime.forms.saveTenantError'));

        setFormMessage(message, 'is-success', 'runtime.forms.tenantCreated', { tenant: tenantId });
        ['newTenantId', 'newTenantName', 'newTenantFilePath', 'newTenantExpiresAt'].forEach((id) => {
            byId(id).value = '';
        });
        await loadAdminData({ force: true });
    } catch (error) {
        setFormMessage(message, 'is-error', '', {}, error.message);
    }
}

async function createUser(event) {
    event.preventDefault();
    const message = byId('adminUserCreateMsg');
    const username = byId('adminNewUserUsername').value.trim();
    const password = byId('adminNewUserPassword').value;
    const tenantId = byId('adminNewUserTenant').value || null;
    const role = byId('adminNewUserRole').value;

    if (role === 'viewer' && !tenantId) {
        setFormMessage(message, 'is-error', 'runtime.forms.viewerNeedsTenant');
        return;
    }

    setFormMessage(message, 'is-running', 'runtime.forms.creatingUser');

    try {
        const response = await authFetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, tenant_id: tenantId, role }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || t('runtime.forms.saveUserError'));

        setFormMessage(message, 'is-success', 'runtime.forms.userCreated', { username });
        byId('adminNewUserUsername').value = '';
        byId('adminNewUserPassword').value = '';
        byId('adminNewUserTenant').value = '';
        await loadAdminData({ force: true });
    } catch (error) {
        setFormMessage(message, 'is-error', '', {}, error.message);
    }
}

async function loadTenantUsers() {
    const container = byId('tenant-user-list');
    if (!container) return;
    try {
        const response = await authFetch('/api/users');
        if (!response.ok) throw new Error(t('runtime.forms.loadUsersError'));
        const data = await response.json();
        appState.tenantUsers = data.users || [];
        renderTenantUsers(appState.tenantUsers);
    } catch (error) {
        container.innerHTML = tableEmpty(error.message, 5);
    }
}

function renderTenantUsers(users) {
    const container = byId('tenant-user-list');
    if (!container) return;
    if (!users.length) {
        container.innerHTML = tableEmpty(t('runtime.tables.emptyTenantUsers'), 5);
        return;
    }
    container.innerHTML = users.map((user) => {
        return `
        <tr>
            <td data-label="${escapeHtml(t('runtime.tables.usernameLabel'))}"><strong>${escapeHtml(user.username)}</strong></td>
            <td data-label="${escapeHtml(t('runtime.tables.roleLabel'))}"><span class="status-pill tone-neutral">${escapeHtml(i18n.roleLabel(user.role === 'admin' ? 'admin' : 'viewer'))}</span></td>
            <td data-label="${escapeHtml(t('runtime.tables.statusLabel'))}"><span class="status-pill ${statusToneByBool(user.is_active)}">${user.is_active ? t('common.active') : t('common.inactive')}</span></td>
            <td data-label="${escapeHtml(t('runtime.tables.createdAtLabel'))}">${formatDateTime(user.created_at)}</td>
            <td data-label="${escapeHtml(t('runtime.tables.actionsLabel'))}"><button class="button button--secondary button--compact" type="button" data-edit-user data-user-id="${Number(user.user_id)}" data-username="${escapeHtml(user.username || '')}" data-tenant="${escapeHtml(APP_CONTEXT.userTenant || '')}" data-role="${escapeHtml(user.role || 'viewer')}" data-active="${Boolean(user.is_active)}">${escapeHtml(t('runtime.tables.editUser'))}</button></td>
        </tr>
    `;
    }).join('');
}

async function createTenantUser(event) {
    event.preventDefault();
    const message = byId('tenantUserCreateMsg');
    const username = byId('tenantNewUserUsername').value.trim();
    const password = byId('tenantNewUserPassword').value;

    setFormMessage(message, 'is-running', 'runtime.forms.creatingTenantUser');

    try {
        const response = await authFetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role: 'viewer' }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || t('runtime.forms.saveUserError'));

        setFormMessage(message, 'is-success', 'runtime.forms.userCreated', { username });
        byId('tenantNewUserUsername').value = '';
        byId('tenantNewUserPassword').value = '';
        await loadTenantUsers();
    } catch (error) {
        setFormMessage(message, 'is-error', '', {}, error.message);
    }
}

function renderEditTenantTitle() {
    if (byId('editTenantTitle')) {
        byId('editTenantTitle').textContent = appState.editingTenantId
            ? t('runtime.forms.editTenantTitle', { tenant: appState.editingTenantId })
            : t('modals.editTenant.title');
    }
}

function renderEditUserTitle() {
    if (byId('editUserTitle')) {
        byId('editUserTitle').textContent = appState.editingUserName
            ? t('runtime.forms.editUserTitle', { username: appState.editingUserName })
            : t('modals.editUser.title');
    }
}

function renderViewUserModal() {
    const container = byId('viewUserDetails');
    const title = byId('viewUserTitle');
    if (!container || !title) return;

    title.textContent = appState.viewingUserName
        ? `${t('modals.viewUser.title')} · ${appState.viewingUserName}`
        : t('modals.viewUser.title');

    if (appState.viewingUserError) {
        container.innerHTML = `
            <div class="empty-state">
                <strong>${escapeHtml(appState.viewingUserError)}</strong>
            </div>
        `;
        return;
    }

    if (!appState.viewingUser) {
        container.innerHTML = `
            <div class="detail-row">
                <span class="detail-label">${escapeHtml(t('modals.viewUser.loading'))}</span>
            </div>
        `;
        return;
    }

    const user = appState.viewingUser;
    const detailRows = [
        ['modals.viewUser.usernameLabel', user.username],
        ['modals.viewUser.displayNameLabel', user.display_name || t('common.notAvailable')],
        ['modals.viewUser.emailLabel', user.email || t('common.notAvailable')],
        ['modals.viewUser.phoneLabel', user.phone || t('common.notAvailable')],
        ['modals.viewUser.tenantLabel', user.tenant_id || t('common.systemWide')],
        ['modals.viewUser.roleLabel', i18n.roleLabel(user.role === 'superadmin' ? 'superadmin' : user.role === 'admin' ? 'admin' : 'viewer')],
        ['modals.viewUser.statusLabel', user.is_active ? t('common.active') : t('common.inactive')],
        ['modals.viewUser.createdAtLabel', user.created_at ? formatDateTime(user.created_at) : t('common.notAvailable')],
    ];

    container.innerHTML = detailRows.map(([labelKey, value]) => `
        <div class="detail-row">
            <span class="detail-label">${escapeHtml(t(labelKey))}</span>
            <strong class="detail-value">${escapeHtml(value)}</strong>
        </div>
    `).join('');
}

function openEditTenant(tenantId) {
    const tenant = appState.tenants.find((item) => item.tenant_id === tenantId);
    if (!tenant) return;

    appState.editingTenantId = tenantId;
    byId('editTenantId').value = tenant.tenant_id;
    byId('editTenantName').value = tenant.tenant_name;
    byId('editTenantFilePath').value = tenant.file_path || '';
    byId('editTenantActive').value = tenant.is_active ? '1' : '0';
    byId('editTenantExpiresAt').value = tenant.expires_at
        ? new Date(new Date(tenant.expires_at).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16)
        : '';
    renderEditTenantTitle();
    clearFormMessage(byId('editTenantMsg'));
    toggleModal('modalEditTenant', true);
}

function closeEditTenantModal() {
    appState.editingTenantId = '';
    toggleModal('modalEditTenant', false);
}

async function submitEditTenant(event) {
    event.preventDefault();
    const message = byId('editTenantMsg');
    const tenantId = byId('editTenantId').value;

    setFormMessage(message, 'is-running', 'runtime.forms.savingChanges');

    const body = {
        tenant_name: byId('editTenantName').value.trim(),
        file_path: byId('editTenantFilePath').value.trim() || null,
        is_active: byId('editTenantActive').value === '1',
        expires_at: byId('editTenantExpiresAt').value || '',
    };

    try {
        const response = await authFetch(`/api/tenants/${tenantId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || t('runtime.forms.saveTenantUpdateError'));

        setFormMessage(message, 'is-success', 'runtime.forms.tenantSaved');
        await loadAdminData({ force: true });
        window.setTimeout(closeEditTenantModal, 700);
    } catch (error) {
        setFormMessage(message, 'is-error', '', {}, error.message);
    }
}

async function openEditUser(userId, username, tenantId, role, isActive) {
    appState.editingUserName = username;
    byId('editUserId').value = userId;
    byId('editUserUsername').value = username;
    byId('editUserPassword').value = '';
    byId('editUserRole').value = role;
    byId('editUserActive').value = isActive ? '1' : '0';
    renderEditUserTitle();
    clearFormMessage(byId('editUserMsg'));

    const select = byId('editUserTenant');
    select.innerHTML = tenantOptionsMarkup(appState.tenants);
    try {
        await fetchTenants();
        select.innerHTML = tenantOptionsMarkup(appState.tenants);
    } catch (error) {}
    select.value = tenantId || '';
    toggleModal('modalEditUser', true);
}

function closeEditUserModal() {
    appState.editingUserName = '';
    toggleModal('modalEditUser', false);
}

async function openViewUser(userId, username) {
    appState.viewingUserName = username || '';
    appState.viewingUser = null;
    appState.viewingUserError = '';
    renderViewUserModal();
    toggleModal('modalViewUser', true);

    try {
        appState.viewingUser = await fetchUserDetail(userId);
    } catch (error) {
        appState.viewingUserError = error.message || t('runtime.forms.loadUserDetailError');
    }

    renderViewUserModal();
}

function closeViewUserModal() {
    appState.viewingUser = null;
    appState.viewingUserName = '';
    appState.viewingUserError = '';
    toggleModal('modalViewUser', false);
}

async function submitEditUser(event) {
    event.preventDefault();
    const message = byId('editUserMsg');
    const userId = byId('editUserId').value;

    const body = {
        tenant_id: byId('editUserTenant').value || null,
        role: byId('editUserRole').value,
        is_active: byId('editUserActive').value === '1',
    };
    if (byId('editUserPassword').value) {
        body.password = byId('editUserPassword').value;
    }

    setFormMessage(message, 'is-running', 'runtime.forms.savingChanges');

    try {
        const response = await authFetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || t('runtime.forms.saveUserUpdateError'));

        setFormMessage(message, 'is-success', 'runtime.forms.userSaved');
        if (APP_CONTEXT.userRole === 'superadmin') {
            await loadAdminData({ force: true });
        } else if (APP_CONTEXT.userRole === 'admin') {
            await loadTenantUsers();
        }
        window.setTimeout(closeEditUserModal, 700);
    } catch (error) {
        setFormMessage(message, 'is-error', '', {}, error.message);
    }
}

function bindGlobalEvents() {
    byId('toggleSidebar')?.addEventListener('click', toggleSidebar);
    byId('shellScrim')?.addEventListener('click', closeSidebarOnMobile);
    byId('logoutBtn')?.addEventListener('click', async () => {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    });

    byId('modalOverlay')?.addEventListener('click', (event) => {
        if (event.target.id === 'modalOverlay') closeModal();
    });
    byId('modalEditTenant')?.addEventListener('click', (event) => {
        if (event.target.id === 'modalEditTenant') closeEditTenantModal();
    });
    byId('modalEditUser')?.addEventListener('click', (event) => {
        if (event.target.id === 'modalEditUser') closeEditUserModal();
    });
    byId('modalViewUser')?.addEventListener('click', (event) => {
        if (event.target.id === 'modalViewUser') closeViewUserModal();
    });
    byId('modalConfirm')?.addEventListener('click', (event) => {
        if (event.target.id === 'modalConfirm') closeConfirmModal();
    });
    byId('confirmCancelBtn')?.addEventListener('click', () => closeConfirmModal(false));
    byId('confirmActionBtn')?.addEventListener('click', () => closeConfirmModal(true));

    document.addEventListener('click', (event) => {
        const runEtlButton = event.target.closest('[data-run-etl-current]');
        if (runEtlButton) {
            triggerETL(currentTenant());
            return;
        }

        const closeButton = event.target.closest('[data-close-modal]');
        if (closeButton) {
            const modal = closeButton.dataset.closeModal;
            if (modal === 'edit-tenant') closeEditTenantModal();
            if (modal === 'edit-user') closeEditUserModal();
            if (modal === 'view-user') closeViewUserModal();
            if (modal === 'dashboard') closeModal();
            if (modal === 'confirm') closeConfirmModal();
            return;
        }

        const editTenantButton = event.target.closest('[data-edit-tenant]');
        if (editTenantButton) {
            openEditTenant(editTenantButton.dataset.editTenant || '');
            return;
        }

        const editUserButton = event.target.closest('[data-edit-user]');
        if (editUserButton) {
            openEditUser(
                Number(editUserButton.dataset.userId),
                editUserButton.dataset.username || '',
                editUserButton.dataset.tenant || '',
                editUserButton.dataset.role || 'viewer',
                editUserButton.dataset.active === 'true'
            );
            return;
        }

        const viewUserButton = event.target.closest('[data-view-user]');
        if (viewUserButton) {
            openViewUser(
                Number(viewUserButton.dataset.userId),
                viewUserButton.dataset.username || ''
            );
            return;
        }

        const deleteFileButton = event.target.closest('[data-delete-file]');
        if (deleteFileButton) {
            deleteFile(deleteFileButton.dataset.tenant || '', deleteFileButton.dataset.filename || '');
        }
    });

    byId('fileInput')?.addEventListener('change', showFilePreview);
    byId('etlTenantSelect')?.addEventListener('change', loadUploadedFiles);
    byId('tenantSearchInput')?.addEventListener('input', (event) => {
        appState.tenantSearchTerm = event.target.value || '';
        renderTenants(appState.tenants);
    });
    byId('userSearchInput')?.addEventListener('input', (event) => {
        appState.userSearchTerm = event.target.value || '';
        renderUsers(appState.users);
    });
    byId('analysisTenantSelect')?.addEventListener('change', async (event) => {
        appState.analysisTenantId = event.target.value || '';
        window.sessionStorage.setItem('dashboardAnalysisTenant', appState.analysisTenantId);
        renderAnalysisScope();

        if (appState.activePage === 'analysis') {
            await loadSupersetIframe(appState.activeAnalysis, {
                iframeId: 'iframe-analysis',
                frameStateId: 'frameState-analysis',
            });
        }
    });

    const uploadZone = byId('uploadZone');
    if (uploadZone) {
        uploadZone.addEventListener('dragover', (event) => {
            event.preventDefault();
            uploadZone.classList.add('is-dragging');
        });
        uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('is-dragging'));
        uploadZone.addEventListener('drop', (event) => {
            event.preventDefault();
            uploadZone.classList.remove('is-dragging');
            if (event.dataTransfer.files.length) {
                byId('fileInput').files = event.dataTransfer.files;
                showFilePreview();
            }
        });
    }

    window.addEventListener('resize', setSidebarState);
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeSidebarOnMobile();
        }
    });
}

function bindForms() {
    byId('formCreateTenant')?.addEventListener('submit', createTenant);
    byId('formCreateAdminUser')?.addEventListener('submit', createUser);
    byId('formCreateTenantUser')?.addEventListener('submit', createTenantUser);
    byId('formEditTenant')?.addEventListener('submit', submitEditTenant);
    byId('formEditUser')?.addEventListener('submit', submitEditUser);
    byId('newTenantId')?.addEventListener('input', autoFillTenantPath);
}

function renderLocaleState() {
    renderShellContext();
    renderAnalysisScope();
    updatePageChrome(appState.activePage || APP_CONTEXT.defaultPage);
    setActiveAnalysis(appState.activeAnalysis);
    renderHealthState();
    renderOverviewIntel();
    renderTenants(appState.tenants);
    renderUsers(appState.users);
    renderETLLogs(appState.etlLogs);
    renderTenantUsers(appState.tenantUsers);
    renderUploadedFiles();
    renderUploadStatus();
    renderEditTenantTitle();
    renderEditUserTitle();
    renderViewUserModal();
    renderConfirmDialog();
    populateTenantDropdown();

    const editUserTenant = byId('editUserTenant');
    if (editUserTenant && appState.tenants.length) {
        const selectedValue = editUserTenant.value || '';
        editUserTenant.innerHTML = tenantOptionsMarkup(appState.tenants);
        editUserTenant.value = selectedValue;
    }

    if (byId('fileInput')?.files?.length) {
        showFilePreview();
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    bindNavigation();
    bindGlobalEvents();
    bindForms();
    setSidebarState();
    renderShellContext();
    renderHealthState();
    renderOverviewIntel();
    i18n.onChange(renderLocaleState);
    checkHealth();
    loadKPIs();
    populateETLTenantSelect();
    loadUploadedFiles();

    const requestedPage = sessionStorage.getItem('dashboardPage');
    if (requestedPage) {
        sessionStorage.removeItem('dashboardPage');
    }
    const hasInitialRoute = requestedPage ? navigateTo(requestedPage) : false;
    if (!hasInitialRoute) {
        navigateTo(APP_CONTEXT.defaultPage);
    }

    if (APP_CONTEXT.userRole === 'superadmin') {
        await loadAdminData();
    }
    if (APP_CONTEXT.userRole === 'admin') {
        await loadTenantUsers();
    }

    renderLocaleState();
});

window.openEditTenant = openEditTenant;
window.openEditUser = openEditUser;
window.closeViewUserModal = closeViewUserModal;
window.closeModal = closeModal;
window.closeConfirmModal = closeConfirmModal;
window.closeEditTenantModal = closeEditTenantModal;
window.closeEditUserModal = closeEditUserModal;
window.deleteFile = deleteFile;
window.triggerETL = triggerETL;
window.currentTenant = currentTenant;
