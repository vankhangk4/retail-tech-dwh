# ============================================================
# FILE: superset/superset_config.py
# Mô tả: Apache Superset Configuration — RBAC + Multi-Tenant RLS
# ============================================================

import os

# SECRET_KEY — bắt buộc, Superset không chạy nếu không có
# IMPORTANT: Phải sử dụng một key cố định từ .env để tránh session bị invalid
SECRET_KEY = os.environ.get(
    'SUPERSET_SECRET_KEY',
    'default-secret-key-superset-dwh-multitenant-32chars-min!!!'  # Cố định cho dev
)
# Không tạo key ngẫu nhiên - nó sẽ làm hỏng session và gây redirect loop
# if 'changeme' in SECRET_KEY:
#     SECRET_KEY = 'dev-secret-key-' + ''.join(random.choices(string.ascii_letters + string.digits, k=40))

# ============================================================
# AUTHENTICATION & SECURITY
# ============================================================

# Tắt đăng ký tự động — user không tự tạo tài khoản
AUTH_USER_REGISTRATION = False

# Role mặc định cho anonymous user (None = không cho phép truy cập)
PUBLIC_ROLE_LIKE = None

# Tắt CSRF khi chạy provisioning script (bật lại bằng env SUPERSET_CSRF_ENABLED=true khi cần)
WTF_CSRF_ENABLED = os.environ.get('SUPERSET_CSRF_ENABLED', 'false').lower() == 'true'
WTF_CSRF_TIME_LIMIT = 3600  # 1 giờ

# Session timeout (8 giờ = 28800 giây = JWT access token TTL)
PERMANENT_SESSION_LIFETIME = 28800

# Cookie settings
SESSION_COOKIE_HTTPONLY = True  # Không cho JavaScript truy cập
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection

# Bật CORS (chỉ cho phép domain thật khi production)
ENABLE_CORS = True
CORS_ALLOW_ORIGINS = '*'
CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
CORS_ALLOW_CREDENTIALS = True

# Cookie settings (HTTP trong dev, HTTPS trong prod)
SESSION_COOKIE_SECURE = os.environ.get('SUPERSET_COOKIE_SECURE', 'False').lower() == 'true'

# ============================================================
# FEATURE FLAGS
# ============================================================

FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'ENABLE_JAVASCRIPT_CONTROLS': False,    # Tắt để tránh XSS
    'SQLLAB_BACKEND_PERSISTENCE': True,
    'DASHBOARD_CACHE': True,
    'ROW_LEVEL_SECURITY': True,              # BẬT RLS cho multi-tenant
    'ALERT_REPORTS': True,
    'DISPLAY_MARKDOWN': True,
    'EMBEDDED_SUPERSET': True,              # BẬT embedded SDK — cho phép embed dashboard
}

# ============================================================
# ROW LEVEL SECURITY (RLS) CONFIGURATION
# ============================================================
# Superset RLS tự động append WHERE clause vào mọi query
# Cấu hình được thiết lập trong Superset UI:
#   Security → Row Level Security → (+)
#   Table: FactSales, Role: RLS_STORE_HN, Clause: tenant_id = 'STORE_HN'
#
# Các Role RLS cần tạo trong Superset:
#   - RLS_STORE_HN  → thấy data STORE_HN
#   - RLS_STORE_HCM → thấy data STORE_HCM
#   - Admin: không có RLS filter (toàn quyền)
#
# Các bảng cần cấu hình RLS:
#   - FactSales, FactInventory, FactPurchase (TenantID)
#   - DimCustomer, DimStore, DimEmployee (TenantID)
#   - DM_SalesSummary, DM_CustomerRFM (TenantID)

# ============================================================
# DATABASE CONNECTION
# ============================================================

# Superset METADATA database — BẮT BUỘC dùng PostgreSQL (Superset internal tables)
# Đây là nơi Superset lưu: users, roles, dashboards, charts, RLS rules
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL',
    'postgresql://superset:superset123@superset-db:5432/superset'
)

# MSSQL Data Warehouse — dùng để query data (không phải Superset metadata)
# Đặt tên khác để tránh nhầm lẫn với SQLALCHEMY_DATABASE_URI
# Superset sẽ kết nối MSSQL qua UI: Settings → Databases → + Database
MSSQL_WAREHOUSE_URI = os.environ.get(
    'MSSQL_DATABASE_URL',
    f"mssql+pymssql://sa:{os.environ.get('MSSQL_SA_PASSWORD', 'M1tjtnrx')}@mssql:1433/DWH_MultiTenant"
)

# ============================================================
# CACHE CONFIGURATION
# ============================================================

# Redis cache backend
_cache_host = os.environ.get('REDIS_HOST', 'superset-redis')
_cache_port = os.environ.get('REDIS_PORT', '6379')
_cache_pass = os.environ.get('REDIS_PASSWORD', '')
_cache_db = os.environ.get('REDIS_DB', '0')

# Use redis:// URL format for better compatibility
if _cache_pass:
    _redis_url = f'redis://:{_cache_pass}@{_cache_host}:{_cache_port}/{_cache_db}'
else:
    _redis_url = f'redis://{_cache_host}:{_cache_port}/{_cache_db}'

CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': _redis_url,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_DEFAULT_TIMEOUT': 300,
}

# Data cache per dashboard
DATA_CACHE_TIME_OUT = 300  # 5 phút

# ============================================================
# LOGGING
# ============================================================

# Ghi log hoạt động của user (đăng nhập, truy cập dashboard)
LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'
LOG_LEVEL = 'INFO'

# ============================================================
# MISC
# ============================================================

# Upload max size (10MB)
DASHBOARD_POSITION_DATA_LIMIT = 65536
UPLOAD_MAX_SIZE = 10 * 1024 * 1024

# Alert & Reports
ALERT_REPORTS_NOTIFICATION_DRY_RUN = False
ALERT_REPORTS_WORKING_TIMEOUT = 3600

# Hide left navbar for tenants (view only mode)
FAB_VIEW_MENU__hide_nav_if_no_perms = True