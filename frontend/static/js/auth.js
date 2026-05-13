(function () {
    'use strict';

    function byId(id) {
        return document.getElementById(id);
    }

    const pageType = document.body.dataset.authPage || (byId('registerForm') ? 'register' : 'login');

    const COPY = {
        vi: {
            page: {
                languageLabel: 'Ngôn ngữ',
                languageSelectAria: 'Chọn ngôn ngữ giao diện',
                login: {
                    browserTitle: 'Đăng nhập | DWH Operations Console',
                    skipLink: 'Bỏ qua giới thiệu, tới biểu mẫu đăng nhập',
                    brandMeta: 'Cổng truy cập theo tenant cho nền tảng dữ liệu bán lẻ',
                    heroEyebrow: 'Truy cập an toàn',
                    heroTitle: 'Truy cập an toàn vào nền tảng dữ liệu bán lẻ.',
                    heroDescription: 'Đăng nhập để kiểm tra trạng thái hệ thống, theo dõi dữ liệu và mở dashboard trong đúng phạm vi tenant đã được cấp.',
                    statusAria: 'Tín hiệu hệ thống và bảo mật',
                    signalSecurityTitle: 'Tư thế bảo mật',
                    signalGatewayLabel: 'Auth Gateway',
                    signalSessionLabel: 'Chính sách phiên',
                    signalSessionValue: 'Thiết lập sau đăng nhập',
                    signalScopeTitle: 'Phân quyền dữ liệu',
                    signalTenantLabel: 'Phạm vi tenant',
                    signalTenantValue: 'Xác định sau xác thực',
                    signalAccessLabel: 'Quyền truy cập',
                    signalAccessValue: 'Theo vai trò được cấp',
                    cardEyebrow: 'Đăng nhập',
                    cardTitle: 'Vào nền tảng',
                    cardDescription: 'Dùng tài khoản đã được cấp để mở dashboard, tín hiệu vận hành và lớp dữ liệu liên quan đến tenant của bạn.',
                    usernameLabel: 'Tên đăng nhập',
                    usernamePlaceholder: 'ví dụ: admin',
                    passwordLabel: 'Mật khẩu',
                    passwordPlaceholder: 'Nhập mật khẩu',
                    passwordToggleAria: 'Hiện hoặc ẩn mật khẩu',
                    submit: 'Đăng nhập vào hệ thống',
                    submitLoading: 'Đang xác thực truy cập...',
                    footerPrompt: 'Chưa có tài khoản?',
                    footerLink: 'Tạo tài khoản User',
                    footerNote: 'Đăng nhập là điểm vào cho dữ liệu, dashboard và tín hiệu hệ thống.',
                },
                register: {
                    browserTitle: 'Đăng ký User | DWH Operations Console',
                    skipLink: 'Bỏ qua giới thiệu, tới biểu mẫu đăng ký',
                    brandMeta: 'Đăng ký truy cập theo tenant cho nền tảng dữ liệu bán lẻ',
                    heroEyebrow: 'Khởi tạo truy cập',
                    heroTitle: 'Tạo tài khoản để nhận quyền truy cập dữ liệu.',
                    heroDescription: 'Self-signup này tạo tài khoản User với quyền xem dashboard và dữ liệu trong tenant được chỉ định.',
                    statusAria: 'Tín hiệu hệ thống và phân quyền',
                    signalAccessTitle: 'Kiểm soát truy cập',
                    signalGatewayLabel: 'Auth Gateway',
                    signalRoleLabel: 'Chính sách vai trò',
                    signalRoleValue: 'User mặc định khi self-signup',
                    signalDataTitle: 'Trạng thái dữ liệu',
                    signalDashboardLabel: 'Phạm vi dashboard',
                    signalDashboardValue: 'Theo tenant đã chọn',
                    signalDataLabel: 'Truy cập dữ liệu',
                    signalDataValue: 'Kích hoạt sau xác thực',
                    cardEyebrow: 'Đăng ký',
                    cardTitle: 'Tạo tài khoản User',
                    cardDescription: 'Dùng mã tenant do admin cung cấp hoặc chọn tenant được phép self-signup. Quyền xem dữ liệu sẽ được áp tự động theo chính sách tenant.',
                    usernameLabel: 'Tên đăng nhập',
                    usernamePlaceholder: 'ví dụ: user_hn',
                    passwordLabel: 'Mật khẩu',
                    passwordPlaceholder: 'Ít nhất 6 ký tự',
                    passwordToggleAria: 'Hiện hoặc ẩn mật khẩu',
                    confirmLabel: 'Xác nhận mật khẩu',
                    confirmPlaceholder: 'Nhập lại mật khẩu',
                    confirmToggleAria: 'Hiện hoặc ẩn mật khẩu xác nhận',
                    tenantLabel: 'Tenant',
                    scopeEyebrow: 'Phạm vi mặc định',
                    scopePill: 'Theo tenant',
                    scopeTitle: 'User',
                    scopeDescription: 'Self-signup chỉ cấp quyền xem dashboard và dữ liệu trong tenant đã chọn. Mọi quyền mở rộng sẽ do admin quản trị sau.',
                    submit: 'Tạo tài khoản User',
                    submitLoading: 'Đang cấp quyền truy cập...',
                    footerPrompt: 'Đã có tài khoản?',
                    footerLink: 'Quay lại đăng nhập',
                    footerNote: 'Self-signup chỉ áp dụng cho lớp truy cập User của hệ thống.',
                },
            },
            trust: {
                checking: {
                    label: 'Đang kiểm tra',
                    loginMessage: 'Đang kiểm tra lớp xác thực trước khi cho phép đăng nhập.',
                    registerMessage: 'Đang kiểm tra lớp xác thực trước khi tạo tài khoản mới.',
                },
                ok: {
                    label: 'Đang phản hồi',
                    loginMessage: 'Lớp xác thực đang phản hồi. Bạn có thể tiếp tục đăng nhập.',
                    registerMessage: 'Lớp xác thực đang phản hồi. Bạn có thể tiếp tục tạo tài khoản mới.',
                },
                error: {
                    label: 'Mất phản hồi',
                    loginMessage: 'Lớp xác thực đang mất phản hồi. Kiểm tra dịch vụ trước khi tiếp tục đăng nhập.',
                    registerMessage: 'Lớp xác thực đang mất phản hồi. Kiểm tra dịch vụ trước khi tiếp tục tạo tài khoản.',
                },
            },
            validation: {
                usernameRequired: 'Vui lòng nhập tên đăng nhập.',
                passwordRequired: 'Vui lòng nhập mật khẩu.',
                invalidUsername: 'Chỉ dùng chữ cái, số hoặc dấu gạch dưới.',
                passwordTooShort: 'Mật khẩu cần ít nhất 6 ký tự.',
                confirmMismatch: 'Mật khẩu xác nhận chưa khớp.',
                tenantRequired: 'Vui lòng chọn hoặc nhập mã tenant.',
                loginInvalid: 'Thông tin đăng nhập không hợp lệ. Kiểm tra lại tài khoản và thử lại.',
                loginForbidden: 'Tài khoản hoặc phạm vi cửa hàng đang bị khóa. Liên hệ quản trị để kiểm tra.',
                loginFailed: 'Không thể đăng nhập. Kiểm tra lại tài khoản và thử lại.',
                loginService: 'Không kết nối được lớp xác thực. Kiểm tra dịch vụ rồi thử lại.',
                registerFailed: 'Không thể tạo tài khoản. Kiểm tra dữ liệu rồi thử lại.',
                registerConflict: 'Tên đăng nhập đã tồn tại. Vui lòng chọn mã đăng nhập khác.',
                registerService: 'Không kết nối được dịch vụ đăng ký. Kiểm tra Auth Gateway rồi thử lại.',
                registerSuccess: 'Tài khoản User đã được tạo. Hệ thống sẽ chuyển sang màn hình đăng nhập.',
            },
            strength: {
                veryWeak: 'Rất yếu',
                weak: 'Yếu',
                sufficient: 'Đủ dùng',
                strong: 'Mạnh',
            },
            tenant: {
                loading: 'Đang tải danh sách tenant...',
                loadingHint: 'Đang kiểm tra khả năng tải danh sách tenant từ hệ thống.',
                prompt: 'Chọn tenant cần truy cập',
                loadFailed: 'Không tải được danh sách tenant',
                publicHint: 'Chọn tenant được phép self-signup trong hệ thống.',
                manualHint: 'Danh sách tenant không mở công khai. Nhập trực tiếp mã tenant do admin cung cấp.',
                manualLabel: 'Nhập mã tenant thủ công',
                manualPlaceholder: 'ví dụ: STORE_HN',
            },
        },
        en: {
            page: {
                languageLabel: 'Language',
                languageSelectAria: 'Choose interface language',
                login: {
                    browserTitle: 'Sign In | DWH Operations Console',
                    skipLink: 'Skip the introduction and go to the sign-in form',
                    brandMeta: 'Tenant-based access portal for the retail data platform',
                    heroEyebrow: 'Secure access',
                    heroTitle: 'Secure access to the retail data platform.',
                    heroDescription: 'Sign in to review system status, monitor data, and open dashboards within the branch scope assigned to your account.',
                    statusAria: 'System and security signals',
                    signalSecurityTitle: 'Security posture',
                    signalGatewayLabel: 'Auth Gateway',
                    signalSessionLabel: 'Session policy',
                    signalSessionValue: 'Applied after sign-in',
                    signalScopeTitle: 'Data authorization',
                    signalTenantLabel: 'Branch scope',
                    signalTenantValue: 'Resolved after authentication',
                    signalAccessLabel: 'Access rights',
                    signalAccessValue: 'Based on the assigned role',
                    cardEyebrow: 'Sign in',
                    cardTitle: 'Access the platform',
                    cardDescription: 'Use the assigned account to open dashboards, operational signals, and the data layer related to your branch scope.',
                    usernameLabel: 'Username',
                    usernamePlaceholder: 'example: admin',
                    passwordLabel: 'Password',
                    passwordPlaceholder: 'Enter your password',
                    passwordToggleAria: 'Show or hide password',
                    submit: 'Sign in to the platform',
                    submitLoading: 'Authenticating access...',
                    footerPrompt: 'Need an account?',
                    footerLink: 'Create a User account',
                    footerNote: 'Sign-in is the entry point for data, dashboards, and system signals.',
                },
                register: {
                    browserTitle: 'User Registration | DWH Operations Console',
                    skipLink: 'Skip the introduction and go to the registration form',
                    brandMeta: 'Tenant-based self-registration for the retail data platform',
                    heroEyebrow: 'Access onboarding',
                    heroTitle: 'Create an account to receive data access.',
                    heroDescription: 'This self-signup flow creates a User account with dashboard and data viewing rights within the selected branch scope.',
                    statusAria: 'System and authorization signals',
                    signalAccessTitle: 'Access control',
                    signalGatewayLabel: 'Auth Gateway',
                    signalRoleLabel: 'Role policy',
                    signalRoleValue: 'User is assigned by default during self-signup',
                    signalDataTitle: 'Data readiness',
                    signalDashboardLabel: 'Dashboard scope',
                    signalDashboardValue: 'Based on the selected branch',
                    signalDataLabel: 'Data access',
                    signalDataValue: 'Activated after authentication',
                    cardEyebrow: 'Registration',
                    cardTitle: 'Create a User account',
                    cardDescription: 'Use the branch code provided by the administrator or select a branch that supports self-signup. Data viewing rights will be assigned automatically by branch policy.',
                    usernameLabel: 'Username',
                    usernamePlaceholder: 'example: user_hn',
                    passwordLabel: 'Password',
                    passwordPlaceholder: 'At least 6 characters',
                    passwordToggleAria: 'Show or hide password',
                    confirmLabel: 'Confirm password',
                    confirmPlaceholder: 'Enter the password again',
                    confirmToggleAria: 'Show or hide confirmation password',
                    tenantLabel: 'Branch',
                    scopeEyebrow: 'Default scope',
                    scopePill: 'By branch',
                    scopeTitle: 'User',
                    scopeDescription: 'Self-signup grants dashboard and data viewing rights only within the selected branch. Any extended rights will be managed later by an administrator.',
                    submit: 'Create User account',
                    submitLoading: 'Provisioning access...',
                    footerPrompt: 'Already have an account?',
                    footerLink: 'Back to sign in',
                    footerNote: 'Self-signup applies only to the User access layer of the platform.',
                },
            },
            trust: {
                checking: {
                    label: 'Checking',
                    loginMessage: 'Checking the authentication layer before allowing sign-in.',
                    registerMessage: 'Checking the authentication layer before creating a new account.',
                },
                ok: {
                    label: 'Responding',
                    loginMessage: 'The authentication layer is responding. You can continue signing in.',
                    registerMessage: 'The authentication layer is responding. You can continue creating the account.',
                },
                error: {
                    label: 'Unavailable',
                    loginMessage: 'The authentication layer is not responding. Verify the service before continuing sign-in.',
                    registerMessage: 'The authentication layer is not responding. Verify the service before continuing registration.',
                },
            },
            validation: {
                usernameRequired: 'Enter the username.',
                passwordRequired: 'Enter the password.',
                invalidUsername: 'Use letters, numbers, or underscores only.',
                passwordTooShort: 'The password must contain at least 6 characters.',
                confirmMismatch: 'The confirmation password does not match.',
                tenantRequired: 'Select or enter a branch code.',
                loginInvalid: 'Invalid sign-in credentials. Check the account and try again.',
                loginForbidden: 'The account or branch scope is locked. Contact an administrator for review.',
                loginFailed: 'Unable to sign in. Check the account and try again.',
                loginService: 'Unable to connect to the authentication layer. Check the service and try again.',
                registerFailed: 'Unable to create the account. Review the data and try again.',
                registerConflict: 'The username already exists. Choose a different username.',
                registerService: 'Unable to connect to the registration service. Check the Auth Gateway and try again.',
                registerSuccess: 'The User account has been created. The system will redirect to the sign-in screen.',
            },
            strength: {
                veryWeak: 'Very weak',
                weak: 'Weak',
                sufficient: 'Acceptable',
                strong: 'Strong',
            },
            tenant: {
                loading: 'Loading available branches...',
                loadingHint: 'Checking whether the platform can load the branch list.',
                prompt: 'Select the branch to access',
                loadFailed: 'Unable to load the branch list',
                publicHint: 'Select a branch that is available for self-signup in the platform.',
                manualHint: 'The branch list is not exposed publicly. Enter the branch code provided by the administrator.',
                manualLabel: 'Enter the branch code manually',
                manualPlaceholder: 'example: STORE_HN',
            },
        },
    };

    const i18n = window.DWHI18n.createPageI18n({
        copy: COPY,
        documentTitleKey: `page.${pageType}.browserTitle`,
        languageSelect: byId('languageSelect'),
    });

    const t = (path, params) => i18n.t(path, params);

    let authTrustState = 'checking';
    let tenantLoadState = 'loading';
    let tenantOptions = [];

    function showAlert(element, message = '', tone = 'danger', translationKey = '', params = {}) {
        if (!element) return;
        element.classList.remove('alert--danger', 'alert--success');
        element.classList.add(tone === 'success' ? 'alert--success' : 'alert--danger');
        element.textContent = translationKey ? t(translationKey, params) : message;
        element.classList.add('is-visible');
        element.classList.remove('is-hidden');
        i18n.setRuntimeCopy(element, translationKey, params);
    }

    function hideAlert(element) {
        if (!element) return;
        element.textContent = '';
        element.classList.remove('is-visible');
        element.classList.add('is-hidden');
        i18n.setRuntimeCopy(element);
    }

    function setFieldError(id, translationKey = '', params = {}) {
        const element = byId(id);
        if (!element) return;
        element.textContent = translationKey ? t(translationKey, params) : '';
        i18n.setRuntimeCopy(element, translationKey, params);

        const inputId = element.dataset.input;
        if (!inputId) return;

        let input = byId(inputId);
        if (inputId === 'tenant_id' && input && input.disabled) {
            input = byId('tenant_id_manual') || input;
        }
        if (input) {
            input.setAttribute('aria-invalid', translationKey ? 'true' : 'false');
        }
    }

    function togglePasswordVisibility(button) {
        const inputId = button.getAttribute('data-target');
        const input = byId(inputId);
        if (!input) return;
        const nextType = input.type === 'password' ? 'text' : 'password';
        input.type = nextType;
        button.setAttribute('aria-pressed', String(nextType === 'text'));
    }

    function bindPasswordToggles() {
        document.querySelectorAll('[data-toggle-password]').forEach((button) => {
            button.addEventListener('click', () => togglePasswordVisibility(button));
        });
    }

    function setButtonLoading(button, isLoading, labelKey) {
        if (!button) return;
        button.disabled = isLoading;
        const label = button.querySelector('.button__label');
        if (label) {
            label.textContent = isLoading ? t(labelKey) : t(`page.${pageType}.submit`);
        }
    }

    function applyAuthTrustState(state) {
        authTrustState = state;

        document.querySelectorAll('[data-auth-health-label]').forEach((element) => {
            element.textContent = t(`trust.${state}.label`);
            element.dataset.state = state;
        });

        document.querySelectorAll('[data-auth-trust-message]').forEach((element) => {
            element.textContent = t(`trust.${state}.${pageType}Message`);
        });

        document.querySelectorAll('[data-auth-trust-dot]').forEach((element) => {
            element.classList.remove('is-checking', 'is-live', 'is-danger');
            element.classList.add(state === 'ok' ? 'is-live' : state === 'error' ? 'is-danger' : 'is-checking');
        });
    }

    async function hydrateAuthTrust() {
        if (!document.querySelector('[data-auth-health-label]')) return;

        applyAuthTrustState('checking');
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            applyAuthTrustState(data.api === 'ok' ? 'ok' : 'error');
        } catch (error) {
            applyAuthTrustState('error');
        }
    }

    function updatePasswordStrength(value = byId('password')?.value || '') {
        const container = byId('passwordStrength');
        if (!container) return;

        if (!value) {
            container.classList.remove('is-visible');
            delete container.dataset.level;
            return;
        }

        let score = 0;
        if (value.length >= 6) score += 1;
        if (value.length >= 10) score += 1;
        if (/[A-Z]/.test(value)) score += 1;
        if (/[0-9]/.test(value) || /[^a-zA-Z0-9]/.test(value)) score += 1;

        const level = Math.max(score, 1);
        const labelKey = level === 1
            ? 'strength.veryWeak'
            : level === 2
                ? 'strength.weak'
                : level === 3
                    ? 'strength.sufficient'
                    : 'strength.strong';

        container.dataset.level = String(level);
        container.querySelector('.password-strength__label').textContent = t(labelKey);
        container.classList.add('is-visible');
    }

    function renderTenantOptions() {
        const select = byId('tenant_id');
        const manualWrapper = byId('tenantManualWrapper');
        const manualInput = byId('tenant_id_manual');
        const tenantHint = byId('tenantHint');
        if (!select) return;

        const currentSelectValue = select.value;

        if (tenantLoadState === 'list' && tenantOptions.length) {
            select.innerHTML = '';
            select.appendChild(new Option(t('tenant.prompt'), ''));
            tenantOptions.forEach((tenant) => {
                select.appendChild(new Option(`${tenant.tenant_id} — ${tenant.tenant_name}`, tenant.tenant_id));
            });
            select.disabled = false;
            select.value = tenantOptions.some((tenant) => tenant.tenant_id === currentSelectValue) ? currentSelectValue : '';
            manualWrapper?.classList.remove('is-visible');
            if (tenantHint) tenantHint.textContent = t('tenant.publicHint');
            return;
        }

        select.innerHTML = '';
        select.appendChild(new Option(
            tenantLoadState === 'loading' ? t('tenant.loading') : t('tenant.loadFailed'),
            ''
        ));
        select.disabled = true;
        manualWrapper?.classList.add('is-visible');
        if (tenantHint) {
            tenantHint.textContent = tenantLoadState === 'loading' ? t('tenant.loadingHint') : t('tenant.manualHint');
        }
        if (manualInput && !manualInput.placeholder) {
            manualInput.placeholder = t('tenant.manualPlaceholder');
        }
    }

    async function populateTenantOptions() {
        const select = byId('tenant_id');
        if (!select) return;

        tenantLoadState = 'loading';
        renderTenantOptions();

        try {
            const response = await fetch('/api/tenants');
            if (!response.ok) throw new Error('Unauthenticated');
            const data = await response.json();
            tenantOptions = (data.tenants || []).filter((tenant) => tenant.is_active);
            tenantLoadState = tenantOptions.length ? 'list' : 'manual';
        } catch (error) {
            tenantOptions = [];
            tenantLoadState = 'manual';
        }

        renderTenantOptions();
    }

    async function handleLoginSubmit(event) {
        event.preventDefault();

        const usernameInput = byId('username');
        const passwordInput = byId('password');
        const button = byId('loginBtn');
        const alertBox = byId('loginAlert');

        hideAlert(alertBox);
        setFieldError('usernameError');
        setFieldError('passwordError');

        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        if (!username) {
            setFieldError('usernameError', 'validation.usernameRequired');
        }
        if (!password) {
            setFieldError('passwordError', 'validation.passwordRequired');
        }
        if (!username || !password) return;

        setButtonLoading(button, true, 'page.login.submitLoading');

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });
            const data = await response.json();

            if (!response.ok || !data.success) {
                const translationKey = response.status === 401
                    ? 'validation.loginInvalid'
                    : response.status === 403
                        ? 'validation.loginForbidden'
                        : 'validation.loginFailed';
                showAlert(alertBox, '', 'danger', translationKey);
                return;
            }

            window.location.href = '/dashboard';
        } catch (error) {
            showAlert(alertBox, '', 'danger', 'validation.loginService');
        } finally {
            setButtonLoading(button, false, 'page.login.submit');
        }
    }

    async function handleRegisterSubmit(event) {
        event.preventDefault();

        const alertBox = byId('registerAlert');
        const button = byId('registerBtn');
        hideAlert(alertBox);

        ['usernameError', 'passwordError', 'confirmError', 'tenantError'].forEach((id) => setFieldError(id));

        const username = byId('username').value.trim();
        const password = byId('password').value;
        const confirmPassword = byId('confirmPassword').value;
        const tenantSelect = byId('tenant_id');
        const tenantManual = byId('tenant_id_manual');
        const roleInput = byId('role');
        const role = roleInput ? roleInput.value : 'user';
        const tenantId = tenantSelect.disabled ? tenantManual.value.trim() : tenantSelect.value;

        let isValid = true;

        if (!username) {
            setFieldError('usernameError', 'validation.usernameRequired');
            isValid = false;
        } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            setFieldError('usernameError', 'validation.invalidUsername');
            isValid = false;
        }

        if (!password) {
            setFieldError('passwordError', 'validation.passwordRequired');
            isValid = false;
        } else if (password.length < 6) {
            setFieldError('passwordError', 'validation.passwordTooShort');
            isValid = false;
        }

        if (confirmPassword !== password) {
            setFieldError('confirmError', 'validation.confirmMismatch');
            isValid = false;
        }

        if (!tenantId) {
            setFieldError('tenantError', 'validation.tenantRequired');
            isValid = false;
        }

        if (!isValid) return;

        setButtonLoading(button, true, 'page.register.submitLoading');

        try {
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password, role, tenant_id: tenantId }),
            });
            const data = await response.json();

            if (!response.ok || !data.success) {
                const translationKey = response.status === 409
                    ? 'validation.registerConflict'
                    : 'validation.registerFailed';
                showAlert(alertBox, '', 'danger', translationKey);
                return;
            }

            showAlert(alertBox, '', 'success', 'validation.registerSuccess');
            window.setTimeout(() => {
                window.location.href = '/login';
            }, 1100);
        } catch (error) {
            showAlert(alertBox, '', 'danger', 'validation.registerService');
        } finally {
            setButtonLoading(button, false, 'page.register.submit');
        }
    }

    function reapplyLocalizedState() {
        i18n.applyRuntimeCopy();
        applyAuthTrustState(authTrustState);
        if (pageType === 'register') {
            renderTenantOptions();
            updatePasswordStrength();
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        bindPasswordToggles();
        i18n.onChange(reapplyLocalizedState);
        reapplyLocalizedState();
        hydrateAuthTrust();

        byId('loginForm')?.addEventListener('submit', handleLoginSubmit);

        if (pageType === 'register') {
            populateTenantOptions();
            byId('password')?.addEventListener('input', (event) => updatePasswordStrength(event.target.value));
            byId('registerForm')?.addEventListener('submit', handleRegisterSubmit);
        }
    });
})();
