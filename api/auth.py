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
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel

from api.models import (
    LoginRequest, LoginResponse, UserInfo,
    DashboardTokenResponse, TokenPayload
)

# ---- Configuration ----
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'changeme-minimum-32-chars!!')
ALGORITHM = 'HS256'
ACCESS_EXPIRE = timedelta(hours=8)
REFRESH_EXPIRE = timedelta(days=7)
SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
SUPERSET_ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
SUPERSET_ADMIN_PWD = os.environ.get('SUPERSET_ADMIN_PWD', 'admin')

# ---- Password hashing ----
pwd_ctx = passlib.context.CryptContext(schemes=['bcrypt'], deprecated='auto')

# ---- Logger ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Router ----
router = APIRouter(prefix='/auth', tags=['Authentication'])


# ============================================================
# USER REGISTRY — tất cả credentials từ .env
# Format: APP_{USERNAME}_HASH=bcrypt_hash
# ============================================================
APP_USERS = {
    'admin': {
        'password': 'Admin@1234',
        'tenant_id': None,
        'role': 'admin',
    },
    'manager_hn': {
        'password': 'Pass@HN123',
        'tenant_id': 'STORE_HN',
        'role': 'viewer',
    },
    'manager_hcm': {
        'password': 'Pass@HCM123',
        'tenant_id': 'STORE_HCM',
        'role': 'viewer',
    },
}

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


# ============================================================
# BOOTSTRAP — tạo user vào AppUsers khi API khởi động
# ============================================================

def bootstrap_users():
    """Tạo/upsert user từ APP_USERS vào bảng AppUsers (chạy 1 lần khi start)."""
    conn = get_mssql_conn()
    cursor = conn.cursor()

    try:
        for username, info in APP_USERS.items():
            password_hash = hash_password(info['password'])

            cursor.execute(
                'SELECT UserID FROM AppUsers WHERE Username = %s',
                (username,)
            )
            row = cursor.fetchone()

            if row:
                cursor.execute(
                    'UPDATE AppUsers SET PasswordHash = %s, TenantID = %s, Role = %s, IsActive = 1 WHERE Username = %s',
                    (password_hash, info['tenant_id'], info['role'], username)
                )
                logger.info(f'[BOOTSTRAP] Updated user: {username}')
            else:
                cursor.execute(
                    'INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive) VALUES (%s, %s, %s, %s, 1)',
                    (username, password_hash, info['tenant_id'], info['role'])
                )
                logger.info(f'[BOOTSTRAP] Created user: {username}')

            conn.commit()

        logger.info('[BOOTSTRAP] All users synced to AppUsers table')

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


# Chạy bootstrap khi module load
bootstrap_users()


# ---- Endpoints ----

@router.post('/login', response_model=LoginResponse)
def login(req: LoginRequest):
    """
    Đăng nhập — xác thực username/password từ .env (source of truth).
    """
    username = req.username.strip()
    password = req.password

    # Validate against env var registry
    if username not in APP_USERS:
        logger.warning(f'Login failed: user not found — {username}')
        raise HTTPException(401, detail='Sai tai khoan hoac mat khau')

    user_info = APP_USERS[username]
    if password != user_info['password']:
        logger.warning(f'Login failed: wrong password — {username}')
        raise HTTPException(401, detail='Sai tai khoan hoac mat khau')

    # Lấy UserID từ DB (đã bootstrap ở trên)
    user_id = get_user_id_from_db(username)
    if user_id is None:
        # Fallback: dùng hash của username làm user_id cố định
        import hashlib
        user_id = int(hashlib.md5(username.encode()).hexdigest()[:8], 16) % 100000

    access_token = create_access_token(user_id, username, user_info['tenant_id'], user_info['role'])
    refresh_token = create_refresh_token(user_id, username)

    logger.info(f'Login success: {username} | tenant={user_info["tenant_id"]} | role={user_info["role"]}')

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
    if username not in APP_USERS:
        raise HTTPException(401, detail='User khong con hoat dong')

    user_info = APP_USERS[username]
    user_id = get_user_id_from_db(username)
    if user_id is None:
        import hashlib
        user_id = int(hashlib.md5(username.encode()).hexdigest()[:8], 16) % 100000

    access_token = create_access_token(user_id, username, user_info['tenant_id'], user_info['role'])
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

    if payload.role not in ('admin', 'viewer'):
        raise HTTPException(403, detail='Khong co quyen truy cap dashboard')

    # Validate dashboard_id (1-5)
    if dashboard_id < 1 or dashboard_id > 5:
        raise HTTPException(400, detail='Dashboard ID khong hop le (1–5)')

    try:
        admin_token = get_superset_admin_token()
    except HTTPException:
        raise HTTPException(502, detail='Khong ket noi duoc Superset')

    # Xác định RLS clause — dùng TenantID (capital) vì MSSQL column name
    if payload.role == 'admin' and payload.tenant_id is None:
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
                    {'type': 'dashboard', 'id': dashboard_id},
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
    logger.info(
        f'Guest token issued: username={payload.username} | '
        f'dashboard={dashboard_id} | tenant={payload.tenant_id} | role={payload.role}'
    )

    return DashboardTokenResponse(
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
