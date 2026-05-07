# ============================================================
# FILE: api/auth.py
# Mô tả: Auth Gateway — FastAPI endpoints cho xác thực multi-tenant
# Users được khai báo trong .env (source of truth)
# Backend tự động upsert vào AppUsers khi khởi động
# ============================================================

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import passlib.context
import pymssql as mssql
import requests
from fastapi import APIRouter, HTTPException, Header, Depends, Request
from pydantic import BaseModel

from api.superset_provision import provision_user as superset_provision_user
from api.models import (
    LoginRequest, LoginResponse, UserInfo,
    DashboardTokenResponse, TokenPayload,
    RegisterRequest,
    UserProfile, UpdateProfileRequest, ChangePasswordRequest,
    AvatarUploadRequest, LoginHistoryItem,
)

# ---- Configuration ----
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'changeme-minimum-32-chars!!')
ALGORITHM = 'HS256'
ACCESS_EXPIRE = timedelta(hours=8)
REFRESH_EXPIRE = timedelta(days=7)
SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
SUPERSET_PUBLIC_URL = os.environ.get('SUPERSET_PUBLIC_URL', SUPERSET_URL)
SUPERSET_ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
SUPERSET_ADMIN_PWD = os.environ.get('SUPERSET_ADMIN_PWD', 'admin')
SUPERSET_EMBED_ALLOWED_DOMAINS = [
    domain.strip()
    for domain in os.environ.get('SUPERSET_EMBED_ALLOWED_DOMAINS', '').split(',')
    if domain.strip()
]
LEGACY_DASHBOARD_ID_MAP = {
    11: 1,
    12: 2,
    13: 3,
    14: 4,
    15: 5,
}

# ---- Password hashing ----
pwd_ctx = passlib.context.CryptContext(schemes=['bcrypt'], deprecated='auto')

# ---- Logger ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Router ----
router = APIRouter(prefix='/api', tags=['Authentication'])


# ---- Helpers ----

def get_mssql_conn():
    """Tạo kết nối SQL Server."""
    return mssql.connect(
        server=os.environ.get('MSSQL_SERVER', 'localhost'),
        user=os.environ.get('MSSQL_USER', 'sa'),
        password=os.environ.get('MSSQL_PASSWORD', ''),
        database=os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant')
    )


def get_db():
    """Dependency để lấy kết nối SQL Server."""
    conn = get_mssql_conn()
    try:
        yield conn
    finally:
        conn.close()


def verify_password(plain: str, hashed: str) -> bool:
    """Xác thực password với bcrypt hash."""
    try:
        return pwd_ctx.verify(plain, hashed)
    except Exception:
        return False


def hash_password(password: str) -> str:
    """Hash password bằng bcrypt (rounds=12)."""
    return pwd_ctx.hash(password)


def create_access_token(user_id: int, username: str, tenant_id: Optional[str], role: str) -> str:
    """Tạo JWT access token chứa user_id, username, tenant_id, role."""
    payload = {
        'user_id': user_id,
        'username': username,
        'tenant_id': tenant_id,
        'role': role,
        'exp': datetime.now(timezone.utc) + ACCESS_EXPIRE,
        'iat': datetime.now(timezone.utc),
        'type': 'access',
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def create_refresh_token(user_id: int, username: str) -> str:
    """Tạo JWT refresh token."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(timezone.utc) + REFRESH_EXPIRE,
        'iat': datetime.now(timezone.utc),
        'type': 'refresh',
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> TokenPayload:
    """Decode và validate JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail='Token da het han')
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Token khong hop le')


def get_superset_admin_token() -> str:
    """Lấy Superset admin token để tạo guest token."""
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/login',
        json={
            'username': SUPERSET_ADMIN_USER,
            'password': SUPERSET_ADMIN_PWD,
            'provider': 'db'
        },
        timeout=30
    )
    if r.status_code != 200:
        raise HTTPException(502, detail=f'Khong lay duoc Superset admin token: {r.text}')
    return r.json()['access_token']


def get_or_create_embedded_dashboard_uuid(dashboard_id: int, admin_token: str) -> str:
    """Ensure Superset embedded config exists and return its UUID."""
    headers = {'Authorization': f'Bearer {admin_token}'}
    embedded_url = f'{SUPERSET_URL}/api/v1/dashboard/{dashboard_id}/embedded'

    try:
        r = requests.get(embedded_url, headers=headers, timeout=30)
    except requests.RequestException as e:
        logger.error(f'Embedded dashboard lookup error: {e}')
        raise HTTPException(502, detail=f'Loi doc embedded dashboard Superset: {str(e)}')

    if r.status_code == 200:
        embedded_uuid = r.json().get('result', {}).get('uuid')
        if embedded_uuid:
            return embedded_uuid
        raise HTTPException(502, detail='Superset embedded dashboard khong co uuid')

    if r.status_code != 404:
        logger.error(f'Embedded dashboard lookup failed: {r.status_code} — {r.text}')
        raise HTTPException(502, detail=f'Khong doc duoc embedded dashboard: {r.text}')

    try:
        r = requests.post(
            embedded_url,
            headers=headers,
            json={'allowed_domains': SUPERSET_EMBED_ALLOWED_DOMAINS},
            timeout=30
        )
    except requests.RequestException as e:
        logger.error(f'Embedded dashboard create error: {e}')
        raise HTTPException(502, detail=f'Loi tao embedded dashboard Superset: {str(e)}')

    if r.status_code not in (200, 201):
        logger.error(f'Embedded dashboard create failed: {r.status_code} — {r.text}')
        raise HTTPException(502, detail=f'Tao embedded dashboard that bai: {r.text}')

    embedded_uuid = r.json().get('result', {}).get('uuid')
    if not embedded_uuid:
        raise HTTPException(502, detail='Superset embedded dashboard khong tra ve uuid')

    logger.info(f'Embedded dashboard enabled: dashboard={dashboard_id} | uuid={embedded_uuid}')
    return embedded_uuid


# ============================================================
# BOOTSTRAP — tạo user vào AppUsers khi API khởi động
# ============================================================

def sync_existing_tenants_to_superset():
    """Sync existing tenants from MSSQL to Superset RLS provisioning.

    Called on API startup to provision RLS roles for all active tenants.
    Requires Superset to be running and PostgreSQL database accessible.
    """
    try:
        from api.superset_provision import provision_tenant

        conn = get_mssql_conn()
        cursor = conn.cursor()

        cursor.execute('SELECT TenantID FROM Tenants WHERE IsActive = 1 ORDER BY TenantID')
        tenants = [row[0] for row in cursor.fetchall()]
        conn.close()

        logger.info(f'[BOOTSTRAP] Syncing {len(tenants)} tenants to Superset RLS...')
        for tenant_id in tenants:
            try:
                success = provision_tenant(tenant_id)
                if success:
                    logger.info(f'[BOOTSTRAP] Provisioned Superset RLS for tenant: {tenant_id}')
                else:
                    logger.warning(f'[BOOTSTRAP] Failed to provision tenant {tenant_id} (may not be critical)')
            except Exception as e:
                logger.warning(f'[BOOTSTRAP] Error provisioning tenant {tenant_id}: {e}')
    except Exception as e:
        logger.warning(f'[BOOTSTRAP] Tenant sync to Superset skipped: {e}')


def bootstrap_users():
    """Upsert user từ env vào bảng AppUsers khi API start.

    Đọc từ env: DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS, DEFAULT_ADMIN_ROLE.
    Nếu env không có giá trị → bỏ qua (không tạo user mặc định trong code).
    """
    conn = get_mssql_conn()
    cursor = conn.cursor()

    try:
        username  = os.environ.get('DEFAULT_ADMIN_USER', '').strip()
        password  = os.environ.get('DEFAULT_ADMIN_PASS', '').strip()
        role      = os.environ.get('DEFAULT_ADMIN_ROLE', 'superadmin').strip()

        if not username or not password:
            logger.info('[BOOTSTRAP] DEFAULT_ADMIN_USER/PASS not set in env — skipping user bootstrap')
            return

        password_hash = hash_password(password)

        cursor.execute('SELECT UserID FROM AppUsers WHERE Username = %s', (username,))
        row = cursor.fetchone()

        if row:
            cursor.execute(
                'UPDATE AppUsers SET PasswordHash = %s, Role = %s, IsActive = 1 WHERE Username = %s',
                (password_hash, role, username)
            )
            logger.info(f'[BOOTSTRAP] Updated user: {username}')
        else:
            cursor.execute(
                'INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive) VALUES (%s, %s, %s, %s, 1)',
                (username, password_hash, None, role)
            )
            logger.info(f'[BOOTSTRAP] Created user: {username}')

        conn.commit()
        logger.info('[BOOTSTRAP] User synced to AppUsers table')

    except Exception as e:
        logger.warning(f'[BOOTSTRAP] DB sync skipped: {e}')
    finally:
        conn.close()


def get_user_id_from_db(username: str) -> Optional[int]:
    """Lấy UserID từ bảng AppUsers (sau bootstrap)."""
    conn = get_mssql_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT UserID FROM AppUsers WHERE Username = %s', (username,))
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def wait_for_mssql(max_retries: int = 10, delay: int = 5) -> bool:
    """Đợi MSSQL sẵn sàng trước khi bootstrap."""
    import time
    for attempt in range(max_retries):
        try:
            conn = get_mssql_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            conn.close()
            return True
        except Exception:
            logger.warning(f'[BOOTSTRAP] Waiting for MSSQL... attempt {attempt+1}/{max_retries}')
            time.sleep(delay)
    return False


def run_bootstrap():
    """Wrapper chạy bootstrap với retry — gọi từ startup event."""
    if not wait_for_mssql(max_retries=10, delay=5):
        logger.error('[BOOTSTRAP] MSSQL not available — skipping bootstrap')
        return
    # Sync users từ env
    bootstrap_users()
    # Sync existing tenants to Superset RLS (idempotent)
    sync_existing_tenants_to_superset()


# ---- Endpoints ----

@router.post('/register')
def register(req: RegisterRequest):
    """Đăng ký tài khoản mới — chỉ viewer. Admin phải do superadmin tạo."""
    username  = req.username.strip()
    password  = req.password
    role      = req.role or 'viewer'
    tenant_id = req.tenant_id.strip() if req.tenant_id else None

    if role != 'viewer':
        raise HTTPException(400, detail='Admin phai duoc tao boi superadmin qua /api/admin/users')

    # Validate username: chỉ chữ, số, dấu gạch dưới
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise HTTPException(400, detail='Username chi chap nhan chu cai, so va dau gach duoi')

    # Validate tenant tồn tại và đang hoạt động
    conn_tenant = get_mssql_conn()
    cursor_tenant = conn_tenant.cursor(as_dict=True)
    try:
        cursor_tenant.execute(
            'SELECT TenantID, IsActive, ExpiresAt FROM Tenants WHERE TenantID = %s',
            (tenant_id,)
        )
        t_row = cursor_tenant.fetchone()
        if not t_row:
            raise HTTPException(400, detail=f'Tenant "{tenant_id}" khong ton tai')
        if not t_row['IsActive']:
            raise HTTPException(400, detail=f'Tenant "{tenant_id}" da bi vo hieu hoa')
        # Check expiration
        if t_row['ExpiresAt']:
            now = datetime.now(timezone.utc)
            exp = t_row['ExpiresAt']
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if now > exp:
                raise HTTPException(400, detail=f'Tenant "{tenant_id}" da het han — khong the dang ky')
    finally:
        conn_tenant.close()

    conn = get_mssql_conn()
    cursor = conn.cursor()
    try:
        # Kiểm tra username đã tồn tại chưa
        cursor.execute('SELECT UserID FROM AppUsers WHERE Username = %s', (username,))
        if cursor.fetchone():
            raise HTTPException(409, detail='Ten dang nhap da ton tai')

        password_hash = hash_password(password)
        cursor.execute(
            'INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive) '
            'VALUES (%s, %s, %s, %s, 1)',
            (username, password_hash, tenant_id, role)
        )
        conn.commit()
        logger.info(f'[REGISTER] User created: {username} | role={role} | tenant={tenant_id}')
        superset_ok = superset_provision_user(username, password, tenant_id=tenant_id)
        return {
            'success': True,
            'message': f'Tai khoan "{username}" da duoc tao thanh cong',
            'superset_user_provisioned': superset_ok,
        }
    finally:
        conn.close()


def _record_login(user_id: int, ip: Optional[str], ua: Optional[str], status: str = 'success'):
    """Ghi lịch sử đăng nhập vào LoginHistory — không ném exception nếu lỗi."""
    try:
        conn = get_mssql_conn()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO LoginHistory (UserID, IPAddress, UserAgent, Status) VALUES (%s, %s, %s, %s)',
            (user_id, (ip or '')[:45], (ua or '')[:500], status)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f'[LOGIN_HISTORY] Could not record login: {e}')


@router.post('/login', response_model=LoginResponse)
def login(req: LoginRequest, request: Request = None):
    """Đăng nhập — verify qua AppUsers table (bcrypt)."""
    username = req.username.strip()
    password = req.password

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(
            'SELECT UserID, Username, PasswordHash, TenantID, Role, IsActive '
            'FROM AppUsers WHERE Username = %s',
            (username,)
        )
        row = cursor.fetchone()

        if not row:
            logger.warning(f'Login failed: user not found — {username}')
            raise HTTPException(401, detail='Sai tai khoan hoac mat khau')

        if not row['IsActive']:
            logger.warning(f'Login failed: user inactive — {username}')
            raise HTTPException(403, detail='Tai khoan bi khoa')

        tenant_id = row['TenantID']

        # Check tenant expiration
        if tenant_id:
            conn_check = get_mssql_conn()
            cursor_check = conn_check.cursor(as_dict=True)
            cursor_check.execute(
                'SELECT ExpiresAt FROM Tenants WHERE TenantID = %s',
                (tenant_id,)
            )
            tenant_row = cursor_check.fetchone()
            conn_check.close()
            if tenant_row and tenant_row['ExpiresAt']:
                now_utc = datetime.now(timezone.utc)
                exp_utc = tenant_row['ExpiresAt']
                if exp_utc.tzinfo is None:
                    exp_utc = exp_utc.replace(tzinfo=timezone.utc)
                if now_utc > exp_utc:
                    logger.warning(f'Login blocked: tenant {tenant_id} expired at {tenant_row["ExpiresAt"]}')
                    raise HTTPException(403, detail=f'Tenant "{tenant_id}" da het han vao {exp_utc.strftime("%d/%m/%Y %H:%M")} — khong the dang nhap')

        if not verify_password(password, row['PasswordHash']):
            logger.warning(f'Login failed: wrong password — {username}')
            raise HTTPException(401, detail='Sai tai khoan hoac mat khau')

        user_id = row['UserID']
        role = row['Role']
        logger.info(f'Login success: {username} | tenant={tenant_id} | role={role}')
    finally:
        conn.close()

    client_ip = request.client.host if request and request.client else None
    user_agent = request.headers.get('User-Agent') if request else None
    _record_login(user_id, client_ip, user_agent, 'success')

    access_token = create_access_token(user_id, username, tenant_id, role)
    refresh_token = create_refresh_token(user_id, username)

    return LoginResponse(
        access_token=access_token,
        token_type='bearer',
        expires_in=int(ACCESS_EXPIRE.total_seconds())
    )


@router.post('/refresh')
def refresh_token_endpoint(refresh_token: str):
    """Đổi refresh token lấy access token mới."""
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get('type') != 'refresh':
            raise HTTPException(401, detail='Refresh token khong hop le')
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail='Refresh token da het han')
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Refresh token khong hop le')

    username = payload.get('username', '')

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(
            'SELECT UserID, TenantID, Role FROM AppUsers WHERE Username = %s AND IsActive = 1',
            (username,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(401, detail='User khong con hoat dong')

    user_id = row['UserID']
    tenant_id = row['TenantID']
    role = row['Role']

    access_token = create_access_token(user_id, username, tenant_id, role)
    return {'access_token': access_token, 'token_type': 'bearer'}


@router.get('/dashboard-token', response_model=DashboardTokenResponse)
def get_dashboard_token(
    authorization: str = Header(...),
    dashboard_id: int = 1,
):
    """
    Nhận JWT từ Auth Gateway → tạo Superset Guest Token.
    dashboard_id: ID của dashboard cần truy cập (1–5, mặc định = 1)
    """
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]

    payload = decode_token(token)

    if payload.role not in ('superadmin', 'admin', 'viewer'):
        raise HTTPException(403, detail='Khong co quyen truy cap dashboard')

    dashboard_id = LEGACY_DASHBOARD_ID_MAP.get(dashboard_id, dashboard_id)

    # Validate dashboard_id (1-5)
    if dashboard_id < 1 or dashboard_id > 5:
        raise HTTPException(400, detail='Dashboard ID khong hop le (1–5)')

    try:
        admin_token = get_superset_admin_token()
    except HTTPException:
        raise HTTPException(502, detail='Khong ket noi duoc Superset')

    embedded_uuid = get_or_create_embedded_dashboard_uuid(dashboard_id, admin_token)

    # Xác định RLS clause — dùng TenantID (capital) vì MSSQL column name
    if payload.role in ('superadmin', 'admin') and payload.tenant_id is None:
        rls_clause = '1=1'
        username_for_token = f'admin_{payload.user_id}'
    else:
        rls_clause = f"TenantID = '{payload.tenant_id}'"
        username_for_token = f'tenant_{payload.tenant_id}'

    # Tạo guest token cho dashboard cụ thể + RLS filter
    try:
        r = requests.post(
            f'{SUPERSET_URL}/api/v1/security/guest_token/',
            headers={'Authorization': f'Bearer {admin_token}'},
            json={
                'user': {
                    'username': username_for_token,
                    'first_name': payload.role,
                    'last_name': payload.tenant_id or 'admin',
                },
                'resources': [
                    {'type': 'dashboard', 'id': embedded_uuid},
                ],
                'rls': [
                    {'clause': rls_clause}
                ]
            },
            timeout=30
        )
    except requests.RequestException as e:
        logger.error(f'Guest token error: {e}')
        raise HTTPException(502, detail=f'Loi tao guest token Superset: {str(e)}')

    if r.status_code != 200:
        logger.error(f'Guest token failed: {r.status_code} — {r.text}')
        raise HTTPException(502, detail=f'Tao guest token that bai: {r.text}')

    guest_token = r.json().get('token', '')
    dashboard_url = f'{SUPERSET_PUBLIC_URL}/embedded/{embedded_uuid}'

    logger.info(
        f'Guest token issued: username={payload.username} | '
        f'dashboard={dashboard_id} | embedded={embedded_uuid} | '
        f'tenant={payload.tenant_id} | role={payload.role}'
    )

    return DashboardTokenResponse(
        dashboard_url=dashboard_url,
        dashboard_id=dashboard_id,
        embedded_dashboard_uuid=embedded_uuid,
        guest_token=guest_token,
        token_type='bearer',
        expires_in=3600
    )


@router.get('/me', response_model=UserInfo)
def get_current_user(authorization: str = Header(...)):
    """Trả về thông tin user hiện tại từ JWT token."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]

    payload = decode_token(token)

    username = payload.username if hasattr(payload, 'username') and payload.username else ''
    return UserInfo(
        user_id=payload.user_id,
        username=username,
        tenant_id=payload.tenant_id,
        role=payload.role,
        is_active=True
    )


@router.get('/me/profile', response_model=UserProfile)
def get_profile(authorization: str = Header(...)):
    """Trả về full hồ sơ người dùng bao gồm display_name, email, phone, avatar."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    payload = decode_token(authorization[7:])

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(
            'SELECT UserID, Username, DisplayName, Email, Phone, AvatarData, '
            'TenantID, Role, IsActive, CreatedAt FROM AppUsers WHERE UserID = %s',
            (payload.user_id,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(404, detail='User khong ton tai')

    created_at = row['CreatedAt'].strftime('%d/%m/%Y %H:%M') if row.get('CreatedAt') else None
    return UserProfile(
        user_id=row['UserID'],
        username=row['Username'],
        display_name=row.get('DisplayName'),
        email=row.get('Email'),
        phone=row.get('Phone'),
        avatar_data=row.get('AvatarData'),
        tenant_id=row.get('TenantID'),
        role=row['Role'],
        is_active=bool(row['IsActive']),
        created_at=created_at,
    )


@router.put('/me/profile')
def update_profile(req: UpdateProfileRequest, authorization: str = Header(...)):
    """Cập nhật display_name, email, phone."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    payload = decode_token(authorization[7:])

    conn = get_mssql_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE AppUsers SET DisplayName = %s, Email = %s, Phone = %s WHERE UserID = %s',
            (req.display_name, req.email, req.phone, payload.user_id)
        )
        conn.commit()
    finally:
        conn.close()

    logger.info(f'[PROFILE] Updated profile: user_id={payload.user_id}')
    return {'success': True, 'message': 'Ho so da duoc cap nhat'}


@router.put('/me/password')
def change_password(req: ChangePasswordRequest, authorization: str = Header(...)):
    """Đổi mật khẩu — yêu cầu xác minh mật khẩu hiện tại."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    payload = decode_token(authorization[7:])

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(
            'SELECT PasswordHash FROM AppUsers WHERE UserID = %s AND IsActive = 1',
            (payload.user_id,)
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(404, detail='User khong ton tai')

        if not verify_password(req.current_password, row['PasswordHash']):
            raise HTTPException(400, detail='Mat khau hien tai khong dung')

        new_hash = hash_password(req.new_password)
        cursor.execute(
            'UPDATE AppUsers SET PasswordHash = %s WHERE UserID = %s',
            (new_hash, payload.user_id)
        )
        conn.commit()
    finally:
        conn.close()

    logger.info(f'[PASSWORD] Changed password: user_id={payload.user_id}')
    return {'success': True, 'message': 'Mat khau da duoc doi thanh cong'}


@router.post('/me/avatar')
def update_avatar(req: AvatarUploadRequest, authorization: str = Header(...)):
    """Upload avatar dưới dạng base64 data URL."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    payload = decode_token(authorization[7:])

    # Validate là data URL hợp lệ
    data = req.avatar_data.strip()
    if not data.startswith('data:image/'):
        raise HTTPException(400, detail='Avatar phai la data URL dang image')

    # Giới hạn kích thước ~5MB sau khi base64
    if len(data) > 7_000_000:
        raise HTTPException(400, detail='Anh qua lon — toi da 5MB')

    conn = get_mssql_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE AppUsers SET AvatarData = %s WHERE UserID = %s',
            (data, payload.user_id)
        )
        conn.commit()
    finally:
        conn.close()

    logger.info(f'[AVATAR] Updated avatar: user_id={payload.user_id}')
    return {'success': True, 'message': 'Anh dai dien da duoc cap nhat'}


@router.delete('/me/avatar')
def remove_avatar(authorization: str = Header(...)):
    """Xóa avatar — quay về initials mặc định."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    payload = decode_token(authorization[7:])

    conn = get_mssql_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE AppUsers SET AvatarData = NULL WHERE UserID = %s',
            (payload.user_id,)
        )
        conn.commit()
    finally:
        conn.close()

    return {'success': True}


@router.get('/me/login-history')
def get_login_history(authorization: str = Header(...)):
    """Trả về 20 phiên đăng nhập gần nhất."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    payload = decode_token(authorization[7:])

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(
            'SELECT TOP 20 HistoryID, LoginAt, IPAddress, UserAgent, Status '
            'FROM LoginHistory WHERE UserID = %s ORDER BY LoginAt DESC',
            (payload.user_id,)
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    items = [
        LoginHistoryItem(
            history_id=r['HistoryID'],
            login_at=r['LoginAt'].strftime('%d/%m/%Y %H:%M:%S') if r.get('LoginAt') else '',
            ip_address=r.get('IPAddress'),
            user_agent=r.get('UserAgent'),
            status=r.get('Status', 'success'),
        )
        for r in rows
    ]
    return {'items': [i.model_dump() for i in items]}
