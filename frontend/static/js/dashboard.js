const APP_CONTEXT = JSON.parse(document.getElementById('app-context').textContent);

const DASHBOARD_MAP = {
    revenue: { id: 1, label: 'Doanh thu' },
    products: { id: 2, label: 'Sản phẩm' },
    inventory: { id: 3, label: 'Tồn kho' },
    customers: { id: 4, label: 'Khách hàng' },
    employees: { id: 5, label: 'Nhân viên' },
};

const appState = {
    health: 'checking',
    kpi: {},
    tenants: [],
    users: [],
    etlLogs: [],
};

function byId(id) {
    return document.getElementById(id);
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function formatCurrency(value) {
    return `${new Intl.NumberFormat('vi-VN').format(Number(value || 0))} VNĐ`;
}

function formatInteger(value) {
    return new Intl.NumberFormat('vi-VN').format(Number(value || 0));
}

function formatDateTime(value) {
    if (!value) return '—';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '—';
    return date.toLocaleString('vi-VN');
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

function authFetch(url, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (APP_CONTEXT.accessToken) {
        headers.Authorization = `Bearer ${APP_CONTEXT.accessToken}`;
    }
    return fetch(url, { ...options, headers });
}

function setSidebarState() {
    if (window.innerWidth <= 1024) {
        document.body.classList.remove('sidebar-collapsed');
    }
}

function toggleSidebar() {
    if (window.innerWidth <= 1024) {
        document.body.classList.toggle('sidebar-open');
        return;
    }
    document.body.classList.toggle('sidebar-collapsed');
}

function closeSidebarOnMobile() {
    if (window.innerWidth <= 1024) {
        document.body.classList.remove('sidebar-open');
    }
}

function updatePageChrome(page) {
    const target = document.querySelector(`.page[data-page="${page}"]`);
    if (!target) return;
    byId('pageTitle').textContent = target.dataset.pageTitle || target.querySelector('h2')?.textContent || 'Điều hành';
    byId('pageSubtitle').textContent = target.dataset.pageSubtitle || '';
    byId('pageEyebrow').textContent = target.dataset.pageEyebrow || 'Điều hành';
}

function navigateTo(page) {
    document.querySelectorAll('.nav-link').forEach((link) => {
        link.classList.toggle('is-active', link.dataset.page === page);
    });
    document.querySelectorAll('.page').forEach((section) => {
        section.classList.toggle('is-active', section.dataset.page === page);
    });
    updatePageChrome(page);
    closeSidebarOnMobile();

    if (DASHBOARD_MAP[page]) {
        loadSupersetIframe(page);
    }
}

function bindNavigation() {
    document.querySelectorAll('.nav-link').forEach((link) => {
        link.addEventListener('click', () => navigateTo(link.dataset.page));
    });

    document.querySelectorAll('[data-open-page]').forEach((button) => {
        button.addEventListener('click', () => navigateTo(button.dataset.openPage));
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
            if (message.switchboardAction === 'error') {
                console.error('Superset embedded token error:', message.error);
            }
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

async function loadSupersetIframe(page) {
    const config = DASHBOARD_MAP[page];
    const iframe = byId(`iframe-${page}`);
    if (!config || !iframe) return;

    iframe.src = 'about:blank';
    iframe.removeAttribute('srcdoc');
    const frameState = byId(`frameState-${page}`);
    if (frameState) frameState.textContent = 'Đang xin dashboard token và dựng phiên nhúng.';

    try {
        const response = await fetch(`/api/dashboard-token?dashboard_id=${config.id}`);
        if (!response.ok) throw new Error('Token error');
        const data = await response.json();
        renderEmbeddedDashboard(iframe, data);
        if (frameState) frameState.textContent = 'Đang hiển thị dashboard nhúng qua Superset.';
    } catch (error) {
        console.error('Dashboard token error:', error);
        iframe.srcdoc = '<p style="padding:20px;font:16px system-ui;color:#b42318;">Không lấy được dashboard token. Vui lòng đăng nhập lại hoặc kiểm tra dịch vụ Superset.</p>';
        if (frameState) frameState.textContent = 'Không thể dựng dashboard nhúng ở thời điểm này.';
    }
}

function toggleModal(id, visible) {
    const modal = byId(id);
    if (!modal) return;
    modal.classList.toggle('is-visible', visible);
}

async function openSupersetDashboard(dashboardId) {
    byId('modalTitle').textContent = 'Phòng phân tích tập trung';
    const iframe = byId('modalIframe');
    iframe.onload = null;
    iframe.src = 'about:blank';

    try {
        const response = await fetch(`/api/dashboard-token?dashboard_id=${dashboardId}`);
        if (!response.ok) throw new Error('Token error');
        const data = await response.json();
        renderEmbeddedDashboard(iframe, data);
        toggleModal('modalOverlay', true);
    } catch (error) {
        alert('Không lấy được dashboard token. Vui lòng đăng nhập lại.');
    }
}

function closeModal() {
    toggleModal('modalOverlay', false);
    byId('modalIframe').src = 'about:blank';
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
    const liveStatus = appState.health === 'ok';

    indicator.innerHTML = `
        <span class="status-pill ${liveStatus ? 'tone-success' : 'tone-danger'}">
            <span class="health-dot ${liveStatus ? 'is-live' : 'is-danger'}"></span>
            ${liveStatus ? 'API ổn định' : 'API cần kiểm tra'}
        </span>
    `;

    healthLabel.textContent = liveStatus
        ? 'Tuyến xác thực đang phản hồi ổn định'
        : 'Auth Gateway đang mất phản hồi hoặc trả về trạng thái lỗi';
    healthCopy.textContent = liveStatus
        ? 'Có thể tiếp tục đọc tín hiệu vận hành, mở dashboard phân tích hoặc kiểm tra ETL.'
        : 'Ưu tiên kiểm tra dịch vụ nền trước khi trình bày dashboard phân tích cho hội đồng.';
}

async function loadKPIs() {
    try {
        const response = await fetch('/api/kpi');
        if (!response.ok) return;
        const data = await response.json();
        appState.kpi = data.kpi || {};
        renderKPIs();
    } catch (error) {
        console.warn('KPI load error:', error);
    }
}

function renderKPIs() {
    const kpi = appState.kpi;
    byId('kpi-revenue').textContent = formatCurrency(kpi.total_revenue || 0);
    byId('kpi-profit').textContent = formatCurrency(kpi.total_profit || 0);
    byId('kpi-orders').textContent = formatInteger(kpi.total_orders || 0);
    byId('kpi-customers').textContent = formatInteger(kpi.total_customers || 0);
    byId('kpi-revenue-change').textContent = 'Dùng để mở câu chuyện doanh thu theo tenant và danh mục.';
    byId('kpi-profit-change').textContent = `Biên lợi nhuận gộp: ${kpi.profit_margin_pct || 0}%`;
    byId('kpi-orders-change').textContent = (kpi.low_stock_alerts || 0) > 0
        ? `${kpi.low_stock_alerts} cảnh báo tồn kho đang mở.`
        : 'Chưa ghi nhận cảnh báo tồn kho khẩn.';
    byId('kpi-customers-change').textContent = 'Theo dõi phạm vi khách hàng đang hiện diện trong hệ thống.';
    renderOverviewIntel();
}

function getFreshnessInfo() {
    const latestLog = sortLogs(appState.etlLogs)[0];
    if (!latestLog?.start_time) {
        return {
            tone: 'tone-warning',
            label: 'Chưa có log ETL gần đây',
            caption: 'Cần chạy ETL hoặc xác nhận kênh log trước khi trình bày độ tươi dữ liệu.',
            timestamp: 'Chưa có mốc đồng bộ',
        };
    }

    const latestDate = new Date(latestLog.start_time);
    const diffHours = (Date.now() - latestDate.getTime()) / 36e5;
    if (diffHours <= 8) {
        return {
            tone: 'tone-success',
            label: 'Dữ liệu đang ở vùng tươi',
            caption: `Lần ETL gần nhất chạy lúc ${formatDateTime(latestLog.start_time)}.`,
            timestamp: formatDateTime(latestLog.start_time),
        };
    }
    if (diffHours <= 24) {
        return {
            tone: 'tone-warning',
            label: 'Dữ liệu cần được nhắc lại khi demo',
            caption: `Lần ETL gần nhất chạy lúc ${formatDateTime(latestLog.start_time)}.`,
            timestamp: formatDateTime(latestLog.start_time),
        };
    }
    return {
        tone: 'tone-danger',
        label: 'Dữ liệu đã lâu chưa được làm tươi',
        caption: `Lần ETL gần nhất là ${formatDateTime(latestLog.start_time)}.`,
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
            title: `${tenant.tenant_id} đã hết hạn`,
            detail: `Tenant cần được gia hạn hoặc giải thích rõ trạng thái trước khi cấp dashboard.`,
        });
    });

    inactive.forEach((tenant) => {
        items.push({
            tone: 'tone-warning',
            title: `${tenant.tenant_id} đang tắt`,
            detail: 'Tenant hiện không active. Cần xác minh đây là chủ ý quản trị hay sự cố.',
        });
    });

    latestFailingLogs.forEach((log) => {
        items.push({
            tone: 'tone-danger',
            title: `ETL lỗi tại ${log.tenant_id || 'tenant chưa rõ'}`,
            detail: `${log.source_table || 'Nguồn dữ liệu'} trả về trạng thái ${log.status || 'lỗi'} lúc ${formatDateTime(log.start_time)}.`,
        });
    });

    if (!items.length) {
        items.push({
            tone: 'tone-success',
            title: 'Chưa có tenant cần can thiệp ngay',
            detail: 'Có thể dùng overview làm điểm mở đầu rồi chuyển thẳng sang phòng phân tích phù hợp.',
        });
    }

    container.innerHTML = items.slice(0, 4).map((item) => `
        <article class="attention-item">
            <div class="attention-item__head">
                <span class="status-pill ${item.tone}">${item.title}</span>
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
            ? `${activeTenantCount} tenant đang active trong hệ thống.`
            : 'Sẽ hiển thị khi danh sách tenant được nạp.';
    }

    if (byId('userInventoryCount')) {
        byId('userInventoryCount').textContent = formatInteger(users);
        byId('userInventoryNote').textContent = users
            ? 'Bao gồm admin hệ thống và các user theo tenant.'
            : 'Chưa nạp danh sách user quản trị.';
    }

    if (byId('etlIssueCount')) {
        byId('etlIssueCount').textContent = formatInteger(etlIssues);
        byId('etlIssueNote').textContent = etlIssues
            ? 'Có log ETL lỗi cần được giải thích hoặc xử lý.'
            : 'Chưa ghi nhận log ETL lỗi trong dữ liệu đang có.';
    }
}

function renderNextAction() {
    const freshness = getFreshnessInfo();
    let nextAction = 'Mở Dashboard Doanh thu để bắt đầu câu chuyện vận hành.';

    if (appState.health !== 'ok') {
        nextAction = 'Kiểm tra Auth Gateway trước, sau đó mới trình bày phần dashboard.';
    } else if (appState.etlLogs.some((log) => isFailStatus(log.status))) {
        nextAction = 'Đi tới Vận hành ETL hoặc Giám sát ETL để giải thích lỗi pipeline mới nhất.';
    } else if (appState.tenants.some((tenant) => tenant.expires_at && new Date(tenant.expires_at) < new Date())) {
        nextAction = 'Mở Quản trị hệ thống để xử lý tenant đã hết hạn rồi mới đi tiếp.';
    } else if (freshness.tone === 'tone-warning' || freshness.tone === 'tone-danger') {
        nextAction = 'Nhắc rõ thời điểm ETL gần nhất trước khi đi sâu vào các chỉ số phân tích.';
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
    if (byId('sessionScope')) {
        byId('sessionScope').textContent = APP_CONTEXT.userTenant || 'Toàn hệ thống';
    }
    if (byId('sessionRole')) {
        byId('sessionRole').textContent = APP_CONTEXT.userRole === 'superadmin'
            ? 'Superadmin'
            : APP_CONTEXT.userRole === 'admin'
                ? 'Admin'
                : 'Viewer';
    }
    if (byId('overviewTimestamp')) {
        byId('overviewTimestamp').textContent = new Date().toLocaleString('vi-VN');
    }

    renderAttentionList();
    renderGovernanceStats();
    renderNextAction();
}

function tableEmpty(message, colspan) {
    return `<tr><td colspan="${colspan}"><div class="empty-state"><strong>${escapeHtml(message)}</strong></div></td></tr>`;
}

function renderTenants(tenants) {
    const container = byId('tenant-list');
    if (!container) return;
    if (!tenants.length) {
        container.innerHTML = tableEmpty('Chưa có tenant nào trong hệ thống.', 6);
        return;
    }
    const now = new Date();
    container.innerHTML = tenants.map((tenant) => {
        const expired = tenant.expires_at && new Date(tenant.expires_at) < now;
        return `
            <tr>
                <td data-label="Mã tenant"><strong>${escapeHtml(tenant.tenant_id)}</strong></td>
                <td data-label="Tên tenant">${escapeHtml(tenant.tenant_name)}</td>
                <td data-label="Đường dẫn">${escapeHtml(tenant.file_path || '—')}</td>
                <td data-label="Trạng thái"><span class="status-pill ${statusToneByBool(tenant.is_active)}">${tenant.is_active ? 'Hoạt động' : 'Tắt'}</span></td>
                <td data-label="Hiệu lực">
                    <span class="status-pill ${expired ? 'tone-danger' : tenant.expires_at ? 'tone-warning' : 'tone-neutral'}">
                        ${tenant.expires_at ? formatDateTime(tenant.expires_at) : 'Không giới hạn'}
                    </span>
                </td>
                <td data-label="Thao tác">
                    <button class="button button--secondary button--compact" type="button" onclick="openEditTenant('${escapeHtml(tenant.tenant_id)}')">Chỉnh tenant</button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderUsers(users) {
    const container = byId('user-list');
    if (!container) return;
    if (!users.length) {
        container.innerHTML = tableEmpty('Chưa có user nào trong hệ thống.', 5);
        return;
    }
    container.innerHTML = users.map((user) => {
        const safeUsername = encodeURIComponent(user.username || '');
        const safeTenant = encodeURIComponent(user.tenant_id || '');
        const safeRole = encodeURIComponent(user.role || 'viewer');
        return `
        <tr>
            <td data-label="Username"><strong>${escapeHtml(user.username)}</strong></td>
            <td data-label="Tenant">${escapeHtml(user.tenant_id || '—')}</td>
            <td data-label="Vai trò"><span class="status-pill ${user.role === 'admin' ? 'tone-warning' : 'tone-neutral'}">${user.role === 'admin' ? 'Admin' : 'Viewer'}</span></td>
            <td data-label="Trạng thái"><span class="status-pill ${statusToneByBool(user.is_active)}">${user.is_active ? 'Hoạt động' : 'Tắt'}</span></td>
            <td data-label="Thao tác">
                <button class="button button--secondary button--compact" type="button" onclick="openEditUser(${Number(user.user_id)}, decodeURIComponent('${safeUsername}'), decodeURIComponent('${safeTenant}'), decodeURIComponent('${safeRole}'), ${Boolean(user.is_active)})">Chỉnh user</button>
            </td>
        </tr>
    `;
    }).join('');
}

function renderETLLogs(logs) {
    const container = byId('etl-logs');
    if (!container) return;
    if (!logs.length) {
        container.innerHTML = '<div class="empty-state"><strong>Chưa có log ETL.</strong><span class="microcopy">Khi pipeline chạy, các bản ghi gần nhất sẽ xuất hiện ở đây.</span></div>';
        return;
    }

    container.innerHTML = `
        <div class="table-shell">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Thời gian</th>
                        <th>Tenant</th>
                        <th>Nguồn</th>
                        <th>Trạng thái</th>
                        <th>Số dòng</th>
                    </tr>
                </thead>
                <tbody>
                    ${sortLogs(logs).slice(0, 20).map((log) => `
                        <tr>
                            <td data-label="Thời gian">${formatDateTime(log.start_time)}</td>
                            <td data-label="Tenant"><strong>${escapeHtml(log.tenant_id || '—')}</strong></td>
                            <td data-label="Nguồn">${escapeHtml(log.source_table || '—')}</td>
                            <td data-label="Trạng thái"><span class="status-pill ${isFailStatus(log.status) ? 'tone-danger' : isSuccessStatus(log.status) ? 'tone-success' : 'tone-neutral'}">${escapeHtml(log.status || '—')}</span></td>
                            <td data-label="Số dòng" class="tabular">${formatInteger(log.rows_inserted || 0)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

async function loadAdminData() {
    await populateTenantDropdown();

    try {
        const tenantResponse = await authFetch('/api/tenants');
        if (tenantResponse.ok) {
            const data = await tenantResponse.json();
            appState.tenants = data.tenants || [];
            renderTenants(appState.tenants);
        }
    } catch (error) {
        console.warn('Tenants load error', error);
    }

    try {
        const userResponse = await authFetch('/api/users');
        if (userResponse.ok) {
            const data = await userResponse.json();
            appState.users = data.users || [];
            renderUsers(appState.users);
        }
    } catch (error) {
        console.warn('Users load error', error);
    }

    try {
        const logResponse = await authFetch('/api/etl/logs');
        if (logResponse.ok) {
            const data = await logResponse.json();
            appState.etlLogs = data.logs || [];
            renderETLLogs(appState.etlLogs);
        }
    } catch (error) {
        console.warn('ETL logs load error', error);
    }

    renderOverviewIntel();
}

function populateStatusBlock({ toneClass, icon, title, detail }) {
    const status = byId('uploadStatus');
    const iconEl = byId('statusIcon');
    const titleEl = byId('statusText');
    const detailEl = byId('statusDetail');
    if (!status || !iconEl || !titleEl || !detailEl) return;

    status.className = `workflow-status ${toneClass}`;
    status.hidden = false;
    iconEl.innerHTML = icon;
    titleEl.textContent = title;
    detailEl.innerHTML = detail;
}

function currentTenant() {
    const select = byId('etlTenantSelect');
    return select ? select.value : (APP_CONTEXT.userTenant || '');
}

async function populateETLTenantSelect() {
    const select = byId('etlTenantSelect');
    if (!select) return;
    try {
        const response = await authFetch('/api/tenants');
        if (!response.ok) return;
        const data = await response.json();
        const tenants = data.tenants || [];
        select.innerHTML = tenants.map((tenant) => `<option value="${tenant.tenant_id}">${tenant.tenant_id} — ${tenant.tenant_name}</option>`).join('');
    } catch (error) {
        console.warn('ETL tenant load error', error);
    }
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
                    <span>${(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                </article>
            `).join('')}
        </div>
        <div class="inline-actions">
            <button class="button button--primary" id="btnUploadSubmit" type="button">Nạp file vào staging</button>
            <button class="button button--secondary" type="button" id="btnRunEtl">Chạy ETL ngay</button>
        </div>
    `;

    byId('btnUploadSubmit').addEventListener('click', uploadFile);
    byId('btnRunEtl').addEventListener('click', () => triggerETL(currentTenant()));
}

async function uploadFile() {
    const input = byId('fileInput');
    if (!input?.files.length) {
        alert('Vui lòng chọn ít nhất một file để nạp.');
        return;
    }

    const formData = new FormData();
    for (const file of input.files) {
        formData.append('files', file);
    }

    const submitButton = byId('btnUploadSubmit');
    if (submitButton) submitButton.disabled = true;

    populateStatusBlock({
        toneClass: 'is-running',
        icon: '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" fill="none"></circle><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path>',
        title: `Đang nạp ${input.files.length} file lên staging`,
        detail: '<p>Hệ thống đang gửi file tới API upload và kiểm tra phản hồi.</p>',
    });

    try {
        const response = await authFetch(`/api/upload/${currentTenant()}`, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.detail || data.message || 'Upload thất bại');
        }

        populateStatusBlock({
            toneClass: 'is-success',
            icon: '<path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"></path>',
            title: `Đã nạp ${data.successful_uploads}/${data.total_files} file vào staging`,
            detail: data.uploaded_files.map((file) => (
                `<p>${file.success ? '✓' : '✕'} ${escapeHtml(file.filename)}${file.file_type ? ` · ${escapeHtml(file.file_type)}` : ''}${file.error ? ` · ${escapeHtml(file.error)}` : ''}</p>`
            )).join(''),
        });

        input.value = '';
        byId('uploadPreview').innerHTML = '';
        await loadUploadedFiles();
    } catch (error) {
        populateStatusBlock({
            toneClass: 'is-error',
            icon: '<path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>',
            title: 'Không thể nạp file vào staging',
            detail: `<p>${escapeHtml(error.message)}</p>`,
        });
    } finally {
        if (submitButton) submitButton.disabled = false;
    }
}

async function triggerETL(tenant) {
    if (!tenant) {
        alert('Chưa có tenant để chạy ETL.');
        return;
    }

    populateStatusBlock({
        toneClass: 'is-running',
        icon: '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" fill="none"></circle><path d="M12 7v5l3 2" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path>',
        title: `Đang kích hoạt ETL cho ${tenant}`,
        detail: '<p>Pipeline sẽ nạp dữ liệu vào warehouse và tạo log tương ứng.</p>',
    });

    try {
        const response = await authFetch(`/api/upload/${tenant}/etl`, { method: 'POST' });
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.detail || data.message || 'Không kích hoạt được ETL');
        }

        populateStatusBlock({
            toneClass: 'is-success',
            icon: '<path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"></path>',
            title: `ETL đã được kích hoạt cho ${tenant}`,
            detail: `<p>${escapeHtml(data.message || 'Theo dõi log ETL để kiểm tra tiến trình nạp dữ liệu.')}</p>`,
        });

        if (APP_CONTEXT.userRole === 'superadmin') {
            await loadAdminData();
        }
    } catch (error) {
        populateStatusBlock({
            toneClass: 'is-error',
            icon: '<path d="M18 6 6 18M6 6l12 12" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round"></path>',
            title: 'ETL không thể khởi chạy',
            detail: `<p>${escapeHtml(error.message)}</p>`,
        });
    }
}

async function loadUploadedFiles() {
    const tenant = currentTenant();
    const container = byId('uploadedFilesList');
    if (!container) return;

    if (!tenant) {
        container.innerHTML = '<div class="empty-state"><strong>Chưa có tenant đang được chọn.</strong><span class="microcopy">Chọn tenant trước khi xem lịch sử upload.</span></div>';
        return;
    }

    try {
        const response = await authFetch(`/api/upload/${tenant}/files`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        const files = data.files || [];

        if (!files.length) {
            container.innerHTML = '<div class="empty-state"><strong>Chưa có file nào được nạp gần đây.</strong><span class="microcopy">Sau khi upload, lịch sử file sẽ hiển thị ở đây.</span></div>';
            return;
        }

        container.innerHTML = `
            <div class="table-shell">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Tên file</th>
                            <th>Loại</th>
                            <th>Kích thước</th>
                            <th>Thời điểm</th>
                            ${['admin', 'superadmin'].includes(APP_CONTEXT.userRole) ? '<th>Thao tác</th>' : ''}
                        </tr>
                    </thead>
                    <tbody>
                        ${files.map((file) => `
                            <tr>
                                <td data-label="Tên file"><strong>${escapeHtml(file.filename)}</strong></td>
                                <td data-label="Loại"><span class="status-pill tone-neutral">${escapeHtml(file.file_type || 'Chưa rõ')}</span></td>
                                <td data-label="Kích thước">${file.size_bytes > 1024 * 1024 ? `${(file.size_bytes / 1024 / 1024).toFixed(1)} MB` : `${(file.size_bytes / 1024).toFixed(1)} KB`}</td>
                                <td data-label="Thời điểm">${formatDateTime(file.uploaded_at)}</td>
                                ${['admin', 'superadmin'].includes(APP_CONTEXT.userRole)
                                    ? `<td data-label="Thao tác"><button class="button button--danger button--compact" type="button" onclick="deleteFile('${encodeURIComponent(tenant)}', '${encodeURIComponent(file.filename)}')">Xóa file</button></td>`
                                    : ''}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    } catch (error) {
        container.innerHTML = `<div class="empty-state"><strong>Lỗi tải file.</strong><span class="microcopy">${escapeHtml(error.message)}</span></div>`;
    }
}

async function deleteFile(tenant, filename) {
    const decodedTenant = decodeURIComponent(tenant);
    const decodedFilename = decodeURIComponent(filename);
    if (!confirm(`Xóa file "${decodedFilename}" khỏi staging?`)) return;
    try {
        const response = await fetch(`/api/upload/${decodedTenant}/files/${encodeURIComponent(decodedFilename)}`, { method: 'DELETE' });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || 'Không thể xóa file');
        await loadUploadedFiles();
    } catch (error) {
        alert(error.message);
    }
}

async function populateTenantDropdown() {
    const select = byId('adminNewUserTenant');
    if (!select) return;
    try {
        const response = await authFetch('/api/tenants');
        if (!response.ok) return;
        const data = await response.json();
        const tenants = data.tenants || [];
        select.innerHTML = '<option value="">Toàn hệ thống</option>' +
            tenants.map((tenant) => `<option value="${tenant.tenant_id}">${tenant.tenant_id} — ${tenant.tenant_name}</option>`).join('');
    } catch (error) {
        console.warn('Tenant dropdown load error', error);
    }
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
        message.textContent = 'Vui lòng nhập mã tenant hợp lệ.';
        message.className = 'microcopy form-msg is-error';
        return;
    }

    message.textContent = 'Đang tạo tenant...';
    message.className = 'microcopy form-msg is-running';

    const body = { tenant_id: tenantId, tenant_name: tenantName, file_path: filePath };
    if (expiresAt) body.expires_at = expiresAt;

    try {
        const response = await authFetch('/api/tenants', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || 'Không thể tạo tenant');

        message.textContent = `Đã tạo tenant ${tenantId}.`;
        message.className = 'microcopy form-msg is-success';
        ['newTenantId', 'newTenantName', 'newTenantFilePath', 'newTenantExpiresAt'].forEach((id) => {
            byId(id).value = '';
        });
        await loadAdminData();
    } catch (error) {
        message.textContent = error.message;
        message.className = 'microcopy form-msg is-error';
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
        message.textContent = 'Viewer cần gắn với một tenant cụ thể.';
        message.className = 'microcopy form-msg is-error';
        return;
    }

    message.textContent = 'Đang tạo user...';
    message.className = 'microcopy form-msg is-running';

    try {
        const response = await authFetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, tenant_id: tenantId, role }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || 'Không thể tạo user');

        message.textContent = `Đã tạo user ${username}.`;
        message.className = 'microcopy form-msg is-success';
        byId('adminNewUserUsername').value = '';
        byId('adminNewUserPassword').value = '';
        byId('adminNewUserTenant').value = '';
        await loadAdminData();
    } catch (error) {
        message.textContent = error.message;
        message.className = 'microcopy form-msg is-error';
    }
}

async function loadTenantUsers() {
    const container = byId('tenant-user-list');
    if (!container) return;
    try {
        const response = await authFetch('/api/users');
        if (!response.ok) throw new Error('Không tải được danh sách user');
        const data = await response.json();
        renderTenantUsers(data.users || []);
    } catch (error) {
        container.innerHTML = tableEmpty(error.message, 5);
    }
}

function renderTenantUsers(users) {
    const container = byId('tenant-user-list');
    if (!container) return;
    if (!users.length) {
        container.innerHTML = tableEmpty('Tenant này chưa có user nào.', 5);
        return;
    }
    container.innerHTML = users.map((user) => {
        const safeUsername = encodeURIComponent(user.username || '');
        const safeTenant = encodeURIComponent(APP_CONTEXT.userTenant || '');
        const safeRole = encodeURIComponent(user.role || 'viewer');
        return `
        <tr>
            <td data-label="Username"><strong>${escapeHtml(user.username)}</strong></td>
            <td data-label="Vai trò"><span class="status-pill tone-neutral">${escapeHtml(user.role === 'viewer' ? 'Viewer' : user.role)}</span></td>
            <td data-label="Trạng thái"><span class="status-pill ${statusToneByBool(user.is_active)}">${user.is_active ? 'Hoạt động' : 'Tắt'}</span></td>
            <td data-label="Ngày tạo">${formatDateTime(user.created_at)}</td>
            <td data-label="Thao tác"><button class="button button--secondary button--compact" type="button" onclick="openEditUser(${Number(user.user_id)}, decodeURIComponent('${safeUsername}'), decodeURIComponent('${safeTenant}'), decodeURIComponent('${safeRole}'), ${Boolean(user.is_active)})">Chỉnh user</button></td>
        </tr>
    `;
    }).join('');
}

async function createTenantUser(event) {
    event.preventDefault();
    const message = byId('tenantUserCreateMsg');
    const username = byId('tenantNewUserUsername').value.trim();
    const password = byId('tenantNewUserPassword').value;

    message.textContent = 'Đang tạo user tenant...';
    message.className = 'microcopy form-msg is-running';

    try {
        const response = await authFetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password, role: 'viewer' }),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || 'Không thể tạo user');

        message.textContent = `Đã tạo user ${username}.`;
        message.className = 'microcopy form-msg is-success';
        byId('tenantNewUserUsername').value = '';
        byId('tenantNewUserPassword').value = '';
        await loadTenantUsers();
    } catch (error) {
        message.textContent = error.message;
        message.className = 'microcopy form-msg is-error';
    }
}

function openEditTenant(tenantId) {
    const tenant = appState.tenants.find((item) => item.tenant_id === tenantId);
    if (!tenant) return;

    byId('editTenantId').value = tenant.tenant_id;
    byId('editTenantName').value = tenant.tenant_name;
    byId('editTenantFilePath').value = tenant.file_path || '';
    byId('editTenantActive').value = tenant.is_active ? '1' : '0';
    byId('editTenantExpiresAt').value = tenant.expires_at
        ? new Date(new Date(tenant.expires_at).getTime() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 16)
        : '';
    byId('editTenantTitle').textContent = `Chỉnh tenant ${tenantId}`;
    byId('editTenantMsg').textContent = '';
    toggleModal('modalEditTenant', true);
}

function closeEditTenantModal() {
    toggleModal('modalEditTenant', false);
}

async function submitEditTenant(event) {
    event.preventDefault();
    const message = byId('editTenantMsg');
    const tenantId = byId('editTenantId').value;

    message.textContent = 'Đang lưu thay đổi...';
    message.className = 'microcopy form-msg is-running';

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
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || 'Không thể lưu tenant');

        message.textContent = 'Đã lưu thay đổi tenant.';
        message.className = 'microcopy form-msg is-success';
        await loadAdminData();
        window.setTimeout(closeEditTenantModal, 700);
    } catch (error) {
        message.textContent = error.message;
        message.className = 'microcopy form-msg is-error';
    }
}

async function openEditUser(userId, username, tenantId, role, isActive) {
    byId('editUserId').value = userId;
    byId('editUserUsername').value = username;
    byId('editUserPassword').value = '';
    byId('editUserRole').value = role;
    byId('editUserActive').value = isActive ? '1' : '0';
    byId('editUserTitle').textContent = `Chỉnh user ${username}`;
    byId('editUserMsg').textContent = '';

    const select = byId('editUserTenant');
    select.innerHTML = '<option value="">Toàn hệ thống</option>';
    try {
        const response = await authFetch('/api/tenants');
        if (response.ok) {
            const data = await response.json();
            const tenants = data.tenants || [];
            select.innerHTML = '<option value="">Toàn hệ thống</option>' +
                tenants.map((tenant) => `<option value="${tenant.tenant_id}">${tenant.tenant_id} — ${tenant.tenant_name}</option>`).join('');
        }
    } catch (error) {
        console.warn('Tenant list for edit user failed', error);
    }
    select.value = tenantId || '';
    toggleModal('modalEditUser', true);
}

function closeEditUserModal() {
    toggleModal('modalEditUser', false);
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

    message.textContent = 'Đang lưu thay đổi user...';
    message.className = 'microcopy form-msg is-running';

    try {
        const response = await authFetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const data = await response.json();
        if (!response.ok || !data.success) throw new Error(data.detail || data.message || 'Không thể lưu user');

        message.textContent = 'Đã lưu thay đổi user.';
        message.className = 'microcopy form-msg is-success';
        if (APP_CONTEXT.userRole === 'superadmin') {
            await loadAdminData();
        } else if (APP_CONTEXT.userRole === 'admin') {
            await loadTenantUsers();
        }
        window.setTimeout(closeEditUserModal, 700);
    } catch (error) {
        message.textContent = error.message;
        message.className = 'microcopy form-msg is-error';
    }
}

function bindGlobalEvents() {
    byId('toggleSidebar')?.addEventListener('click', toggleSidebar);
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

    byId('fileInput')?.addEventListener('change', showFilePreview);
    byId('etlTenantSelect')?.addEventListener('change', loadUploadedFiles);

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
}

function bindForms() {
    byId('formCreateTenant')?.addEventListener('submit', createTenant);
    byId('formCreateAdminUser')?.addEventListener('submit', createUser);
    byId('formCreateTenantUser')?.addEventListener('submit', createTenantUser);
    byId('formEditTenant')?.addEventListener('submit', submitEditTenant);
    byId('formEditUser')?.addEventListener('submit', submitEditUser);
    byId('newTenantId')?.addEventListener('input', autoFillTenantPath);
}

document.addEventListener('DOMContentLoaded', async () => {
    bindNavigation();
    bindGlobalEvents();
    bindForms();
    setSidebarState();
    renderOverviewIntel();
    navigateTo('overview');
    checkHealth();
    loadKPIs();
    populateETLTenantSelect();
    loadUploadedFiles();

    if (APP_CONTEXT.userRole === 'superadmin') {
        await loadAdminData();
    }
    if (APP_CONTEXT.userRole === 'admin') {
        await loadTenantUsers();
    }
});

window.openEditTenant = openEditTenant;
window.openEditUser = openEditUser;
window.closeModal = closeModal;
window.closeEditTenantModal = closeEditTenantModal;
window.closeEditUserModal = closeEditUserModal;
window.deleteFile = deleteFile;
window.triggerETL = triggerETL;
window.currentTenant = currentTenant;
