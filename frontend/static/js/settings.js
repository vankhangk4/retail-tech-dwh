// ============================================================
// settings.js — Trang Cài đặt & Hồ sơ người dùng
// ============================================================

(function () {
    'use strict';

    // ── Health check / logout (shared with dashboard) ────────
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await fetch('/api/logout', { method: 'POST' });
            } finally {
                window.location.href = '/login';
            }
        });
    }

    fetch('/api/health').then(r => r.json()).then(data => {
        const el = document.getElementById('healthIndicator');
        if (!el) return;
        const ok = data.api === 'ok';
        el.innerHTML = `<span class="status-pill ${ok ? 'tone-success' : 'tone-danger'}">${ok ? 'API ổn định' : 'API cần kiểm tra'}</span>`;
    }).catch(() => {});

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
    const tabBtns   = document.querySelectorAll('.settings-tab-btn');
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
            // Load login history lazily when security tab opens
            if (target === 'security' && !historyLoaded) {
                loadLoginHistory();
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

    // ── Password toggle (show/hide) ───────────────────────────
    document.querySelectorAll('[data-toggle-password]').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.dataset.target;
            const input    = document.getElementById(targetId);
            if (!input) return;
            const isHidden = input.type === 'password';
            input.type = isHidden ? 'text' : 'password';
            btn.setAttribute('aria-pressed', String(isHidden));
        });
    });

    // ── Alert helpers ─────────────────────────────────────────
    function showAlert(el, msg, type = 'danger', timeoutMs = 0) {
        if (!el) return;
        window.clearTimeout(el._hideTimer);
        el.textContent = msg;
        el.className = `alert alert--${type}`;
        el.classList.remove('is-hidden');
        el.classList.add('is-visible');
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
    }

    // ── Button loading state ──────────────────────────────────
    function setBtnLoading(btn, loading, label) {
        if (!btn) return;
        btn.disabled = loading;
        const labelEl = btn.querySelector('.button__label');
        if (labelEl) labelEl.textContent = loading ? 'Đang xử lý...' : label;
    }

    // ══════════════════════════════════════════════════════════
    // Load profile on page open
    // ══════════════════════════════════════════════════════════
    let profileCache = null;

    async function loadProfile() {
        try {
            const r = await fetch('/api/me/profile');
            if (!r.ok) return;
            const data = await r.json();
            profileCache = data;
            populateProfile(data);
        } catch (error) {
            showAlert(profileErrorAlert, 'Không tải được hồ sơ tài khoản. Vui lòng thử tải lại trang.');
        }
    }

    function populateProfile(data) {
        const headerUsername = document.getElementById('headerUsername');
        if (headerUsername) headerUsername.textContent = data.username || '—';

        const identityUsername = document.getElementById('identityUsername');
        if (identityUsername) identityUsername.textContent = data.username || '—';

        const identityCreatedAt = document.getElementById('identityCreatedAt');
        if (identityCreatedAt) identityCreatedAt.textContent = data.created_at || '—';

        const displayName = document.getElementById('displayName');
        if (displayName) displayName.value = data.display_name || '';

        const email = document.getElementById('email');
        if (email) email.value = data.email || '';

        const phone = document.getElementById('phone');
        if (phone) phone.value = data.phone || '';

        // Avatar
        if (data.avatar_data) {
            setAvatarImage(data.avatar_data, data.username || '?');
        } else {
            clearAvatarImage(data.username || '?');
        }

        // Update sidebar avatar initials with display_name if available
        if (sidebarAvatarInitial && (data.display_name || data.username)) {
            const name = data.display_name || data.username;
            sidebarAvatarInitial.textContent = name[0].toUpperCase();
        }
    }

    // ══════════════════════════════════════════════════════════
    // Avatar handling
    // ══════════════════════════════════════════════════════════
    const avatarInput     = document.getElementById('avatarInput');
    const avatarImg       = document.getElementById('avatarImg');
    const avatarInitials  = document.getElementById('avatarInitials');
    const avatarRemoveBtn = document.getElementById('avatarRemoveBtn');
    const avatarSuccessMsg = document.getElementById('avatarSuccessMsg');
    const avatarErrorMsg   = document.getElementById('avatarErrorMsg');
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

    // Resize image to max 200×200 using Canvas, return base64 JPEG
    function resizeImage(file, maxDim = 200) {
        return new Promise((resolve, reject) => {
            if (file.size > 8_000_000) {
                reject(new Error('Ảnh quá lớn — tối đa 8MB trước khi nén'));
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
                    canvas.width  = w;
                    canvas.height = h;
                    const ctx2 = canvas.getContext('2d');
                    ctx2.drawImage(img, 0, 0, w, h);
                    resolve(canvas.toDataURL('image/jpeg', 0.88));
                };
                img.onerror = () => reject(new Error('Không đọc được file ảnh'));
                img.src = evt.target.result;
            };
            reader.onerror = () => reject(new Error('Không đọc được file'));
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
                if (!r.ok) throw new Error(data.detail || data.error || 'Lỗi tải ảnh');

                const username = profileCache?.username || '?';
                setAvatarImage(dataUrl, username);

                showAlert(avatarSuccessMsg, 'Ảnh đại diện đã được cập nhật.', 'success', 4000);
            } catch (err) {
                showAlert(avatarErrorMsg, err.message || 'Lỗi tải ảnh lên');
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
                if (!r.ok) throw new Error('Lỗi xóa ảnh');
                const username = profileCache?.username || '?';
                clearAvatarImage(username);
                showAlert(avatarSuccessMsg, 'Đã xóa ảnh đại diện.', 'success', 3000);
            } catch (err) {
                showAlert(avatarErrorMsg, 'Không xóa được ảnh đại diện');
            }
        });
    }

    // ══════════════════════════════════════════════════════════
    // Profile form submit
    // ══════════════════════════════════════════════════════════
    const profileForm         = document.getElementById('profileForm');
    const profileErrorAlert   = document.getElementById('profileErrorAlert');
    const profileSuccessAlert = document.getElementById('profileSuccessAlert');
    const profileSaveBtn      = document.getElementById('profileSaveBtn');
    const profileResetBtn     = document.getElementById('profileResetBtn');

    if (profileForm) {
        profileForm.addEventListener('submit', async e => {
            e.preventDefault();
            hideAlert(profileErrorAlert);
            hideAlert(profileSuccessAlert);
            setBtnLoading(profileSaveBtn, true, 'Lưu thay đổi');

            const body = {
                display_name: document.getElementById('displayName')?.value.trim() || null,
                email:        document.getElementById('email')?.value.trim() || null,
                phone:        document.getElementById('phone')?.value.trim() || null,
            };

            try {
                const r = await fetch('/api/me/profile', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || data.error || 'Lỗi cập nhật');

                if (profileCache) {
                    profileCache.display_name = body.display_name;
                    profileCache.email        = body.email;
                    profileCache.phone        = body.phone;
                }

                // Update sidebar initial if display_name changed
                const name = body.display_name || profileCache?.username || '?';
                if (sidebarAvatarInitial && sidebarAvatarImg?.classList.contains('is-hidden')) {
                    sidebarAvatarInitial.textContent = name[0].toUpperCase();
                }
                if (avatarInitials && avatarImg?.classList.contains('is-hidden')) {
                    avatarInitials.textContent = name[0].toUpperCase();
                }

                showAlert(profileSuccessAlert, 'Hồ sơ đã được cập nhật thành công.', 'success');
            } catch (err) {
                showAlert(profileErrorAlert, err.message || 'Lỗi cập nhật hồ sơ');
            } finally {
                setBtnLoading(profileSaveBtn, false, 'Lưu thay đổi');
            }
        });
    }

    if (profileResetBtn) {
        profileResetBtn.addEventListener('click', () => {
            if (!profileCache) return;
            document.getElementById('displayName').value = profileCache.display_name || '';
            document.getElementById('email').value        = profileCache.email || '';
            document.getElementById('phone').value        = profileCache.phone || '';
            hideAlert(profileErrorAlert);
            hideAlert(profileSuccessAlert);
        });
    }

    // ══════════════════════════════════════════════════════════
    // Password strength meter
    // ══════════════════════════════════════════════════════════
    const newPasswordInput  = document.getElementById('newPassword');
    const pwdStrengthEl     = document.getElementById('pwdStrength');
    const pwdStrengthLabel  = document.getElementById('pwdStrengthLabel');

    function scorePassword(pwd) {
        let score = 0;
        if (pwd.length >= 6)  score++;
        if (pwd.length >= 10) score++;
        if (/[A-Z]/.test(pwd) && /[a-z]/.test(pwd)) score++;
        if (/[0-9]/.test(pwd)) score++;
        if (/[^A-Za-z0-9]/.test(pwd)) score++;
        return Math.min(Math.max(Math.ceil(score * 4 / 5), 1), 4);
    }

    const strengthLabels = ['', 'Yếu', 'Trung bình', 'Khá mạnh', 'Mạnh'];

    if (newPasswordInput && pwdStrengthEl) {
        newPasswordInput.addEventListener('input', () => {
            const val = newPasswordInput.value;
            if (!val) {
                pwdStrengthEl.hidden = true;
                return;
            }
            pwdStrengthEl.hidden = false;
            const level = scorePassword(val);
            pwdStrengthEl.dataset.level = level;
            if (pwdStrengthLabel) pwdStrengthLabel.textContent = strengthLabels[level];
        });
    }

    // ══════════════════════════════════════════════════════════
    // Password form submit
    // ══════════════════════════════════════════════════════════
    const passwordForm         = document.getElementById('passwordForm');
    const passwordErrorAlert   = document.getElementById('passwordErrorAlert');
    const passwordSuccessAlert = document.getElementById('passwordSuccessAlert');
    const passwordSaveBtn      = document.getElementById('passwordSaveBtn');
    const confirmPasswordError = document.getElementById('confirmPasswordError');

    if (passwordForm) {
        passwordForm.addEventListener('submit', async e => {
            e.preventDefault();
            hideAlert(passwordErrorAlert);
            hideAlert(passwordSuccessAlert);
            if (confirmPasswordError) confirmPasswordError.textContent = '';

            const currentPwd = document.getElementById('currentPassword')?.value || '';
            const newPwd     = document.getElementById('newPassword')?.value || '';
            const confirmPwd = document.getElementById('confirmPassword')?.value || '';

            if (newPwd !== confirmPwd) {
                if (confirmPasswordError) confirmPasswordError.textContent = 'Mật khẩu xác nhận không khớp';
                return;
            }
            if (newPwd.length < 6) {
                showAlert(passwordErrorAlert, 'Mật khẩu mới phải có ít nhất 6 ký tự');
                return;
            }

            setBtnLoading(passwordSaveBtn, true, 'Đổi mật khẩu');

            try {
                const r = await fetch('/api/me/password', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ current_password: currentPwd, new_password: newPwd }),
                });
                const data = await r.json();
                if (!r.ok) throw new Error(data.detail || data.error || 'Lỗi đổi mật khẩu');

                passwordForm.reset();
                if (pwdStrengthEl) pwdStrengthEl.hidden = true;
                showAlert(passwordSuccessAlert, 'Mật khẩu đã được đổi thành công. Hãy đăng nhập lại nếu được yêu cầu.', 'success');
            } catch (err) {
                showAlert(passwordErrorAlert, err.message || 'Lỗi đổi mật khẩu');
            } finally {
                setBtnLoading(passwordSaveBtn, false, 'Đổi mật khẩu');
            }
        });
    }

    // ══════════════════════════════════════════════════════════
    // Login history
    // ══════════════════════════════════════════════════════════
    let historyLoaded = false;
    const loginHistoryBody  = document.getElementById('loginHistoryBody');
    const refreshHistoryBtn = document.getElementById('refreshHistoryBtn');

    function parseUserAgent(ua) {
        if (!ua) return '—';
        // Extract browser and OS in a concise form
        let browser = 'Không rõ';
        let os      = '';

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

        return os ? `${browser} — ${os}` : browser;
    }

    async function loadLoginHistory() {
        if (!loginHistoryBody) return;
        loginHistoryBody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><span class="text-faint">Đang tải...</span></div></td></tr>`;

        try {
            const r = await fetch('/api/me/login-history');
            const data = await r.json();
            const items = data.items || [];

            if (items.length === 0) {
                loginHistoryBody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><strong>Chưa có lịch sử</strong><span>Chưa ghi nhận phiên đăng nhập nào.</span></div></td></tr>`;
                historyLoaded = true;
                return;
            }

            loginHistoryBody.innerHTML = items.map((item, idx) => {
                const isSuccess = item.status === 'success';
                const pillClass = isSuccess ? 'tone-live' : 'tone-danger';
                const pillLabel = isSuccess ? 'Thành công' : 'Thất bại';
                const isCurrent = idx === 0 ? '<span class="status-pill tone-neutral login-session-pill">Phiên này</span>' : '';
                return `
                    <tr>
                        <td data-label="Thời gian">
                            <span class="login-time">${escHtml(item.login_at)}</span>
                            ${isCurrent}
                        </td>
                        <td data-label="Địa chỉ IP">
                            <span class="login-ip">${escHtml(item.ip_address || '—')}</span>
                        </td>
                        <td data-label="Trình duyệt">
                            <span class="ua-text" title="${escHtml(item.user_agent || '')}">
                                ${escHtml(parseUserAgent(item.user_agent))}
                            </span>
                        </td>
                        <td data-label="Trạng thái">
                            <span class="status-pill ${pillClass}">${pillLabel}</span>
                        </td>
                    </tr>`;
            }).join('');

            historyLoaded = true;
        } catch (err) {
            loginHistoryBody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><span class="tone-danger">Không tải được lịch sử đăng nhập</span></div></td></tr>`;
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
            historyLoaded = false;
            loadLoginHistory();
        });
    }

    // ── Sidebar nav links — store page target in sessionStorage ──
    document.querySelectorAll('[data-navto]').forEach(link => {
        link.addEventListener('click', e => {
            const page = link.dataset.navto;
            if (page) sessionStorage.setItem('dashboardPage', page);
        });
    });

    // ── Init ────────────────────────────────────────────────
    loadProfile();
}());
