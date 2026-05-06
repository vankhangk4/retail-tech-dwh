function showAlert(element, message, tone = 'danger') {
    if (!element) return;
    element.classList.remove('alert--danger', 'alert--success');
    element.classList.add(tone === 'success' ? 'alert--success' : 'alert--danger');
    element.textContent = message;
    element.classList.add('is-visible');
}

function hideAlert(element) {
    if (!element) return;
    element.textContent = '';
    element.classList.remove('is-visible');
}

function setFieldError(id, message) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = message || '';
    const inputId = el.dataset.input;
    if (inputId) {
        let input = document.getElementById(inputId);
        if (inputId === 'tenant_id' && input && input.disabled) {
            input = document.getElementById('tenant_id_manual') || input;
        }
        if (input) {
            input.setAttribute('aria-invalid', message ? 'true' : 'false');
        }
    }
}

function togglePasswordVisibility(button) {
    const inputId = button.getAttribute('data-target');
    const input = document.getElementById(inputId);
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

async function handleLoginSubmit(event) {
    event.preventDefault();
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const button = document.getElementById('loginBtn');
    const alertBox = document.getElementById('loginAlert');

    hideAlert(alertBox);
    setFieldError('usernameError', '');
    setFieldError('passwordError', '');

    const username = usernameInput.value.trim();
    const password = passwordInput.value;

    if (!username) {
        setFieldError('usernameError', 'Vui lòng nhập tên đăng nhập.');
    }
    if (!password) {
        setFieldError('passwordError', 'Vui lòng nhập mật khẩu.');
    }
    if (!username || !password) return;

    button.disabled = true;
    button.querySelector('.button__label').textContent = 'Đang xác thực truy cập...';

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            showAlert(alertBox, data.message || 'Không thể đăng nhập. Kiểm tra lại tài khoản và thử lại.');
            return;
        }
        window.location.href = '/dashboard';
    } catch (error) {
        showAlert(alertBox, 'Không kết nối được lớp xác thực. Kiểm tra dịch vụ rồi thử lại.');
    } finally {
        button.disabled = false;
        button.querySelector('.button__label').textContent = 'Đăng nhập vào hệ thống';
    }
}

function updatePasswordStrength(value) {
    const container = document.getElementById('passwordStrength');
    if (!container) return;

    if (!value) {
        container.classList.remove('is-visible');
        return;
    }

    let score = 0;
    if (value.length >= 6) score += 1;
    if (value.length >= 10) score += 1;
    if (/[A-Z]/.test(value)) score += 1;
    if (/[0-9]/.test(value) || /[^a-zA-Z0-9]/.test(value)) score += 1;

    const palette = ['var(--danger)', 'var(--warning)', 'var(--warning)', 'var(--success)'];
    const labels = ['Rất yếu', 'Yếu', 'Đủ dùng', 'Mạnh'];
    const bars = container.querySelectorAll('[data-strength-bar]');
    bars.forEach((bar, index) => {
        bar.style.background = index < score ? palette[Math.max(score - 1, 0)] : 'var(--bg-subtle)';
    });
    container.querySelector('.password-strength__label').textContent = labels[Math.max(score - 1, 0)];
    container.classList.add('is-visible');
}

async function populateTenantOptions() {
    const select = document.getElementById('tenant_id');
    const manualWrapper = document.getElementById('tenantManualWrapper');
    const tenantHint = document.getElementById('tenantHint');
    if (!select) return;

    try {
        const response = await fetch('/api/tenants');
        if (!response.ok) throw new Error('Unauthenticated');
        const data = await response.json();
        const tenants = (data.tenants || []).filter((tenant) => tenant.is_active);
        if (!tenants.length) throw new Error('No tenants');

        select.innerHTML = '<option value="">Chọn tenant cần truy cập</option>' +
            tenants.map((tenant) => (
                `<option value="${tenant.tenant_id}">${tenant.tenant_id} — ${tenant.tenant_name}</option>`
            )).join('');
        select.disabled = false;
        if (manualWrapper) manualWrapper.classList.remove('is-visible');
        if (tenantHint) tenantHint.textContent = 'Chọn tenant được phép self-signup trong hệ thống.';
    } catch (error) {
        select.innerHTML = '<option value="">Không tải được danh sách tenant</option>';
        select.disabled = true;
        if (manualWrapper) manualWrapper.classList.add('is-visible');
        if (tenantHint) {
            tenantHint.textContent = 'Danh sách tenant không mở công khai. Nhập trực tiếp mã tenant do admin cung cấp.';
        }
    }
}

async function handleRegisterSubmit(event) {
    event.preventDefault();
    const alertBox = document.getElementById('registerAlert');
    const button = document.getElementById('registerBtn');
    hideAlert(alertBox);

    ['usernameError', 'passwordError', 'confirmError', 'tenantError'].forEach((id) => setFieldError(id, ''));

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const tenantSelect = document.getElementById('tenant_id');
    const tenantManual = document.getElementById('tenant_id_manual');
    const roleInput = document.getElementById('role');
    const role = roleInput ? roleInput.value : 'user';
    const tenantId = tenantSelect.disabled ? tenantManual.value.trim() : tenantSelect.value;

    let valid = true;

    if (!username) {
        setFieldError('usernameError', 'Vui lòng nhập tên đăng nhập.');
        valid = false;
    } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        setFieldError('usernameError', 'Chỉ dùng chữ cái, số hoặc dấu gạch dưới.');
        valid = false;
    }

    if (password.length < 6) {
        setFieldError('passwordError', 'Mật khẩu cần ít nhất 6 ký tự.');
        valid = false;
    }

    if (confirmPassword !== password) {
        setFieldError('confirmError', 'Mật khẩu xác nhận chưa khớp.');
        valid = false;
    }

    if (!tenantId) {
        setFieldError('tenantError', 'Vui lòng chọn hoặc nhập mã tenant.');
        valid = false;
    }

    if (!valid) return;

    button.disabled = true;
    button.querySelector('.button__label').textContent = 'Đang cấp quyền truy cập...';

    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role, tenant_id: tenantId }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            showAlert(alertBox, data.message || 'Không thể tạo tài khoản. Kiểm tra dữ liệu rồi thử lại.');
            return;
        }
        showAlert(alertBox, data.message || 'Tài khoản User đã được tạo. Chuyển sang đăng nhập...', 'success');
        setTimeout(() => {
            window.location.href = '/login';
        }, 1100);
    } catch (error) {
        showAlert(alertBox, 'Không kết nối được dịch vụ đăng ký. Kiểm tra Auth Gateway rồi thử lại.');
    } finally {
        button.disabled = false;
        button.querySelector('.button__label').textContent = 'Tạo tài khoản User';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    bindPasswordToggles();

    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLoginSubmit);
    }

    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        populateTenantOptions();
        registerForm.addEventListener('submit', handleRegisterSubmit);
        const passwordInput = document.getElementById('password');
        if (passwordInput) {
            passwordInput.addEventListener('input', (event) => updatePasswordStrength(event.target.value));
        }
    }
});
