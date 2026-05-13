# ============================================================
# FILE: api/management.py
# Mô tả: API CRUD cho Tenant, User, ETL Management (Admin only)
# ============================================================

import os
import re
import pymssql as mssql
import jwt
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from passlib.context import CryptContext
from pydantic import BaseModel

from api.superset_provision import (
    provision_tenant as superset_provision_tenant,
    provision_user as superset_provision_user,
    deactivate_user as superset_deactivate_user,
    deprovision_tenant as superset_deprovision_tenant,
)

# ---- Configuration ----
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'changeme-minimum-32-chars!!')
ALGORITHM = 'HS256'

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_ROOT = PROJECT_ROOT / 'data'
TENANT_ID_RE = re.compile(r'^[A-Za-z0-9_]{1,20}$')
USERNAME_RE = re.compile(r'^[A-Za-z0-9_]{3,100}$')
AUTO_TENANT_PREFIX = os.environ.get('AUTO_TENANT_PREFIX', 'tenant').strip() or 'tenant'
try:
    AUTO_TENANT_ID_WIDTH = int(os.environ.get('AUTO_TENANT_ID_WIDTH', '3'))
except ValueError:
    AUTO_TENANT_ID_WIDTH = 3

pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated='auto')
logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api', tags=['Management'])


# ---- Helpers ----

def get_mssql_conn():
    return mssql.connect(
        server=os.environ.get('MSSQL_SERVER', 'localhost'),
        user=os.environ.get('MSSQL_USER', 'sa'),
        password=os.environ.get('MSSQL_PASSWORD', ''),
        database=os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant')
    )


def require_admin(authorization: str = Header(...)):
    """Dependency — chỉ admin (superadmin hoặc tenant-admin) mới được truy cập."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        role = payload.get('role', '')
        if role not in ('superadmin', 'admin'):
            raise HTTPException(403, detail='Chi admin moi co quyen truy cap')
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail='Token da het han')
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Token khong hop le')


def is_superadmin(payload: dict) -> bool:
    """True nếu user là superadmin (toàn quyền hệ thống)."""
    return payload.get('role') == 'superadmin' and payload.get('tenant_id') is None


def require_auth(authorization: str = Header(...)):
    """Dependency — bất kỳ user đã đăng nhập."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail='Token da het han')
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Token khong hop le')


def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)


def validate_tenant_id(tenant_id: str) -> None:
    if not TENANT_ID_RE.match(tenant_id):
        raise HTTPException(
            400,
            detail='TenantID chi chap nhan chu cai, so, dau gach duoi va toi da 20 ky tu'
        )


def validate_username(username: str) -> None:
    if not USERNAME_RE.match(username):
        raise HTTPException(
            400,
            detail='Username chi chap nhan chu cai, so, dau gach duoi va tu 3-100 ky tu'
        )


def parse_expires_at(expires_at: Optional[str]) -> Optional[datetime]:
    if not expires_at or not expires_at.strip():
        return None
    try:
        return datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            400,
            detail='Dinh dang ExpiresAt khong hop le (VD: 2026-12-31T23:59:59)'
        )


def ensure_tenant_dirs(tenant_id: str) -> None:
    tenant_dir = DATA_ROOT / tenant_id / 'logs'
    tenant_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f'[ADMIN] Ensured ETL logs directory: {tenant_dir}')


def generate_tenant_id(cursor) -> str:
    """Sinh TenantID dang tenant_001, tenant_002... theo DB hien tai."""
    prefix = AUTO_TENANT_PREFIX
    if not re.match(r'^[A-Za-z0-9_]{1,12}$', prefix):
        raise HTTPException(500, detail='AUTO_TENANT_PREFIX khong hop le')

    like_pattern = f'{prefix}[_]%'
    cursor.execute('SELECT TenantID FROM Tenants WHERE TenantID LIKE %s', (like_pattern,))
    suffix_re = re.compile(rf'^{re.escape(prefix)}_(\d+)$')
    max_seq = 0
    for row in cursor.fetchall():
        match = suffix_re.match(row[0])
        if match:
            max_seq = max(max_seq, int(match.group(1)))

    next_seq = max_seq + 1
    while True:
        tenant_id = f'{prefix}_{next_seq:0{AUTO_TENANT_ID_WIDTH}d}'
        if len(tenant_id) > 20:
            raise HTTPException(500, detail='TenantID tu sinh vuot qua 20 ky tu')
        cursor.execute('SELECT 1 FROM Tenants WHERE TenantID = %s', (tenant_id,))
        if not cursor.fetchone():
            return tenant_id
        next_seq += 1


def create_tenant_record(
    cursor,
    tenant_id: str,
    tenant_name: Optional[str],
    file_path: Optional[str],
    expires_at: Optional[str],
) -> None:
    validate_tenant_id(tenant_id)
    tenant_name = (tenant_name or f'Tenant {tenant_id}').strip()
    tenant_file_path = (file_path or f'./data/{tenant_id}/').strip()
    expires_dt = parse_expires_at(expires_at)
    cursor.execute(
        'INSERT INTO Tenants (TenantID, TenantName, FilePath, IsActive, ExpiresAt) '
        'VALUES (%s, %s, %s, 1, %s)',
        (tenant_id, tenant_name, tenant_file_path, expires_dt)
    )
    ensure_tenant_dirs(tenant_id)


# ---- Pydantic Models ----

class TenantCreate(BaseModel):
    tenant_id: str
    tenant_name: str
    file_path: Optional[str] = None
    expires_at: Optional[str] = None  # ISO datetime string


class TenantUpdate(BaseModel):
    tenant_name: Optional[str] = None
    file_path: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[str] = None  # ISO datetime string, None = không hết hạn


class UserCreate(BaseModel):
    username: str
    password: str
    tenant_id: Optional[str] = None
    tenant_name: Optional[str] = None
    file_path: Optional[str] = None
    expires_at: Optional[str] = None
    role: str = 'viewer'


class UserUpdate(BaseModel):
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================
# TENANT MANAGEMENT
# ============================================================

@router.get('/tenants')
def list_tenants(payload=Depends(require_admin)):
    """Danh sách tất cả tenant (Admin only)."""
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT TenantID, TenantName, FilePath, IsActive, ExpiresAt, CreatedAt FROM Tenants ORDER BY CreatedAt DESC')
    rows = cursor.fetchall()
    conn.close()

    return {
        'tenants': [
            {
                'tenant_id': r['TenantID'],
                'tenant_name': r['TenantName'],
                'file_path': r['FilePath'],
                'is_active': bool(r['IsActive']),
                'expires_at': r['ExpiresAt'].isoformat() if r['ExpiresAt'] else None,
                'created_at': r['CreatedAt'].isoformat() if r['CreatedAt'] else None,
            }
            for r in rows
        ]
    }


@router.post('/tenants')
def create_tenant(data: TenantCreate, payload=Depends(require_admin)):
    """Tạo tenant mới — chỉ superadmin."""
    if not is_superadmin(payload):
        raise HTTPException(403, detail='Chi superadmin moi co quyen tao tenant')
    validate_tenant_id(data.tenant_id)
    conn = get_mssql_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT 1 FROM Tenants WHERE TenantID = %s', (data.tenant_id,))
        if cursor.fetchone():
            raise HTTPException(400, detail='TenantID da ton tai')

        create_tenant_record(cursor, data.tenant_id, data.tenant_name, data.file_path, data.expires_at)
        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f'[ADMIN] Failed to create tenant {data.tenant_id}: {e}', exc_info=True)
        raise HTTPException(500, detail='Loi khi tao tenant')
    finally:
        conn.close()
    logger.info(f'[ADMIN] Created tenant: {data.tenant_id} by user_id={payload["user_id"]}')

    # Auto-provision Superset role + RLS rules cho tenant mới
    superset_ok = superset_provision_tenant(data.tenant_id)

    return {
        'success': True,
        'tenant_id': data.tenant_id,
        'superset_tenant_provisioned': superset_ok,
    }


@router.put('/tenants/{tenant_id}')
def update_tenant(tenant_id: str, data: TenantUpdate, payload=Depends(require_admin)):
    """Cập nhật tenant — chỉ superadmin."""
    if not is_superadmin(payload):
        raise HTTPException(403, detail='Chi superadmin moi co quyen sua tenant')
    conn = get_mssql_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Tenants WHERE TenantID = %s', (tenant_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(404, detail='Tenant khong ton tai')

    updates = []
    params = []
    if data.tenant_name is not None:
        updates.append('TenantName = %s')
        params.append(data.tenant_name)
    if data.file_path is not None:
        updates.append('FilePath = %s')
        params.append(data.file_path)
    if data.is_active is not None:
        updates.append('IsActive = %s')
        params.append(1 if data.is_active else 0)
    if data.expires_at is not None or data.expires_at == '':
        # '' or null = no expiration
        if data.expires_at and data.expires_at.strip():
            from datetime import datetime
            try:
                expires_dt = datetime.fromisoformat(data.expires_at.replace('Z', '+00:00'))
                updates.append('ExpiresAt = %s')
                params.append(expires_dt)
            except ValueError:
                raise HTTPException(400, detail='Dinh dang ExpiresAt khong hop le (VD: 2026-12-31T23:59:59)')
        else:
            updates.append('ExpiresAt = NULL')

    if updates:
        params.append(tenant_id)
        cursor.execute(f"UPDATE Tenants SET {', '.join(updates)} WHERE TenantID = %s", params)
        conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Updated tenant: {tenant_id}')
    return {'success': True}


@router.delete('/tenants/{tenant_id}')
def delete_tenant(tenant_id: str, payload=Depends(require_admin)):
    """Xóa tenant — chỉ superadmin. Soft delete."""
    if not is_superadmin(payload):
        raise HTTPException(403, detail='Chi superadmin moi co quyen xoa tenant')

    conn = get_mssql_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Tenants WHERE TenantID = %s', (tenant_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(404, detail='Tenant khong ton tai')

    cursor.execute('UPDATE Tenants SET IsActive = 0 WHERE TenantID = %s', (tenant_id,))
    conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Deactivated tenant: {tenant_id}')

    superset_deprovision_tenant(tenant_id)

    return {'success': True}


# ============================================================
# USER MANAGEMENT
# ============================================================

@router.get('/users')
def list_users(payload=Depends(require_admin)):
    """
    Danh sách user.
    - superadmin: thấy TẤT CẢ user
    - admin: chỉ thấy user thuộc tenant của mình
    """
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    if is_superadmin(payload):
        cursor.execute('SELECT UserID, Username, TenantID, Role, IsActive, CreatedAt FROM AppUsers ORDER BY CreatedAt DESC')
    else:
        # Admin: chỉ thấy user thuộc tenant của mình
        my_tenant = payload.get('tenant_id')
        if my_tenant is None:
            # Admin chưa được gán tenant → trả danh sách rỗng
            conn.close()
            return {'users': []}
        cursor.execute(
            'SELECT UserID, Username, TenantID, Role, IsActive, CreatedAt FROM AppUsers WHERE TenantID = %s ORDER BY CreatedAt DESC',
            (my_tenant,)
        )
    rows = cursor.fetchall()
    conn.close()

    return {
        'users': [
            {
                'user_id': r['UserID'],
                'username': r['Username'],
                'tenant_id': r['TenantID'],
                'role': r['Role'],
                'is_active': bool(r['IsActive']),
                'created_at': r['CreatedAt'].isoformat() if r['CreatedAt'] else None,
            }
            for r in rows
        ]
    }


@router.get('/users/tenant/{tenant_id}')
def list_users_by_tenant(tenant_id: str, payload=Depends(require_admin)):
    """Danh sách user theo tenant."""
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT UserID, Username, TenantID, Role, IsActive FROM AppUsers WHERE TenantID = %s', (tenant_id,))
    rows = cursor.fetchall()
    conn.close()
    return {'users': [{'user_id': r['UserID'], 'username': r['Username'], 'tenant_id': r['TenantID'],
                       'role': r['Role'], 'is_active': bool(r['IsActive'])} for r in rows]}


@router.post('/admin/users')
@router.post('/users')
def create_user(data: UserCreate, payload=Depends(require_admin)):
    """
    Tạo user mới.
    - superadmin: tạo bất kỳ user nào
      + role=admin không có tenant_id: tự sinh TenantID và tạo tenant mới
      + role=admin có tenant_id chưa tồn tại: tạo tenant mới với TenantID đó
    - admin: chỉ tạo viewer thuộc tenant của mình
    """
    username = data.username.strip()
    validate_username(username)

    if not is_superadmin(payload):
        my_tenant = payload.get('tenant_id')
        # Admin tenant chỉ được tạo user viewer thuộc tenant của mình
        if data.role not in ('viewer',):
            raise HTTPException(403, detail='Admin chi co quyen tao user viewer')
        # Admin luôn phải có tenant_id để tạo user
        if not my_tenant:
            raise HTTPException(403, detail='Tai khoan admin chua duoc gan tenant — lien he superadmin de assign tenant')
        # Nếu gửi tenant_id cụ thể thì phải khớp với tenant của mình
        if data.tenant_id and data.tenant_id != my_tenant:
            raise HTTPException(403, detail='Admin chi co quyen tao user thuoc tenant cua minh')
        # Không gửi tenant_id → tự động dùng tenant của admin đang đăng nhập
    elif data.role not in ('superadmin', 'admin', 'viewer'):
        raise HTTPException(400, detail='Role phai la superadmin, admin hoac viewer')

    conn = get_mssql_conn()
    cursor = conn.cursor()
    created_tenant_id = None
    tenant_for_user = None
    superset_tenant_ok = None
    superset_user_ok = None
    try:
        cursor.execute('SELECT 1 FROM AppUsers WHERE Username = %s', (username,))
        if cursor.fetchone():
            raise HTTPException(400, detail='Username da ton tai')

        if not is_superadmin(payload):
            tenant_for_user = payload.get('tenant_id')
            cursor.execute(
                'SELECT 1 FROM Tenants WHERE TenantID = %s AND IsActive = 1',
                (tenant_for_user,)
            )
            if not cursor.fetchone():
                raise HTTPException(400, detail='Tenant cua admin khong hop le hoac khong hoat dong')
        elif data.role == 'superadmin':
            if data.tenant_id:
                raise HTTPException(400, detail='Superadmin khong duoc gan TenantID')
            tenant_for_user = None
        elif data.role == 'viewer':
            if not data.tenant_id:
                raise HTTPException(400, detail='Viewer bat buoc phai co TenantID')
            validate_tenant_id(data.tenant_id)
            cursor.execute(
                'SELECT 1 FROM Tenants WHERE TenantID = %s AND IsActive = 1',
                (data.tenant_id,)
            )
            if not cursor.fetchone():
                raise HTTPException(400, detail='TenantID khong hop le hoac khong hoat dong')
            tenant_for_user = data.tenant_id
        else:  # superadmin tạo tenant-admin
            requested_tenant_id = data.tenant_id.strip() if data.tenant_id else None
            if requested_tenant_id:
                validate_tenant_id(requested_tenant_id)
                cursor.execute(
                    'SELECT TenantID, IsActive FROM Tenants WHERE TenantID = %s',
                    (requested_tenant_id,)
                )
                tenant_row = cursor.fetchone()
                if tenant_row:
                    if not tenant_row[1]:
                        raise HTTPException(400, detail='TenantID da ton tai nhung dang bi vo hieu hoa')
                    tenant_for_user = requested_tenant_id
                else:
                    tenant_for_user = requested_tenant_id
                    create_tenant_record(
                        cursor,
                        tenant_for_user,
                        data.tenant_name,
                        data.file_path,
                        data.expires_at,
                    )
                    created_tenant_id = tenant_for_user
            else:
                tenant_for_user = generate_tenant_id(cursor)
                create_tenant_record(
                    cursor,
                    tenant_for_user,
                    data.tenant_name or f'Tenant cua {username}',
                    data.file_path,
                    data.expires_at,
                )
                created_tenant_id = tenant_for_user

            cursor.execute(
                'SELECT 1 FROM AppUsers WHERE TenantID = %s AND Role = %s AND IsActive = 1',
                (tenant_for_user, 'admin')
            )
            if cursor.fetchone():
                raise HTTPException(
                    403,
                    detail='Tenant nay da co admin dang hoat dong. Chi duoc phep tao 1 admin cho moi tenant.'
                )

        password_hash = hash_password(data.password)
        cursor.execute(
            'INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive) VALUES (%s, %s, %s, %s, 1)',
            (username, password_hash, tenant_for_user, data.role)
        )
        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f'[ADMIN] Failed to create user {username}: {e}', exc_info=True)
        raise HTTPException(500, detail='Loi khi tao user')
    finally:
        conn.close()

    logger.info(f'[ADMIN] Created user: {username} role={data.role} tenant={tenant_for_user}')

    # Auto-provision Superset user (role TenantViewer/Gamma + RLS_<tenant_id>)
    # Superadmin (role=superadmin, tenant_id=None) → role Admin trong Superset
    if data.role == 'superadmin':
        superset_user_ok = superset_provision_user(username, data.password, tenant_id=None)
    elif tenant_for_user:
        superset_tenant_ok = superset_provision_tenant(tenant_for_user)
        superset_user_ok = superset_provision_user(username, data.password, tenant_id=tenant_for_user)

    return {
        'success': True,
        'username': username,
        'tenant_id': tenant_for_user,
        'tenant_created': created_tenant_id is not None,
        'created_tenant_id': created_tenant_id,
        'superset_tenant_provisioned': superset_tenant_ok,
        'superset_user_provisioned': superset_user_ok,
    }


@router.get('/users/{user_id}')
def get_user_detail(user_id: int, payload=Depends(require_admin)):
    """
    Chi tiết user.
    - superadmin: xem bất kỳ user nào
    - admin: chỉ xem user thuộc tenant của mình
    """
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    try:
        cursor.execute(
            'SELECT UserID, Username, DisplayName, Email, Phone, TenantID, Role, IsActive, CreatedAt '
            'FROM AppUsers WHERE UserID = %s',
            (user_id,)
        )
        row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(404, detail='User khong ton tai')

    if not is_superadmin(payload):
        my_tenant = payload.get('tenant_id')
        if my_tenant != row['TenantID']:
            raise HTTPException(403, detail='Admin chi co quyen xem user thuoc tenant cua minh')

    return {
        'user': {
            'user_id': row['UserID'],
            'username': row['Username'],
            'display_name': row['DisplayName'],
            'email': row['Email'],
            'phone': row['Phone'],
            'tenant_id': row['TenantID'],
            'role': row['Role'],
            'is_active': bool(row['IsActive']),
            'created_at': row['CreatedAt'].isoformat() if row['CreatedAt'] else None,
        }
    }


@router.put('/users/{user_id}')
def update_user(user_id: int, data: UserUpdate, payload=Depends(require_admin)):
    """
    Cập nhật user.
    - superadmin: cập nhật bất kỳ user nào
    - admin: chỉ cập nhật user thuộc tenant của mình
    """
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT UserID, Username, TenantID, Role FROM AppUsers WHERE UserID = %s', (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, detail='User khong ton tai')

    # Quyền: superadmin thì được sửa tất cả, admin chỉ được sửa user cùng tenant
    if not is_superadmin(payload):
        my_tenant = payload.get('tenant_id')
        if my_tenant != row['TenantID']:
            conn.close()
            raise HTTPException(403, detail='Admin chi co quyen sua user thuoc tenant cua minh')
        # Admin không được nâng quyền user lên superadmin
        if data.role == 'superadmin' or data.role == 'admin':
            conn.close()
            raise HTTPException(403, detail='Admin khong duoc thay doi vai tro cua user')

    updates = []
    params = []
    if data.password is not None:
        updates.append('PasswordHash = %s')
        params.append(hash_password(data.password))
    if data.role is not None:
        if data.role not in ('superadmin', 'admin', 'viewer'):
            conn.close()
            raise HTTPException(400, detail='Role phai la superadmin, admin hoac viewer')
        updates.append('Role = %s')
        params.append(data.role)
    if data.is_active is not None:
        updates.append('IsActive = %s')
        params.append(1 if data.is_active else 0)

    if updates:
        params.append(user_id)
        cursor.execute(f"UPDATE AppUsers SET {', '.join(updates)} WHERE UserID = %s", params)
        conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Updated user_id={user_id} by {payload.get("username")}')
    return {'success': True}


@router.delete('/users/{user_id}')
def delete_user(user_id: int, payload=Depends(require_admin)):
    """
    Xóa user — soft delete.
    - superadmin: xóa bất kỳ user nào (trừ tài khoản superadmin mặc định)
    - admin: chỉ xóa user thuộc tenant của mình
    """
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT Username, TenantID, Role FROM AppUsers WHERE UserID = %s', (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, detail='User khong ton tai')

    # Quyền: superadmin được xóa tất cả, admin chỉ được xóa user cùng tenant
    if not is_superadmin(payload):
        my_tenant = payload.get('tenant_id')
        if row['TenantID'] != my_tenant:
            conn.close()
            raise HTTPException(403, detail='Admin chi co quyen xoa user thuoc tenant cua minh')

    if row['Username'] == 'admin':
        conn.close()
        raise HTTPException(400, detail='Khong the xoa tai khoan admin')

    cursor.execute('UPDATE AppUsers SET IsActive = 0 WHERE UserID = %s', (user_id,))
    conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Deactivated user_id={user_id} by {payload.get("username")}')

    superset_deactivate_user(row['Username'])

    return {'success': True}


# ============================================================
# ETL MANAGEMENT
# ============================================================

@router.get('/etl/logs')
def get_etl_logs(
    limit: int = 50,
    tenant_id: Optional[str] = None,
    payload=Depends(require_admin)
):
    """Danh sách ETL logs (Admin only)."""
    if not is_superadmin(payload):
        tenant_id = payload.get('tenant_id')
        if not tenant_id:
            return {'logs': []}

    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)

    # Use actual column names from the DB schema
    if tenant_id:
        cursor.execute(
            'SELECT LogID, TenantID, TableName, StepName, RowsProcessed, '
            'RowsInserted, RowsUpdated, RowsRejected, DurationSec, '
            'Status, ErrorMessage, CreatedAt '
            'FROM ETLLogs WHERE TenantID = %s ORDER BY CreatedAt DESC',
            (tenant_id,)
        )
    else:
        cursor.execute(
            'SELECT LogID, TenantID, TableName, StepName, RowsProcessed, '
            'RowsInserted, RowsUpdated, RowsRejected, DurationSec, '
            'Status, ErrorMessage, CreatedAt '
            'FROM ETLLogs ORDER BY CreatedAt DESC'
        )

    rows = cursor.fetchall()
    conn.close()

    return {
        'logs': [
            {
                'log_id': r['LogID'],
                'tenant_id': r['TenantID'],
                'source_table': r['TableName'],
                'step_name': r['StepName'],
                'rows_extracted': r['RowsProcessed'],
                'rows_inserted': r['RowsInserted'],
                'rows_rejected': r['RowsRejected'],
                'start_time': r['CreatedAt'].isoformat() if r['CreatedAt'] else None,
                'end_time': r['CreatedAt'].isoformat() if r['CreatedAt'] else None,
                'duration_seconds': r['DurationSec'],
                'status': r['Status'],
                'error_message': r['ErrorMessage'],
            }
            for r in rows[:limit]
        ]
    }


@router.get('/etl/watermarks')
def get_watermarks(payload=Depends(require_admin)):
    """Danh sách watermark của tất cả tenant (Admin only)."""
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    if is_superadmin(payload):
        cursor.execute(
            'SELECT WatermarkID, TenantID, TableName, LastRunTime, LastRunStatus, UpdatedAt '
            'FROM ETL_Watermark ORDER BY TenantID, TableName'
        )
    else:
        tenant_id = payload.get('tenant_id')
        if not tenant_id:
            conn.close()
            return {'watermarks': []}
        cursor.execute(
            'SELECT WatermarkID, TenantID, TableName, LastRunTime, LastRunStatus, UpdatedAt '
            'FROM ETL_Watermark WHERE TenantID = %s ORDER BY TenantID, TableName',
            (tenant_id,)
        )
    rows = cursor.fetchall()
    conn.close()

    return {
        'watermarks': [
            {
                'watermark_id': r['WatermarkID'],
                'tenant_id': r['TenantID'],
                'table_name': r['TableName'],
                'last_run_time': r['LastRunTime'].isoformat() if r['LastRunTime'] else None,
                'last_status': r['LastRunStatus'],
                'updated_at': r['UpdatedAt'].isoformat() if r['UpdatedAt'] else None,
            }
            for r in rows
        ]
    }


@router.post('/etl/trigger/{tenant_id}')
def trigger_etl(tenant_id: str, payload=Depends(require_admin)):
    """Trigger ETL cho 1 tenant cụ thể (Admin only)."""
    import subprocess
    import sys

    if not is_superadmin(payload) and payload.get('tenant_id') != tenant_id:
        raise HTTPException(403, detail='Admin chi duoc trigger ETL cho tenant cua minh')

    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etl', 'orchestrator', 'main_etl.py')

    if not os.path.exists(script_path):
        raise HTTPException(500, detail='ETL script khong ton tai')

    env = {
        **os.environ,
        'MSSQL_SERVER': os.environ.get('MSSQL_SERVER', 'localhost'),
        'MSSQL_USER': os.environ.get('MSSQL_USER', 'sa'),
        'MSSQL_PASSWORD': os.environ.get('MSSQL_PASSWORD', ''),
        'MSSQL_DATABASE': os.environ.get('MSSQL_DATABASE', 'DWH_MultiTenant'),
    }

    try:
        result = subprocess.run(
            [sys.executable, script_path, '--tenant', tenant_id],
            capture_output=True,
            text=True,
            timeout=300,
            env=env
        )
        success = result.returncode == 0
        logger.info(f'[ADMIN] ETL triggered for {tenant_id}: exit={result.returncode}')
        return {
            'success': success,
            'tenant_id': tenant_id,
            'stdout': result.stdout[-500:] if result.stdout else '',
            'stderr': result.stderr[-500:] if result.stderr else '',
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(504, detail='ETL chay qua 5 phut')
    except Exception as e:
        raise HTTPException(500, detail=f'Loi khi trigger ETL: {str(e)}')


# ============================================================
# KPI SUMMARY
# ============================================================

@router.get('/kpi')
def get_kpi_summary(authorization: str = Header(...)):
    """
    Trả về KPI summary cho user hiện tại.
    - Viewer: chỉ thấy data của tenant mình
    - Admin: thấy toàn bộ data
    """
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except:
        raise HTTPException(401, detail='Token khong hop le')

    conn = get_mssql_conn()
    cursor = conn.cursor()

    is_viewer = payload.get('role') == 'viewer' and payload.get('tenant_id')
    is_admin_level = payload.get('role') in ('superadmin', 'admin')

    if is_viewer:
        tid = payload['tenant_id']
        cursor.execute(
            'SELECT ISNULL(SUM(Revenue),0), ISNULL(SUM(Profit),0), '
            'COUNT(*), COUNT(DISTINCT CustomerID) FROM FactSales WHERE TenantID = %s',
            (tid,)
        )
        row = cursor.fetchone()
        cursor.execute(
            'SELECT TOP 12 YEAR(SaleDate), MONTH(SaleDate), ISNULL(SUM(Revenue),0) '
            'FROM FactSales WHERE TenantID = %s '
            'GROUP BY YEAR(SaleDate), MONTH(SaleDate) '
            'ORDER BY YEAR(SaleDate) DESC, MONTH(SaleDate) DESC',
            (tid,)
        )
        monthly = cursor.fetchall()
        cursor.execute(
            'SELECT TOP 5 p.ProductName, SUM(f.Quantity), SUM(f.Revenue) '
            'FROM FactSales f INNER JOIN DimProduct p ON p.ProductID = f.ProductID '
            'WHERE f.TenantID = %s GROUP BY p.ProductName ORDER BY SUM(f.Quantity) DESC',
            (tid,)
        )
        top_products = cursor.fetchall()
        cursor.execute(
            'SELECT COUNT(*) FROM FactInventory i '
            'WHERE i.TenantID = %s AND i.QuantityOnHand <= i.ReorderLevel',
            (tid,)
        )
        low_stock_row = cursor.fetchone()
    elif is_admin_level and payload.get('tenant_id'):
        # Admin có tenant_id: xem data tenant của mình
        tid = payload['tenant_id']
        cursor.execute(
            'SELECT ISNULL(SUM(Revenue),0), ISNULL(SUM(Profit),0), '
            'COUNT(*), COUNT(DISTINCT CustomerID) FROM FactSales WHERE TenantID = %s',
            (tid,)
        )
        row = cursor.fetchone()
        cursor.execute(
            'SELECT TOP 12 YEAR(SaleDate), MONTH(SaleDate), ISNULL(SUM(Revenue),0) '
            'FROM FactSales WHERE TenantID = %s '
            'GROUP BY YEAR(SaleDate), MONTH(SaleDate) '
            'ORDER BY YEAR(SaleDate) DESC, MONTH(SaleDate) DESC',
            (tid,)
        )
        monthly = cursor.fetchall()
        cursor.execute(
            'SELECT TOP 5 p.ProductName, SUM(f.Quantity), SUM(f.Revenue) '
            'FROM FactSales f INNER JOIN DimProduct p ON p.ProductID = f.ProductID '
            'WHERE f.TenantID = %s GROUP BY p.ProductName ORDER BY SUM(f.Quantity) DESC',
            (tid,)
        )
        top_products = cursor.fetchall()
        cursor.execute(
            'SELECT COUNT(*) FROM FactInventory i '
            'WHERE i.TenantID = %s AND i.QuantityOnHand <= i.ReorderLevel',
            (tid,)
        )
        low_stock_row = cursor.fetchone()
    else:
        cursor.execute(
            'SELECT ISNULL(SUM(Revenue),0), ISNULL(SUM(Profit),0), '
            'COUNT(*), COUNT(DISTINCT CustomerID) FROM FactSales'
        )
        row = cursor.fetchone()
        cursor.execute(
            'SELECT TOP 12 YEAR(SaleDate), MONTH(SaleDate), ISNULL(SUM(Revenue),0) '
            'FROM FactSales GROUP BY YEAR(SaleDate), MONTH(SaleDate) '
            'ORDER BY YEAR(SaleDate) DESC, MONTH(SaleDate) DESC'
        )
        monthly = cursor.fetchall()
        cursor.execute(
            'SELECT TOP 5 p.ProductName, SUM(f.Quantity), SUM(f.Revenue) '
            'FROM FactSales f INNER JOIN DimProduct p ON p.ProductID = f.ProductID '
            'GROUP BY p.ProductName ORDER BY SUM(f.Quantity) DESC'
        )
        top_products = cursor.fetchall()
        cursor.execute(
            'SELECT COUNT(*) FROM FactInventory i '
            'WHERE i.QuantityOnHand <= i.ReorderLevel'
        )
        low_stock_row = cursor.fetchone()
    conn.close()

    if row is None:
        return {
            'kpi': {
                'total_revenue': 0, 'total_profit': 0,
                'total_orders': 0, 'total_customers': 0,
                'profit_margin_pct': 0, 'low_stock_alerts': 0,
            },
            'monthly_revenue': [],
            'top_products': [],
            'view_scope': payload.get('tenant_id') or 'all',
        }

    total_rev = float(row[0]) if row[0] else 0
    total_profit = float(row[1]) if row[1] else 0

    return {
        'kpi': {
            'total_revenue': total_rev,
            'total_profit': total_profit,
            'total_orders': int(row[2]) if row[2] else 0,
            'total_customers': int(row[3]) if row[3] else 0,
            'profit_margin_pct': round(total_profit / total_rev * 100, 2) if total_rev else 0,
            'low_stock_alerts': int(low_stock_row[0]) if low_stock_row and low_stock_row[0] else 0,
        },
        'monthly_revenue': [
            {'year': r[0], 'month': r[1], 'revenue': float(r[2])} for r in (monthly or [])
        ],
        'top_products': [
            {'product': r[0], 'qty': int(r[1]) if r[1] else 0, 'revenue': float(r[2]) if r[2] else 0}
            for r in (top_products or [])
        ],
        'view_scope': payload.get('tenant_id') or 'all',
    }
