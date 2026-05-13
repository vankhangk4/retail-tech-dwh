// ============================================================
// settings.js — Trang Cài đặt & Hồ sơ người dùng
// ============================================================

(function () {
    'use strict';

    const APP_CONTEXT = {
        userRole: document.body.dataset.userRole || 'viewer',
        userTenant: document.body.dataset.userTenant || '',
    };

    const LANGUAGE_STORAGE_KEY = 'dwh_ui_lang';
    const LEGACY_LANGUAGE_STORAGE_KEYS = ['dwh_settings_ui_lang'];
    const SUPPORTED_LANGUAGES = new Set(['vi', 'en']);

    const COPY = {
        vi: {
            language: {
                vietnamese: 'Tiếng Việt',
                english: 'English',
            },
            common: {
                notAvailable: 'Chưa xác định',
                processing: 'Đang xử lý',
            },
            roles: {
                superadmin: 'Quản trị hệ thống',
                admin: 'Quản trị chi nhánh',
                viewer: 'Người xem báo cáo',
            },
            page: {
                browserTitle: 'Thiết lập tài khoản | DWH Operations Console',
                skipLink: 'Bỏ qua điều hướng, chuyển tới nội dung chính',
                closeNavigation: 'Đóng thanh điều hướng',
                toggleNavigation: 'Thu gọn hoặc mở thanh điều hướng',
                eyebrow: 'Người dùng',
                title: 'Thiết lập tài khoản',
                description: 'Quản trị hồ sơ người dùng, thông tin liên hệ và bảo mật truy cập của tài khoản đang đăng nhập.',
                usernameChip: 'Tên đăng nhập',
                roleChip: 'Vai trò',
                languageLabel: 'Ngôn ngữ',
                languageSelectAria: 'Chọn ngôn ngữ giao diện',
                tabsAria: 'Nhóm chức năng thiết lập',
            },
            tabs: {
                profile: 'Hồ sơ tài khoản',
                security: 'Bảo mật truy cập',
                drive: 'Kết nối Google Drive',
            },
            profile: {
                avatarTitle: 'Ảnh đại diện',
                avatarDesc: 'Cập nhật ảnh nhận diện dùng tại thanh điều hướng và các màn hình tài khoản. Hỗ trợ JPG, PNG, WEBP, dung lượng đầu vào tối đa 8 MB.',
                avatarPreviewAria: 'Ảnh đại diện hiện hành',
                avatarAlt: 'Ảnh đại diện người dùng',
                avatarUploadTitle: 'Cập nhật ảnh đại diện',
                avatarInputAria: 'Chọn tệp ảnh đại diện',
                avatarHint: 'Hệ thống tự động chuẩn hóa ảnh về kích thước tối đa 200×200 px trước khi lưu.',
                avatarRemove: 'Xóa ảnh hiện hành',
                avatarUpdated: 'Đã cập nhật ảnh đại diện.',
                avatarRemoved: 'Đã xóa ảnh đại diện.',
                infoTitle: 'Thông tin tài khoản',
                infoDesc: 'Cập nhật tên hiển thị và đầu mối liên hệ phục vụ trao đổi vận hành.',
                usernameLabel: 'Tên đăng nhập',
                roleLabel: 'Vai trò',
                tenantLabel: 'Chi nhánh',
                createdAtLabel: 'Ngày tạo tài khoản',
                displayNameLabel: 'Tên hiển thị',
                displayNamePlaceholder: 'Nhập họ tên hoặc tên đầu mối phụ trách',
                displayNameHint: 'Hiển thị tại thanh điều hướng và các màn hình báo cáo.',
                emailLabel: 'Email',
                emailPlaceholder: 'ten.nguoi.dung@congty.vn',
                phoneLabel: 'Số điện thoại liên hệ',
                phonePlaceholder: 'Ví dụ: 0900 000 000',
                save: 'Lưu cập nhật',
                reset: 'Khôi phục',
                loadError: 'Không thể tải thông tin tài khoản. Vui lòng tải lại màn hình.',
                updateSuccess: 'Đã lưu cập nhật thông tin tài khoản.',
                updateError: 'Không thể cập nhật thông tin tài khoản.',
                avatarUploadError: 'Không thể tải ảnh đại diện.',
                avatarDeleteError: 'Không thể xóa ảnh đại diện.',
                avatarFileTooLarge: 'Tệp ảnh vượt dung lượng cho phép, tối đa 8 MB trước khi chuẩn hóa.',
                avatarReadError: 'Không thể đọc tệp ảnh.',
                fileReadError: 'Không thể đọc tệp đã chọn.',
            },
            security: {
                title: 'Cập nhật mật khẩu',
                desc: 'Thiết lập mật khẩu mới cho tài khoản đăng nhập. Mật khẩu nên có tối thiểu 6 ký tự và bao gồm nhiều nhóm ký tự.',
                currentPasswordLabel: 'Mật khẩu hiện hành',
                currentPasswordPlaceholder: 'Nhập mật khẩu hiện hành',
                newPasswordLabel: 'Mật khẩu mới',
                newPasswordPlaceholder: 'Tối thiểu 6 ký tự',
                confirmPasswordLabel: 'Xác nhận mật khẩu mới',
                confirmPasswordPlaceholder: 'Nhập lại để xác nhận',
                togglePasswordAria: 'Hiển thị hoặc ẩn mật khẩu',
                save: 'Lưu mật khẩu mới',
                confirmMismatch: 'Mật khẩu xác nhận không trùng khớp.',
                minLengthError: 'Mật khẩu mới phải có tối thiểu 6 ký tự.',
                updateSuccess: 'Đã cập nhật mật khẩu. Vui lòng đăng nhập lại nếu hệ thống yêu cầu.',
                updateError: 'Không thể cập nhật mật khẩu.',
                strength: {
                    weak: 'Yếu',
                    medium: 'Trung bình',
                    fair: 'Khá',
                    strong: 'Mạnh',
                },
            },
            history: {
                title: 'Nhật ký đăng nhập',
                desc: 'Theo dõi 20 phiên gần nhất để đối soát hoạt động truy cập tài khoản.',
                refresh: 'Làm mới',
                time: 'Thời điểm',
                ip: 'IP truy cập',
                device: 'Thiết bị / Trình duyệt',
                result: 'Kết quả',
                loading: 'Đang tải nhật ký đăng nhập...',
                emptyTitle: 'Chưa phát sinh dữ liệu',
                emptyDesc: 'Hệ thống chưa ghi nhận phiên đăng nhập trong phạm vi theo dõi.',
                error: 'Không thể tải nhật ký đăng nhập.',
                success: 'Thành công',
                failure: 'Không thành công',
                currentSession: 'Phiên hiện tại',
                unknownClient: 'Chưa xác định',
            },
            drive: {
                title: 'Kết nối Google Drive',
                desc: 'Liên kết thư mục Google Drive chứa file Excel nguồn để chuẩn bị nạp dữ liệu và chạy ETL theo lịch vận hành.',
                statusDisconnected: 'Chưa kết nối',
                statusConnected: 'Đã kết nối',
                statusNotReady: 'Chưa cấu hình',
                providerTitle: 'Google Drive Workspace',
                providerDesc: 'Dùng OAuth để cấp quyền đọc thư mục nguồn, không lưu mật khẩu Google trong hệ thống.',
                connect: 'Kết nối Google Drive',
                disconnect: 'Ngắt kết nối',
                syncRun: 'Đồng bộ và chạy ETL',
                chooseSource: 'Chọn file nguồn',
                sourceLocal: 'Chọn từ máy tính',
                sourceLocalDesc: 'Chọn file Excel hoặc CSV từ thiết bị và nạp vào staging.',
                sourceDrive: 'Chọn từ Google Drive',
                sourceDriveDesc: 'Lấy file Excel hoặc Google Sheets từ tài khoản Drive đã kết nối.',
                filePickerTitle: 'File nguồn',
                filePickerDesc: 'Chọn đúng file nguồn cần nạp vào staging cho kỳ ETL hiện tại.',
                systemPickerDesc: 'Chọn file Excel hoặc CSV từ máy tính để nạp vào staging của chi nhánh hiện tại.',
                drivePickerDesc: 'Chọn file Excel hoặc Google Sheets từ Google Drive để đồng bộ vào staging.',
                searchPlaceholder: 'Tìm theo tên file',
                refreshFiles: 'Chọn file từ máy tính',
                loadingFiles: 'Đang tải danh sách file nguồn...',
                fileListConnectHint: 'Chọn nguồn dữ liệu để tải danh sách file.',
                fileListEmpty: 'Chưa có file nào được chọn.',
                fileListError: 'Không thể tải danh sách file nguồn.',
                noFileSelected: 'Chưa chọn file',
                selectedCount: 'Đã chọn {count} file',
                sheetType: 'Google Sheets',
                fileType: 'File Excel',
                systemFileType: 'File máy tính',
                localUploadSuccess: 'Đã nạp file từ máy tính vào staging.',
                folderLabel: 'ID thư mục nguồn',
                folderPlaceholder: 'Ví dụ: 1AbC...',
                folderHint: 'Thư mục chứa file Excel theo từng chi nhánh hoặc kỳ dữ liệu.',
                scopeLabel: 'Phạm vi đồng bộ',
                scopeCurrent: 'Chi nhánh hiện tại',
                scopeAll: 'Toàn hệ thống',
                patternLabel: 'Quy ước file Excel',
                patternPlaceholder: 'BaoCaoDoanhThu_*.xlsx',
                scheduleLabel: 'Giờ chạy ETL cuối ngày',
                policyEyebrow: 'Quy trình đề xuất',
                policyUpload: 'Google Drive nhận file Excel trong ngày.',
                policySync: 'Hệ thống đồng bộ file nguồn vào staging theo chi nhánh.',
                policyEtl: 'ETL tự động chạy cuối ngày và ghi log để đối soát.',
                save: 'Lưu cấu hình kết nối',
                oauthUnavailable: 'Chưa cấu hình Google Drive OAuth. Cần khai báo Client ID, Client Secret và callback URL trước khi kết nối.',
                configSaved: 'Đã lưu cấu hình Google Drive.',
                configLoadError: 'Không thể tải trạng thái kết nối Google Drive.',
                connectError: 'Không thể khởi tạo phiên kết nối Google Drive.',
                disconnectSuccess: 'Đã ngắt kết nối Google Drive.',
                disconnectError: 'Không thể ngắt kết nối Google Drive.',
                syncSuccess: 'Đã đồng bộ file nguồn và kích hoạt ETL.',
                syncError: 'Không thể đồng bộ dữ liệu từ Google Drive.',
                folderRequired: 'Vui lòng chọn tối thiểu một file nguồn trước khi đồng bộ.',
            },
            sidebar: {
                brandMeta: 'Trung tâm vận hành cho hệ thống Data Warehouse đa chi nhánh',
                scopePrefix: 'Phạm vi dữ liệu',
                scopeAll: 'Toàn hệ thống',
                scopeBranchMode: 'Phạm vi chi nhánh',
                groupOperations: 'Vận hành',
                groupAnalytics: 'Phân tích',
                groupAdmin: 'Quản trị',
                groupAccount: 'Tài khoản',
                primaryNavAria: 'Điều hướng chính',
                overviewTitle: 'Tổng quan',
                overviewMeta: 'Chỉ báo vận hành',
                etlTitle: 'Vận hành ETL',
                etlMeta: 'Nạp dữ liệu và ETL',
                analysisTitle: 'Phân tích',
                analysisMeta: 'Truy cập 5 báo cáo phân tích',
                manageTitle: 'Quản lý chi nhánh',
                manageMeta: 'Người dùng theo chi nhánh',
                adminTitle: 'Quản trị hệ thống',
                adminMeta: 'Chi nhánh, người dùng, giám sát ETL',
                settingsTitle: 'Thiết lập',
                settingsMeta: 'Thông tin và bảo mật',
                healthLoading: 'Đang kiểm tra kết nối API',
                healthHealthy: 'Kết nối API ổn định',
                healthCheck: 'Cần kiểm tra kết nối API',
                signOut: 'Đăng xuất',
            },
        },
        en: {
            language: {
                vietnamese: 'Vietnamese',
                english: 'English',
            },
            common: {
                notAvailable: 'Not available',
                processing: 'Processing',
            },
            roles: {
                superadmin: 'System Administrator',
                admin: 'Branch Administrator',
                viewer: 'Report Viewer',
            },
            page: {
                browserTitle: 'Account Settings | DWH Operations Console',
                skipLink: 'Skip navigation and go to main content',
                closeNavigation: 'Close navigation panel',
                toggleNavigation: 'Collapse or open navigation panel',
                eyebrow: 'User',
                title: 'Account Settings',
                description: 'Manage the active account profile, contact information, and access security.',
                usernameChip: 'Username',
                roleChip: 'Role',
                languageLabel: 'Language',
                languageSelectAria: 'Choose interface language',
                tabsAria: 'Settings function groups',
            },
            tabs: {
                profile: 'Account Profile',
                security: 'Access Security',
                drive: 'Google Drive Connection',
            },
            profile: {
                avatarTitle: 'Avatar',
                avatarDesc: 'Update the identity image used in navigation and account views. Supports JPG, PNG, and WEBP. Maximum upload size is 8 MB.',
                avatarPreviewAria: 'Current avatar',
                avatarAlt: 'User avatar',
                avatarUploadTitle: 'Update avatar',
                avatarInputAria: 'Select avatar image file',
                avatarHint: 'The system standardizes the image to a maximum size of 200×200 px before saving.',
                avatarRemove: 'Remove current avatar',
                avatarUpdated: 'Avatar updated.',
                avatarRemoved: 'Avatar removed.',
                infoTitle: 'Account Information',
                infoDesc: 'Update the display name and contact details used for operational coordination.',
                usernameLabel: 'Username',
                roleLabel: 'Role',
                tenantLabel: 'Branch',
                createdAtLabel: 'Account Created On',
                displayNameLabel: 'Display Name',
                displayNamePlaceholder: 'Enter the full name or operational contact name',
                displayNameHint: 'Displayed in navigation and reporting screens.',
                emailLabel: 'Email',
                emailPlaceholder: 'user.name@company.com',
                phoneLabel: 'Contact Phone Number',
                phonePlaceholder: 'Example: +84 900 000 000',
                save: 'Save Changes',
                reset: 'Restore Values',
                loadError: 'Unable to load account information. Please reload the screen.',
                updateSuccess: 'Account information updated.',
                updateError: 'Unable to update account information.',
                avatarUploadError: 'Unable to upload the avatar.',
                avatarDeleteError: 'Unable to remove the avatar.',
                avatarFileTooLarge: 'The image file exceeds the allowed size. Maximum input size is 8 MB before standardization.',
                avatarReadError: 'Unable to read the image file.',
                fileReadError: 'Unable to read the selected file.',
            },
            security: {
                title: 'Update Password',
                desc: 'Set a new password for the sign-in account. Use at least 6 characters and combine multiple character groups where possible.',
                currentPasswordLabel: 'Current Password',
                currentPasswordPlaceholder: 'Enter the current password',
                newPasswordLabel: 'New Password',
                newPasswordPlaceholder: 'Minimum 6 characters',
                confirmPasswordLabel: 'Confirm New Password',
                confirmPasswordPlaceholder: 'Enter again to confirm',
                togglePasswordAria: 'Show or hide password',
                save: 'Save New Password',
                confirmMismatch: 'The confirmation password does not match.',
                minLengthError: 'The new password must contain at least 6 characters.',
                updateSuccess: 'Password updated. Sign in again if the system requests it.',
                updateError: 'Unable to update the password.',
                strength: {
                    weak: 'Weak',
                    medium: 'Moderate',
                    fair: 'Good',
                    strong: 'Strong',
                },
            },
            history: {
                title: 'Sign-in Log',
                desc: 'Review the latest 20 sessions to reconcile account access activity.',
                refresh: 'Refresh',
                time: 'Timestamp',
                ip: 'IP Address',
                device: 'Device / Browser',
                result: 'Result',
                loading: 'Loading the sign-in log...',
                emptyTitle: 'No records available',
                emptyDesc: 'No sign-in sessions have been recorded in the monitored window.',
                error: 'Unable to load the sign-in log.',
                success: 'Successful',
                failure: 'Unsuccessful',
                currentSession: 'Current Session',
                unknownClient: 'Not identified',
            },
            drive: {
                title: 'Google Drive Connection',
                desc: 'Link the Google Drive folder that stores source Excel files for data loading and scheduled ETL operations.',
                statusDisconnected: 'Not Connected',
                statusConnected: 'Connected',
                statusNotReady: 'Not Configured',
                providerTitle: 'Google Drive Workspace',
                providerDesc: 'Use OAuth to grant read access to the source folder. Google passwords are not stored in the system.',
                connect: 'Connect Google Drive',
                disconnect: 'Disconnect',
                syncRun: 'Sync and Run ETL',
                chooseSource: 'Choose Source Files',
                sourceLocal: 'Choose from Computer',
                sourceLocalDesc: 'Select Excel or CSV files from this device and load them into staging.',
                sourceDrive: 'Choose from Google Drive',
                sourceDriveDesc: 'Load Excel files or Google Sheets from the connected Drive account.',
                filePickerTitle: 'Source Files',
                filePickerDesc: 'Select the source files to load into staging for the current ETL run.',
                systemPickerDesc: 'Select Excel or CSV files from this computer to load into the current branch staging folder.',
                drivePickerDesc: 'Select Excel files or Google Sheets from Google Drive to sync into staging.',
                searchPlaceholder: 'Search by file name',
                refreshFiles: 'Choose Files from Computer',
                loadingFiles: 'Loading source files...',
                fileListConnectHint: 'Choose a data source to load source files.',
                fileListEmpty: 'No files selected yet.',
                fileListError: 'Unable to load source files.',
                noFileSelected: 'No file selected',
                selectedCount: '{count} files selected',
                sheetType: 'Google Sheets',
                fileType: 'Excel File',
                systemFileType: 'Computer File',
                localUploadSuccess: 'Files from computer loaded into staging.',
                folderLabel: 'Source Folder ID',
                folderPlaceholder: 'Example: 1AbC...',
                folderHint: 'Folder containing Excel files by branch or data period.',
                scopeLabel: 'Sync Scope',
                scopeCurrent: 'Current Branch',
                scopeAll: 'System-wide',
                patternLabel: 'Excel File Pattern',
                patternPlaceholder: 'RevenueReport_*.xlsx',
                scheduleLabel: 'End-of-day ETL Time',
                policyEyebrow: 'Recommended Workflow',
                policyUpload: 'Google Drive receives the daily Excel files.',
                policySync: 'The system syncs source files into branch-level staging.',
                policyEtl: 'ETL runs automatically at the end of day and records logs for reconciliation.',
                save: 'Save Connection Settings',
                oauthUnavailable: 'Google Drive OAuth is not configured. Set Client ID, Client Secret, and callback URL before connecting.',
                configSaved: 'Google Drive settings saved.',
                configLoadError: 'Unable to load the Google Drive connection status.',
                connectError: 'Unable to start the Google Drive connection session.',
                disconnectSuccess: 'Google Drive disconnected.',
                disconnectError: 'Unable to disconnect Google Drive.',
                syncSuccess: 'Source files synced and ETL triggered.',
                syncError: 'Unable to sync data from Google Drive.',
                folderRequired: 'Select at least one source file before syncing.',
            },
            sidebar: {
                brandMeta: 'Operations hub for the multi-branch Data Warehouse platform',
                scopePrefix: 'Data scope',
                scopeAll: 'System-wide',
                scopeBranchMode: 'Branch scope',
                groupOperations: 'Operations',
                groupAnalytics: 'Analytics',
                groupAdmin: 'Administration',
                groupAccount: 'Account',
                primaryNavAria: 'Primary navigation',
                overviewTitle: 'Overview',
                overviewMeta: 'Operational signals',
                etlTitle: 'ETL Operations',
                etlMeta: 'Data upload and ETL',
                analysisTitle: 'Analytics',
                analysisMeta: 'Access 5 analytical reports',
                manageTitle: 'Branch Management',
                manageMeta: 'Users by branch',
                adminTitle: 'System Administration',
                adminMeta: 'Branches, users, and ETL monitoring',
                settingsTitle: 'Settings',
                settingsMeta: 'Profile and security',
                healthLoading: 'Checking API connection',
                healthHealthy: 'API connection is healthy',
                healthCheck: 'Check API connection',
                signOut: 'Sign out',
            },
        },
    };

    const strengthLabelKeys = ['', 'security.strength.weak', 'security.strength.medium', 'security.strength.fair', 'security.strength.strong'];

    let currentLanguage = 'vi';
    let profileCache = null;
    let healthState = 'loading';
    let loginHistoryCache = [];
    let loginHistoryState = 'idle';

    const logoutBtn = document.getElementById('logoutBtn');
    const languageSelect = document.getElementById('languageSelect');

    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/logout', { method: 'POST' });
            } finally {
                window.location.href = '/login';
            }
        });
    }

    function normalizeLanguage(value) {
        return SUPPORTED_LANGUAGES.has(value) ? value : 'vi';
    }

    function loadSavedLanguage() {
        try {
            const saved = localStorage.getItem(LANGUAGE_STORAGE_KEY);
            if (saved) {
                return normalizeLanguage(saved);
            }

            for (const key of LEGACY_LANGUAGE_STORAGE_KEYS) {
                const legacyValue = localStorage.getItem(key);
                if (!legacyValue) continue;
                const normalizedLegacy = normalizeLanguage(legacyValue);
                localStorage.setItem(LANGUAGE_STORAGE_KEY, normalizedLegacy);
                return normalizedLegacy;
            }

            return 'vi';
        } catch (error) {
            return 'vi';
        }
    }

    function saveLanguage(value) {
        try {
            localStorage.setItem(LANGUAGE_STORAGE_KEY, value);
        } catch (error) {
            // Ignore storage failures and keep the current in-memory language.
        }
    }

    function resolveCopy(path) {
        return path.split('.').reduce((acc, part) => (acc && acc[part] !== undefined ? acc[part] : undefined), COPY[currentLanguage]);
    }

    function t(path) {
        return resolveCopy(path) ?? path;
    }

    function translateStaticCopy() {
        document.documentElement.lang = currentLanguage;
        document.body.dataset.uiLang = currentLanguage;
        document.title = t('page.browserTitle');

        document.querySelectorAll('[data-i18n]').forEach(el => {
            el.textContent = t(el.dataset.i18n);
        });

        document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
            el.placeholder = t(el.dataset.i18nPlaceholder);
        });

        document.querySelectorAll('[data-i18n-title]').forEach(el => {
            el.title = t(el.dataset.i18nTitle);
        });

        document.querySelectorAll('[data-i18n-aria-label]').forEach(el => {
            el.setAttribute('aria-label', t(el.dataset.i18nAriaLabel));
        });

        document.querySelectorAll('[data-i18n-alt]').forEach(el => {
            el.alt = t(el.dataset.i18nAlt);
        });

        if (languageSelect) languageSelect.value = currentLanguage;
    }

    function translateRole(role) {
        return t(`roles.${role}`);
    }

    function syncRoleLabels() {
        const roleLabel = translateRole(APP_CONTEXT.userRole);
        const headerRoleValue = document.getElementById('headerRoleValue');
        if (headerRoleValue) headerRoleValue.textContent = roleLabel;

        const identityRolePill = document.getElementById('identityRolePill');
        if (identityRolePill) identityRolePill.textContent = roleLabel;

        const sidebarRoleLabel = document.getElementById('sidebarRoleLabel');
        if (sidebarRoleLabel) sidebarRoleLabel.textContent = roleLabel;
    }

    function syncScopeLabels() {
        const sidebarScopeText = document.getElementById('sidebarScopeText');
        const sidebarScopeModeChip = document.getElementById('sidebarScopeModeChip');
        const tenant = APP_CONTEXT.userTenant;

        if (sidebarScopeText) {
            sidebarScopeText.textContent = tenant
                ? `${t('sidebar.scopePrefix')}: ${tenant}`
                : `${t('sidebar.scopePrefix')}: ${t('sidebar.scopeAll')}`;
        }

        if (sidebarScopeModeChip) {
            sidebarScopeModeChip.textContent = tenant ? t('sidebar.scopeBranchMode') : t('sidebar.scopeAll');
        }
    }

    function applyFallbackProfileValues() {
        const fallback = t('common.notAvailable');
        const headerUsername = document.getElementById('headerUsername');
        const identityUsername = document.getElementById('identityUsername');
        const identityCreatedAt = document.getElementById('identityCreatedAt');

        if (headerUsername) headerUsername.textContent = fallback;
        if (identityUsername) identityUsername.textContent = fallback;
        if (identityCreatedAt) identityCreatedAt.textContent = fallback;
    }

    function renderHealthIndicator() {
        const el = document.getElementById('healthIndicator');
        if (!el) return;

        if (healthState === 'loading') {
            el.innerHTML = `<span class="status-pill status-pill--plain tone-neutral">${escHtml(t('sidebar.healthLoading'))}</span>`;
            return;
        }

        const isHealthy = healthState === 'ok';
        const pillTone = isHealthy ? 'tone-success' : 'tone-danger';
        const dotTone = isHealthy ? 'is-live' : 'is-danger';
        const label = isHealthy ? t('sidebar.healthHealthy') : t('sidebar.healthCheck');

        el.innerHTML = `<span class="status-pill status-pill--plain ${pillTone}"><span class="health-dot ${dotTone}"></span>${escHtml(label)}</span>`;
    }

    function reapplyRuntimeTranslations() {
        document.querySelectorAll('[data-i18n-runtime]').forEach(el => {
            const key = el.dataset.i18nRuntime;
            if (key) el.textContent = t(key);
        });
    }

    function applyLanguage(lang) {
        currentLanguage = normalizeLanguage(lang);
        saveLanguage(currentLanguage);
        translateStaticCopy();
        syncRoleLabels();
        syncScopeLabels();
        renderHealthIndicator();
        if (profileCache) {
            populateProfile(profileCache);
        } else {
            applyFallbackProfileValues();
        }
        updatePasswordStrength();
        renderLoginHistory();
        if (typeof renderDriveFileList === 'function') {
            renderDriveFileList();
        }
        reapplyRuntimeTranslations();
    }

    function setRuntimeTranslation(el, translationKey) {
        if (!el) return;
        if (translationKey) {
            el.dataset.i18nRuntime = translationKey;
        } else {
            delete el.dataset.i18nRuntime;
        }
    }

    function showAlert(el, msg, type = 'danger', timeoutMs = 0, translationKey = '') {
        if (!el) return;
        window.clearTimeout(el._hideTimer);
        el.textContent = translationKey ? t(translationKey) : msg;
        el.className = `alert alert--${type}`;
        el.classList.remove('is-hidden');
        el.classList.add('is-visible');
        setRuntimeTranslation(el, translationKey);
        if (timeoutMs > 0) {
            el._hideTimer = window.setTimeout(() => {
                hideAlert(el);
            }, timeoutMs);
        }
    }

    function hideAlert(el) {
        if (!el) return;
        window.clearTimeout(el._hideTimer);
        el.classList.add('is-hidden');
        el.classList.remove('is-visible');
        el.textContent = '';
        setRuntimeTranslation(el, '');
    }

    function setFieldError(el, translationKey = '') {
        if (!el) return;
        el.textContent = translationKey ? t(translationKey) : '';
        setRuntimeTranslation(el, translationKey);
    }

    function setBtnLoading(btn, loading, labelKey) {
        if (!btn) return;
        btn.disabled = loading;
        const labelEl = btn.querySelector('.button__label');
        if (labelEl) labelEl.textContent = loading ? t('common.processing') : t(labelKey);
    }

    fetch('/api/health')
        .then(r => r.json())
        .then(data => {
            healthState = data.api === 'ok' ? 'ok' : 'error';
            renderHealthIndicator();
        })
        .catch(() => {
            healthState = 'error';
            renderHealthIndicator();
        });

    // ── Sidebar toggle ────────────────────────────────────────
    const toggleBtn = document.getElementById('toggleSidebar');
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
        const expanded = window.innerWidth > 1024 || document.body.classList.contains('sidebar-open');
        toggleBtn?.setAttribute('aria-expanded', String(expanded));
    }

    if (toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);
    document.getElementById('shellScrim')?.addEventListener('click', closeSidebarOnMobile);
    window.addEventListener('resize', setSidebarState);
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape') closeSidebarOnMobile();
    });
    setSidebarState();

    // ── Tab switching ─────────────────────────────────────────
    const tabBtns = document.querySelectorAll('.settings-tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;
            tabBtns.forEach(b => {
                b.classList.toggle('is-active', b.dataset.tab === target);
                b.setAttribute('aria-selected', b.dataset.tab === target ? 'true' : 'false');
                b.tabIndex = b.dataset.tab === target ? 0 : -1;
            });
            tabPanels.forEach(panel => {
                panel.classList.toggle('is-hidden', panel.id !== `tab-${target}`);
            });
            if (target === 'security' && loginHistoryState === 'idle') {
                loadLoginHistory();
            }
            if (target === 'drive') {
                loadDriveStatus();
            }
        });

        btn.addEventListener('keydown', event => {
            const buttons = Array.from(tabBtns);
            const currentIndex = buttons.indexOf(btn);
            let nextIndex = currentIndex;

            if (event.key === 'ArrowRight') nextIndex = (currentIndex + 1) % buttons.length;
            if (event.key === 'ArrowLeft') nextIndex = (currentIndex - 1 + buttons.length) % buttons.length;
            if (event.key === 'Home') nextIndex = 0;
            if (event.key === 'End') nextIndex = buttons.length - 1;
            if (nextIndex === currentIndex) return;

            event.preventDefault();
            buttons[nextIndex].focus();
            buttons[nextIndex].click();
        });
    });

    // Google Drive connection
    const driveConnectBtn = document.getElementById('driveConnectBtn');
    const driveDisconnectBtn = document.getElementById('driveDisconnectBtn');
    const driveSyncBtn = document.getElementById('driveSyncBtn');
    const driveSaveBtn = document.getElementById('driveSaveBtn');
    const driveRefreshFilesBtn = document.getElementById('driveRefreshFilesBtn');
    const sourcePickerBtn = document.getElementById('sourcePickerBtn');
    const sourcePickerOptions = document.getElementById('sourcePickerOptions');
    const localSourceFileInput = document.getElementById('localSourceFileInput');
    const driveConfigForm = document.getElementById('driveConfigForm');
    const driveErrorAlert = document.getElementById('driveErrorAlert');
    const driveSuccessAlert = document.getElementById('driveSuccessAlert');
    const driveConnectionStatus = document.getElementById('driveConnectionStatus');
    const driveFileList = document.getElementById('driveFileList');
    const driveFileSearch = document.getElementById('driveFileSearch');
    const driveFilePickerDesc = document.getElementById('driveFilePickerDesc');
    const driveSelectedCount = document.getElementById('driveSelectedCount');
    const driveFolderId = document.getElementById('driveFolderId');
    const driveTenantScope = document.getElementById('driveTenantScope');
    const driveFilePattern = document.getElementById('driveFilePattern');
    const driveScheduleTime = document.getElementById('driveScheduleTime');
    let driveStatusLoaded = false;
    let driveIsConnected = false;
    let driveFilesLoaded = false;
    let systemFilesLoaded = false;
    let sourceType = 'local';
    let driveAvailableFiles = [];
    let driveSelectedFiles = [];
    let systemAvailableFiles = [];
    let systemSelectedFiles = [];
    let driveSearchTimer = 0;

    function interpolateCopy(key, values = {}) {
        return Object.entries(values).reduce(
            (text, [name, value]) => text.replaceAll(`{${name}}`, String(value)),
            t(key),
        );
    }

    function formatDriveFileSize(size) {
        if (!Number.isFinite(size)) return '';
        if (size < 1024) return `${size} B`;
        if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
        return `${(size / (1024 * 1024)).toFixed(1)} MB`;
    }

    function formatDriveModifiedTime(value) {
        if (!value) return '';
        try {
            return new Intl.DateTimeFormat(currentLanguage === 'vi' ? 'vi-VN' : 'en-US', {
                dateStyle: 'short',
                timeStyle: 'short',
            }).format(new Date(value));
        } catch (error) {
            return '';
        }
    }

    function getDriveSelectedIds() {
        return new Set(driveSelectedFiles.map(file => file.id));
    }

    function getSystemSelectedIds() {
        return new Set(systemSelectedFiles.map(file => file.filename));
    }

    function normalizeDriveFile(file) {
        return {
            id: file.id,
            name: file.name || t('common.notAvailable'),
            mimeType: file.mimeType || '',
            modifiedTime: file.modifiedTime || '',
            size: Number.isFinite(file.size) ? file.size : null,
            isGoogleSheet: Boolean(file.isGoogleSheet) || file.mimeType === 'application/vnd.google-apps.spreadsheet',
        };
    }

    function normalizeSystemFile(file) {
        return {
            filename: file.filename || file.name || '',
            name: file.name || file.filename || t('common.notAvailable'),
            file_type: file.file_type || '',
            size_bytes: Number.isFinite(file.size_bytes) ? file.size_bytes : Number(file.size_bytes || 0),
            uploaded_at: file.uploaded_at || '',
        };
    }

    function getActiveSelectedCount() {
        return sourceType === 'local' ? systemSelectedFiles.length : driveSelectedFiles.length;
    }

    function updateDriveSelectedCount() {
        if (!driveSelectedCount) return;
        const count = getActiveSelectedCount();
        driveSelectedCount.textContent = count
            ? interpolateCopy('drive.selectedCount', { count })
            : t('drive.noFileSelected');
        driveSelectedCount.className = `status-pill ${count ? 'tone-success' : 'tone-neutral'}`;
        setRuntimeTranslation(driveSelectedCount, '');
        if (driveSyncBtn) driveSyncBtn.disabled = count === 0 || (sourceType === 'drive' && !driveIsConnected);
    }

    function renderDriveFileList(state = 'ready') {
        if (!driveFileList) return;
        updateDriveSelectedCount();
        if (driveFilePickerDesc) {
            driveFilePickerDesc.textContent = t(sourceType === 'local' ? 'drive.systemPickerDesc' : 'drive.drivePickerDesc');
            setRuntimeTranslation(driveFilePickerDesc, sourceType === 'local' ? 'drive.systemPickerDesc' : 'drive.drivePickerDesc');
        }

        if (sourceType === 'drive' && !driveIsConnected) {
            driveFileList.innerHTML = `<div class="empty-state"><span class="text-faint">${escHtml(t('drive.fileListConnectHint'))}</span></div>`;
            return;
        }
        if (state === 'loading') {
            driveFileList.innerHTML = `<div class="empty-state"><span class="text-faint">${escHtml(t('drive.loadingFiles'))}</span></div>`;
            return;
        }
        const availableFiles = sourceType === 'local' ? systemAvailableFiles : driveAvailableFiles;
        if (!availableFiles.length) {
            driveFileList.innerHTML = `<div class="empty-state"><span class="text-faint">${escHtml(t('drive.fileListEmpty'))}</span></div>`;
            return;
        }

        const selectedIds = sourceType === 'local' ? getSystemSelectedIds() : getDriveSelectedIds();
        driveFileList.innerHTML = availableFiles.map(file => {
            const fileKey = sourceType === 'local' ? file.filename : file.id;
            const checked = selectedIds.has(fileKey) ? 'checked' : '';
            const typeLabel = sourceType === 'local'
                ? (file.file_type || t('drive.systemFileType'))
                : (file.isGoogleSheet ? t('drive.sheetType') : t('drive.fileType'));
            const size = sourceType === 'local' ? file.size_bytes : file.size;
            const modified = sourceType === 'local' ? file.uploaded_at : file.modifiedTime;
            const meta = [typeLabel, formatDriveFileSize(size), formatDriveModifiedTime(modified)].filter(Boolean).join(' • ');
            return `
                <label class="drive-file-option">
                    <input type="checkbox" value="${escHtml(fileKey)}" ${checked}>
                    <span class="drive-file-option__body">
                        <strong>${escHtml(file.name)}</strong>
                        <span>${escHtml(meta)}</span>
                    </span>
                </label>
            `;
        }).join('');

        driveFileList.querySelectorAll('input[type="checkbox"]').forEach(input => {
            input.addEventListener('change', () => {
                const file = availableFiles.find(item => (sourceType === 'local' ? item.filename : item.id) === input.value);
                if (!file) return;
                if (sourceType === 'local') {
                    if (input.checked) {
                        if (!systemSelectedFiles.some(item => item.filename === file.filename)) {
                            systemSelectedFiles.push(file);
                        }
                    } else {
                        systemSelectedFiles = systemSelectedFiles.filter(item => item.filename !== file.filename);
                    }
                } else if (input.checked) {
                    if (!driveSelectedFiles.some(item => item.id === file.id)) {
                        driveSelectedFiles.push(file);
                    }
                } else {
                    driveSelectedFiles = driveSelectedFiles.filter(item => item.id !== file.id);
                }
                updateDriveSelectedCount();
            });
        });
    }

    async function loadDriveFiles({ force = false } = {}) {
        if (!driveIsConnected || (driveFilesLoaded && !force)) {
            renderDriveFileList();
            return;
        }
        hideAlert(driveErrorAlert);
        setBtnLoading(driveRefreshFilesBtn, true, 'drive.refreshFiles');
        renderDriveFileList('loading');
        try {
            const params = new URLSearchParams();
            const searchText = driveFileSearch?.value.trim() || '';
            if (searchText) params.set('q', searchText);
            const r = await fetch(`/api/google-drive/files${params.toString() ? `?${params.toString()}` : ''}`);
            const data = await r.json();
            if (!r.ok) throw new Error(data.error || t('drive.fileListError'));
            driveAvailableFiles = (data.files || []).map(normalizeDriveFile);
            if (!driveSelectedFiles.length && Array.isArray(data.selected_files)) {
                driveSelectedFiles = data.selected_files.map(normalizeDriveFile);
            }
            driveFilesLoaded = true;
            renderDriveFileList();
        } catch (err) {
            driveFileList.innerHTML = `<div class="empty-state"><span class="text-faint">${escHtml(t('drive.fileListError'))}</span></div>`;
            showAlert(driveErrorAlert, err.message || t('drive.fileListError'));
        } finally {
            setBtnLoading(driveRefreshFilesBtn, false, 'drive.refreshFiles');
            if (driveRefreshFilesBtn) driveRefreshFilesBtn.disabled = !driveIsConnected;
        }
    }

    async function loadSystemFiles({ force = false } = {}) {
        renderDriveFileList();
    }

    function loadActiveSourceFiles({ force = false } = {}) {
        if (sourceType === 'local') {
            loadSystemFiles({ force });
        } else {
            loadDriveFiles({ force });
        }
    }

    function setSourceType(nextSourceType, { load = true } = {}) {
        sourceType = nextSourceType === 'drive' ? 'drive' : 'local';
        sourcePickerOptions?.querySelectorAll('[data-source-option]').forEach(btn => {
            btn.classList.toggle('is-active', btn.dataset.sourceOption === sourceType);
        });
        if (driveFileSearch) driveFileSearch.value = '';
        renderDriveFileList();
        if (load) loadActiveSourceFiles();
    }

    function renderDriveStatus({ connected = false, runtime_ready = true, runtime_error = '', config = null } = {}) {
        driveIsConnected = Boolean(connected);
        if (config) {
            sourceType = config.source_type === 'drive' ? 'drive' : 'local';
            if (driveFolderId) driveFolderId.value = config.folder_id || '';
            if (driveTenantScope) driveTenantScope.value = config.tenant_scope || 'current';
            if (driveFilePattern) driveFilePattern.value = config.file_pattern || '*.xlsx;*.xls;*.csv';
            if (driveScheduleTime) driveScheduleTime.value = config.schedule_time || '23:30';
            driveSelectedFiles = Array.isArray(config.selected_files)
                ? config.selected_files.map(normalizeDriveFile)
                : [];
            systemSelectedFiles = Array.isArray(config.selected_system_files)
                ? config.selected_system_files.map(normalizeSystemFile)
                : [];
        }

        if (driveConnectionStatus) {
            const statusKey = !runtime_ready ? 'drive.statusNotReady' : (driveIsConnected ? 'drive.statusConnected' : 'drive.statusDisconnected');
            driveConnectionStatus.textContent = t(statusKey);
            driveConnectionStatus.className = `status-pill ${driveIsConnected ? 'tone-success' : 'tone-neutral'}`;
            setRuntimeTranslation(driveConnectionStatus, statusKey);
        }
        sourcePickerOptions?.querySelectorAll('[data-source-option]').forEach(btn => {
            btn.classList.toggle('is-active', btn.dataset.sourceOption === sourceType);
        });
        if (driveDisconnectBtn) driveDisconnectBtn.disabled = !driveIsConnected;
        if (driveRefreshFilesBtn) driveRefreshFilesBtn.disabled = sourceType === 'drive' && (!runtime_ready || !driveIsConnected);
        if (driveSyncBtn) driveSyncBtn.disabled = getActiveSelectedCount() === 0 || (sourceType === 'drive' && (!runtime_ready || !driveIsConnected));
        renderDriveFileList();
        if (!runtime_ready && runtime_error) {
            showAlert(driveErrorAlert, runtime_error, 'danger');
        }
    }

    async function loadDriveStatus({ force = false } = {}) {
        if (driveStatusLoaded && !force) return;
        try {
            const r = await fetch('/api/google-drive/status');
            const data = await r.json();
            if (!r.ok) throw new Error(data.error || t('drive.configLoadError'));
            driveStatusLoaded = true;
            renderDriveStatus(data);
            loadActiveSourceFiles();
        } catch (err) {
            showAlert(driveErrorAlert, err.message || t('drive.configLoadError'));
        }
    }

    async function saveDriveConfig() {
        hideAlert(driveSuccessAlert);
        hideAlert(driveErrorAlert);
        const body = {
            source_type: sourceType,
            folder_id: driveFolderId?.value.trim() || '',
            tenant_scope: driveTenantScope?.value || 'current',
            file_pattern: driveFilePattern?.value.trim() || '*.xlsx;*.xls;*.csv',
            selected_files: driveSelectedFiles.map(file => ({
                id: file.id,
                name: file.name,
                mimeType: file.mimeType,
            })),
            selected_system_files: systemSelectedFiles.map(file => ({
                filename: file.filename,
                file_type: file.file_type,
                size_bytes: file.size_bytes,
                uploaded_at: file.uploaded_at,
            })),
            schedule_time: driveScheduleTime?.value || '23:30',
        };
        setBtnLoading(driveSaveBtn, true, 'drive.save');
        try {
            const r = await fetch('/api/google-drive/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            const data = await r.json();
            if (!r.ok) throw new Error(data.error || t('drive.configLoadError'));
            renderDriveStatus({ connected: driveIsConnected, runtime_ready: true, config: data.config });
            showAlert(driveSuccessAlert, '', 'success', 4000, 'drive.configSaved');
            return true;
        } catch (err) {
            showAlert(driveErrorAlert, err.message || t('drive.configLoadError'));
            return false;
        } finally {
            setBtnLoading(driveSaveBtn, false, 'drive.save');
        }
    }

    driveConnectBtn?.addEventListener('click', async () => {
        hideAlert(driveSuccessAlert);
        hideAlert(driveErrorAlert);
        setBtnLoading(driveConnectBtn, true, 'drive.connect');
        try {
            const r = await fetch('/api/google-drive/connect-url');
            const data = await r.json();
            if (!r.ok) throw new Error(data.error || t('drive.connectError'));
            window.location.href = data.url;
        } catch (err) {
            showAlert(driveErrorAlert, err.message || t('drive.oauthUnavailable'));
            setBtnLoading(driveConnectBtn, false, 'drive.connect');
        }
    });

    driveDisconnectBtn?.addEventListener('click', async () => {
        hideAlert(driveSuccessAlert);
        hideAlert(driveErrorAlert);
        setBtnLoading(driveDisconnectBtn, true, 'drive.disconnect');
        try {
            const r = await fetch('/api/google-drive/disconnect', { method: 'POST' });
            const data = await r.json();
            if (!r.ok) throw new Error(data.error || t('drive.disconnectError'));
            driveStatusLoaded = false;
            driveFilesLoaded = false;
            systemFilesLoaded = false;
            driveAvailableFiles = [];
            driveSelectedFiles = [];
            systemAvailableFiles = [];
            systemSelectedFiles = [];
            renderDriveStatus({ connected: false, runtime_ready: true });
            showAlert(driveSuccessAlert, '', 'success', 4000, 'drive.disconnectSuccess');
        } catch (err) {
            showAlert(driveErrorAlert, err.message || t('drive.disconnectError'));
        } finally {
            setBtnLoading(driveDisconnectBtn, false, 'drive.disconnect');
            if (!driveIsConnected && driveDisconnectBtn) driveDisconnectBtn.disabled = true;
            updateDriveSelectedCount();
        }
    });

    driveRefreshFilesBtn?.addEventListener('click', () => {
        if (sourceType === 'local') {
            localSourceFileInput?.click();
        } else {
            driveFilesLoaded = false;
            loadActiveSourceFiles({ force: true });
        }
    });

    localSourceFileInput?.addEventListener('change', async () => {
        const selected = Array.from(localSourceFileInput.files || []);
        if (!selected.length) return;
        hideAlert(driveErrorAlert);
        hideAlert(driveSuccessAlert);
        setBtnLoading(driveRefreshFilesBtn, true, 'drive.refreshFiles');

        try {
            const formData = new FormData();
            selected.forEach(file => formData.append('files', file));
            const tenantId = APP_CONTEXT.userTenant;
            if (!tenantId) throw new Error(t('drive.syncError'));

            const r = await fetch(`/api/upload/${encodeURIComponent(tenantId)}`, {
                method: 'POST',
                body: formData,
            });
            const data = await r.json();
            if (!r.ok || data.success === false) {
                throw new Error(data.message || data.error || t('drive.syncError'));
            }

            const uploadedFiles = (data.uploaded_files || [])
                .filter(item => item.success)
                .map(item => normalizeSystemFile({
                    filename: item.filename,
                    file_type: item.file_type,
                    size_bytes: item.file_size_bytes,
                    uploaded_at: new Date().toISOString(),
                }));

            systemAvailableFiles = uploadedFiles;
            systemSelectedFiles = uploadedFiles;
            systemFilesLoaded = true;
            renderDriveFileList();
            showAlert(driveSuccessAlert, '', 'success', 4000, 'drive.localUploadSuccess');
        } catch (err) {
            showAlert(driveErrorAlert, err.message || t('drive.syncError'));
        } finally {
            setBtnLoading(driveRefreshFilesBtn, false, 'drive.refreshFiles');
            localSourceFileInput.value = '';
        }
    });

    driveFileSearch?.addEventListener('input', () => {
        window.clearTimeout(driveSearchTimer);
        driveSearchTimer = window.setTimeout(() => {
            if (sourceType === 'local') {
                systemFilesLoaded = false;
            } else {
                driveFilesLoaded = false;
            }
            loadActiveSourceFiles({ force: true });
        }, 350);
    });

    sourcePickerBtn?.addEventListener('click', () => {
        if (!sourcePickerOptions) return;
        const isOpen = sourcePickerOptions.classList.toggle('is-hidden') === false;
        sourcePickerBtn.setAttribute('aria-expanded', String(isOpen));
    });

    sourcePickerOptions?.querySelectorAll('[data-source-option]').forEach(btn => {
        btn.addEventListener('click', () => {
            sourcePickerOptions.classList.add('is-hidden');
            sourcePickerBtn?.setAttribute('aria-expanded', 'false');
            setSourceType(btn.dataset.sourceOption, { load: true });
        });
    });

    driveSyncBtn?.addEventListener('click', async () => {
        hideAlert(driveSuccessAlert);
        hideAlert(driveErrorAlert);
        if (getActiveSelectedCount() === 0) {
            showAlert(driveErrorAlert, '', 'danger', 0, 'drive.folderRequired');
            return;
        }
        const configSaved = await saveDriveConfig();
        if (!configSaved) return;
        setBtnLoading(driveSyncBtn, true, 'drive.syncRun');
        try {
            const r = await fetch('/api/google-drive/sync', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ run_etl: true }),
            });
            const data = await r.json();
            if (!r.ok) throw new Error(data.error || data.message || t('drive.syncError'));
            const total = data.synced_files?.length || 0;
            showAlert(driveSuccessAlert, `${t('drive.syncSuccess')} (${total})`, 'success', 0);
        } catch (err) {
            showAlert(driveErrorAlert, err.message || t('drive.syncError'));
        } finally {
            setBtnLoading(driveSyncBtn, false, 'drive.syncRun');
        }
    });

    driveConfigForm?.addEventListener('submit', async event => {
        event.preventDefault();
        await saveDriveConfig();
    });

    const initialParams = new URLSearchParams(window.location.search);
    if (initialParams.get('tab') === 'drive') {
        document.querySelector('[data-tab="drive"]')?.click();
    }
    if (initialParams.get('drive') === 'connected') {
        showAlert(driveSuccessAlert, '', 'success', 5000, 'drive.statusConnected');
        loadDriveStatus({ force: true });
    }
    if (initialParams.get('drive_error')) {
        showAlert(driveErrorAlert, initialParams.get('drive_error'), 'danger');
        loadDriveStatus({ force: true });
    }

    // ── Password toggle (show/hide) ───────────────────────────
    document.querySelectorAll('[data-toggle-password]').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input = document.getElementById(targetId);
            if (!input) return;
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            btn.setAttribute('aria-pressed', String(isHidden));
        });
    });

    // ══════════════════════════════════════════════════════════
    // Load profile on page open
    // ══════════════════════════════════════════════════════════
    async function loadProfile() {
        try {
            const r = await fetch('/api/me/profile');
            if (!r.ok) return;
            const data = await r.json();
            profileCache = data;
            populateProfile(data);
        } catch (error) {
            showAlert(profileErrorAlert, '', 'danger', 0, 'profile.loadError');
        }
    }

    function populateProfile(data) {
        const fallback = t('common.notAvailable');

        const headerUsername = document.getElementById('headerUsername');
        if (headerUsername) headerUsername.textContent = data.username || fallback;

        const identityUsername = document.getElementById('identityUsername');
        if (identityUsername) identityUsername.textContent = data.username || fallback;

        const identityCreatedAt = document.getElementById('identityCreatedAt');
        if (identityCreatedAt) identityCreatedAt.textContent = data.created_at || fallback;

        const displayName = document.getElementById('displayName');
        if (displayName) displayName.value = data.display_name || '';

        const email = document.getElementById('email');
        if (email) email.value = data.email || '';

        const phone = document.getElementById('phone');
        if (phone) phone.value = data.phone || '';

        if (data.avatar_data) {
            setAvatarImage(data.avatar_data, data.username || '?');
        } else {
            clearAvatarImage(data.username || '?');
        }

        if (sidebarAvatarInitial && (data.display_name || data.username)) {
            const name = data.display_name || data.username;
            sidebarAvatarInitial.textContent = name[0].toUpperCase();
        }
    }

    // ══════════════════════════════════════════════════════════
    // Avatar handling
    // ══════════════════════════════════════════════════════════
    const avatarInput = document.getElementById('avatarInput');
    const avatarImg = document.getElementById('avatarImg');
    const avatarInitials = document.getElementById('avatarInitials');
    const avatarRemoveBtn = document.getElementById('avatarRemoveBtn');
    const avatarSuccessMsg = document.getElementById('avatarSuccessMsg');
    const avatarErrorMsg = document.getElementById('avatarErrorMsg');
    const sidebarAvatarInitial = document.getElementById('sidebarAvatarInitial');
    const sidebarAvatarImg = document.getElementById('sidebarAvatarImg');

    function setAvatarImage(dataUrl, username) {
        if (avatarImg) {
            avatarImg.src = dataUrl;
            avatarImg.classList.remove('is-hidden');
        }
        avatarInitials?.classList.add('is-hidden');
        if (avatarRemoveBtn) avatarRemoveBtn.hidden = false;

        if (sidebarAvatarImg) {
            sidebarAvatarImg.src = dataUrl;
            sidebarAvatarImg.classList.remove('is-hidden');
        }
        sidebarAvatarInitial?.classList.add('is-hidden');
    }

    function clearAvatarImage(username) {
        if (avatarImg) {
            avatarImg.src = '';
            avatarImg.classList.add('is-hidden');
        }
        const initial = (username || '?')[0].toUpperCase();
        if (avatarInitials) {
            avatarInitials.textContent = initial;
            avatarInitials.classList.remove('is-hidden');
        }
        if (avatarRemoveBtn) avatarRemoveBtn.hidden = true;

        if (sidebarAvatarImg) {
            sidebarAvatarImg.src = '';
            sidebarAvatarImg.classList.add('is-hidden');
        }
        if (sidebarAvatarInitial) {
            sidebarAvatarInitial.textContent = initial;
            sidebarAvatarInitial.classList.remove('is-hidden');
        }
    }

    function resizeImage(file, maxDim = 200) {
        return new Promise((resolve, reject) => {
            if (file.size > 8_000_000) {
                reject(new Error(t('profile.avatarFileTooLarge')));
                return;
            }
            const reader = new FileReader();
            reader.onload = evt => {
                const img = new Image();
                img.onload = () => {
                    const scale = Math.min(maxDim / img.width, maxDim / img.height, 1);
                    const w = Math.round(img.width * scale);
                    const h = Math.round(img.height * scale);
                    const canvas = document.createElement('canvas');
                    canvas.width = w;
                    canvas.height = h;
                    const ctx2 = canvas.getContext('2d');
                    ctx2.drawImage(img, 0, 0, w, h);
                    resolve(canvas.toDataURL('image/jpeg', 0.88));
                };
                img.onerror = () => reject(new Error(t('profile.avatarReadError')));
                img.src = evt.target.result;
            };
            reader.onerror = () => reject(new Error(t('profile.fileReadError')));
            reader.readAsDataURL(file);
        });
    }

    if (avatarInput) {
        avatarInput.addEventListener('change', async () => {
            const file = avatarInput.files[0];
            if (!file) return;
            hideAlert(avatarErrorMsg);

            try {
                const dataUrl = await resizeImage(file);
                const r = await fetch('/api/me/avatar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ avatar_data: dataUrl }),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || data.error || t('profile.avatarUploadError'));

                const username = profileCache?.username || '?';
                setAvatarImage(dataUrl, username);
                showAlert(avatarSuccessMsg, '', 'success', 4000, 'profile.avatarUpdated');
            } catch (err) {
                showAlert(avatarErrorMsg, err.message || t('profile.avatarUploadError'));
            } finally {
                avatarInput.value = '';
            }
        });
    }

    if (avatarRemoveBtn) {
        avatarRemoveBtn.addEventListener('click', async () => {
            hideAlert(avatarErrorMsg);
            try {
                const r = await fetch('/api/me/avatar', { method: 'DELETE' });
                if (!r.ok) throw new Error(t('profile.avatarDeleteError'));
                const username = profileCache?.username || '?';
                clearAvatarImage(username);
                showAlert(avatarSuccessMsg, '', 'success', 3000, 'profile.avatarRemoved');
            } catch (err) {
                showAlert(avatarErrorMsg, err.message || t('profile.avatarDeleteError'));
            }
        });
    }

    // ══════════════════════════════════════════════════════════
    // Profile form submit
    // ══════════════════════════════════════════════════════════
    const profileForm = document.getElementById('profileForm');
    const profileErrorAlert = document.getElementById('profileErrorAlert');
    const profileSuccessAlert = document.getElementById('profileSuccessAlert');
    const profileSaveBtn = document.getElementById('profileSaveBtn');
    const profileResetBtn = document.getElementById('profileResetBtn');

    if (profileForm) {
        profileForm.addEventListener('submit', async e => {
            e.preventDefault();
            hideAlert(profileErrorAlert);
            hideAlert(profileSuccessAlert);
            setBtnLoading(profileSaveBtn, true, 'profile.save');

            const body = {
                display_name: document.getElementById('displayName')?.value.trim() || null,
                email: document.getElementById('email')?.value.trim() || null,
                phone: document.getElementById('phone')?.value.trim() || null,
            };

            try {
                const r = await fetch('/api/me/profile', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || data.error || t('profile.updateError'));

                if (profileCache) {
                    profileCache.display_name = body.display_name;
                    profileCache.email = body.email;
                    profileCache.phone = body.phone;
                }

                const name = body.display_name || profileCache?.username || '?';
                if (sidebarAvatarInitial && sidebarAvatarImg?.classList.contains('is-hidden')) {
                    sidebarAvatarInitial.textContent = name[0].toUpperCase();
                }
                if (avatarInitials && avatarImg?.classList.contains('is-hidden')) {
                    avatarInitials.textContent = name[0].toUpperCase();
                }

                showAlert(profileSuccessAlert, '', 'success', 0, 'profile.updateSuccess');
            } catch (err) {
                showAlert(profileErrorAlert, err.message || t('profile.updateError'));
            } finally {
                setBtnLoading(profileSaveBtn, false, 'profile.save');
            }
        });
    }

    if (profileResetBtn) {
        profileResetBtn.addEventListener('click', () => {
            if (!profileCache) return;
            document.getElementById('displayName').value = profileCache.display_name || '';
            document.getElementById('email').value = profileCache.email || '';
            document.getElementById('phone').value = profileCache.phone || '';
            hideAlert(profileErrorAlert);
            hideAlert(profileSuccessAlert);
        });
    }

    // ══════════════════════════════════════════════════════════
    // Password strength meter
    // ══════════════════════════════════════════════════════════
    const newPasswordInput = document.getElementById('newPassword');
    const pwdStrengthEl = document.getElementById('pwdStrength');
    const pwdStrengthLabel = document.getElementById('pwdStrengthLabel');

    function scorePassword(pwd) {
        let score = 0;
        if (pwd.length >= 6) score++;
        if (pwd.length >= 10) score++;
        if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return Math.min(Math.max(Math.ceil(score * 4 / 5), 1), 4);
    }

    function updatePasswordStrength() {
        if (!newPasswordInput || !pwdStrengthEl) return;
        const val = newPasswordInput.value;
        if (!val) {
            pwdStrengthEl.hidden = true;
            return;
        }
        pwdStrengthEl.hidden = false;
        const level = scorePassword(val);
        pwdStrengthEl.dataset.level = level;
        if (pwdStrengthLabel) pwdStrengthLabel.textContent = t(strengthLabelKeys[level]);
    }

    if (newPasswordInput && pwdStrengthEl) {
        newPasswordInput.addEventListener('input', updatePasswordStrength);
    }

    // ══════════════════════════════════════════════════════════
    // Password form submit
    // ══════════════════════════════════════════════════════════
    const passwordForm = document.getElementById('passwordForm');
    const passwordErrorAlert = document.getElementById('passwordErrorAlert');
    const passwordSuccessAlert = document.getElementById('passwordSuccessAlert');
    const passwordSaveBtn = document.getElementById('passwordSaveBtn');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    if (passwordForm) {
        passwordForm.addEventListener('submit', async e => {
            e.preventDefault();
            hideAlert(passwordErrorAlert);
            hideAlert(passwordSuccessAlert);
            setFieldError(confirmPasswordError, '');

            const currentPwd = document.getElementById('currentPassword')?.value || '';
            const newPwd = document.getElementById('newPassword')?.value || '';
            const confirmPwd = document.getElementById('confirmPassword')?.value || '';

            if (newPwd !== confirmPwd) {
                setFieldError(confirmPasswordError, 'security.confirmMismatch');
                return;
            }
            if (newPwd.length < 6) {
                showAlert(passwordErrorAlert, '', 'danger', 0, 'security.minLengthError');
                return;
            }

            setBtnLoading(passwordSaveBtn, true, 'security.save');

            try {
                const r = await fetch('/api/me/password', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ current_password: currentPwd, new_password: newPwd }),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || data.error || t('security.updateError'));

                passwordForm.reset();
                if (pwdStrengthEl) pwdStrengthEl.hidden = true;
                showAlert(passwordSuccessAlert, '', 'success', 0, 'security.updateSuccess');
            } catch (err) {
                showAlert(passwordErrorAlert, err.message || t('security.updateError'));
            } finally {
                setBtnLoading(passwordSaveBtn, false, 'security.save');
            }
        });
    }

    // ══════════════════════════════════════════════════════════
    // Login history
    // ══════════════════════════════════════════════════════════
    const loginHistoryBody = document.getElementById('loginHistoryBody');
    const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

    function parseUserAgent(ua) {
        if (!ua) return t('common.notAvailable');
        let browser = t('history.unknownClient');
        let os = '';

        if (/Chrome\/(\d+)/.test(ua) && !/Chromium/.test(ua) && !/Edg/.test(ua) && !/OPR/.test(ua)) {
            browser = `Chrome ${RegExp.$1}`;
        } else if (/Firefox\/(\d+)/.test(ua)) {
            browser = `Firefox ${RegExp.$1}`;
        } else if (/Edg\/(\d+)/.test(ua)) {
            browser = `Edge ${RegExp.$1}`;
        } else if (/OPR\/(\d+)/.test(ua)) {
            browser = `Opera ${RegExp.$1}`;
        } else if (/Safari\//.test(ua) && !/Chrome/.test(ua)) {
            browser = 'Safari';
        }

        if (/Windows NT 10/.test(ua)) os = 'Windows 10/11';
        else if (/Windows NT/.test(ua)) os = 'Windows';
        else if (/Mac OS X/.test(ua)) os = 'macOS';
        else if (/Linux/.test(ua) && !/Android/.test(ua)) os = 'Linux';
        else if (/Android/.test(ua)) os = 'Android';
        else if (/iPhone|iPad/.test(ua)) os = 'iOS';

        return os ? `${browser}, ${os}` : browser;
    }

    function renderLoginHistory() {
        if (!loginHistoryBody) return;

        if (loginHistoryState === 'idle' || loginHistoryState === 'loading') {
            loginHistoryBody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><span class="text-faint">${escHtml(t('history.loading'))}</span></div></td></tr>`;
            return;
        }

        if (loginHistoryState === 'error') {
            loginHistoryBody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><span class="tone-danger">${escHtml(t('history.error'))}</span></div></td></tr>`;
            return;
        }

        if (!loginHistoryCache.length) {
            loginHistoryBody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><strong>${escHtml(t('history.emptyTitle'))}</strong><span>${escHtml(t('history.emptyDesc'))}</span></div></td></tr>`;
            return;
        }

        loginHistoryBody.innerHTML = loginHistoryCache.map((item, idx) => {
            const isSuccess = item.status === 'success';
            const pillClass = isSuccess ? 'tone-live' : 'tone-danger';
            const pillLabel = isSuccess ? t('history.success') : t('history.failure');
            const isCurrent = idx === 0
                ? `<span class="status-pill tone-neutral login-session-pill">${escHtml(t('history.currentSession'))}</span>`
                : '';

            return `
                <tr>
                    <td data-label="${escHtml(t('history.time'))}">
                        <span class="login-time">${escHtml(item.login_at)}</span>
                        ${isCurrent}
                    </td>
                    <td data-label="${escHtml(t('history.ip'))}">
                        <span class="login-ip">${escHtml(item.ip_address || t('common.notAvailable'))}</span>
                    </td>
                    <td data-label="${escHtml(t('history.device'))}">
                        <span class="ua-text" title="${escHtml(item.user_agent || '')}">
                            ${escHtml(parseUserAgent(item.user_agent))}
                        </span>
                    </td>
                    <td data-label="${escHtml(t('history.result'))}">
                        <span class="status-pill ${pillClass}">${escHtml(pillLabel)}</span>
                    </td>
                </tr>`;
        }).join('');
    }

    async function loadLoginHistory() {
        if (!loginHistoryBody) return;
        loginHistoryState = 'loading';
        renderLoginHistory();

        try {
            const r = await fetch('/api/me/login-history');
            const data = await r.json();
            loginHistoryCache = Array.isArray(data.items) ? data.items : [];
            loginHistoryState = 'loaded';
            renderLoginHistory();
        } catch (err) {
            loginHistoryCache = [];
            loginHistoryState = 'error';
            renderLoginHistory();
        }
    }

    function escHtml(str) {
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    if (refreshHistoryBtn) {
        refreshHistoryBtn.addEventListener('click', () => {
            loadLoginHistory();
        });
    }

    document.querySelectorAll('[data-navto]').forEach(link => {
        link.addEventListener('click', () => {
            const page = link.dataset.navto;
            if (page) sessionStorage.setItem('dashboardPage', page);
        });
    });

    currentLanguage = loadSavedLanguage();
    applyLanguage(currentLanguage);

    if (languageSelect) {
        languageSelect.addEventListener('change', () => {
            applyLanguage(languageSelect.value);
        });
    }

    loadProfile();
}());
