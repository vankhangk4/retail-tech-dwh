# ============================================================
# FILE: api/management.py
# Mô tả: API CRUD cho Tenant, User, ETL Management (Admin only)
# ============================================================

import os
import pymssql as mssql
import jwt
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from passlib.context import CryptContext
from pydantic import BaseModel

# ---- Configuration ----
JWT_SECRET = os.environ.get('JWT_SECRET_KEY', 'changeme-minimum-32-chars!!')
ALGORITHM = 'HS256'

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
    """Dependency — chỉ admin mới được truy cập."""
    if not authorization.startswith('Bearer '):
        raise HTTPException(401, detail='Authorization header khong hop le')
    token = authorization[7:]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get('role') != 'admin':
            raise HTTPException(403, detail='Chi admin moi co quyen truy cap')
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail='Token da het han')
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail='Token khong hop le')


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


# ---- Pydantic Models ----

class TenantCreate(BaseModel):
    tenant_id: str
    tenant_name: str
    file_path: Optional[str] = None


class TenantUpdate(BaseModel):
    tenant_name: Optional[str] = None
    file_path: Optional[str] = None
    is_active: Optional[bool] = None


class UserCreate(BaseModel):
    username: str
    password: str
    tenant_id: Optional[str] = None
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
    cursor.execute('SELECT TenantID, TenantName, FilePath, IsActive, CreatedAt FROM Tenants ORDER BY CreatedAt DESC')
    rows = cursor.fetchall()
    conn.close()

    return {
        'tenants': [
            {
                'tenant_id': r['TenantID'],
                'tenant_name': r['TenantName'],
                'file_path': r['FilePath'],
                'is_active': bool(r['IsActive']),
                'created_at': r['CreatedAt'].isoformat() if r['CreatedAt'] else None,
            }
            for r in rows
        ]
    }


@router.post('/tenants')
def create_tenant(data: TenantCreate, payload=Depends(require_admin)):
    """Tạo tenant mới (Admin only)."""
    conn = get_mssql_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Tenants WHERE TenantID = %s', (data.tenant_id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(400, detail='TenantID da ton tai')

    cursor.execute(
        'INSERT INTO Tenants (TenantID, TenantName, FilePath, IsActive) VALUES (%s, %s, %s, 1)',
        (data.tenant_id, data.tenant_name, data.file_path)
    )
    conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Created tenant: {data.tenant_id} by user_id={payload["user_id"]}')
    return {'success': True, 'tenant_id': data.tenant_id}


@router.put('/tenants/{tenant_id}')
def update_tenant(tenant_id: str, data: TenantUpdate, payload=Depends(require_admin)):
    """Cập nhật tenant (Admin only)."""
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

    if updates:
        params.append(tenant_id)
        cursor.execute(f"UPDATE Tenants SET {', '.join(updates)} WHERE TenantID = %s", params)
        conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Updated tenant: {tenant_id}')
    return {'success': True}


@router.delete('/tenants/{tenant_id}')
def delete_tenant(tenant_id: str, payload=Depends(require_admin)):
    """Xóa tenant (Admin only) — soft delete."""
    if tenant_id in ('STORE_HN', 'STORE_HCM'):
        raise HTTPException(400, detail='Khong the xoa tenant mac dinh')

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
    return {'success': True}


# ============================================================
# USER MANAGEMENT
# ============================================================

@router.get('/users')
def list_users(payload=Depends(require_admin)):
    """Danh sách tất cả user (Admin only)."""
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)
    cursor.execute('SELECT UserID, Username, TenantID, Role, IsActive, CreatedAt FROM AppUsers ORDER BY CreatedAt DESC')
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


@router.post('/users')
def create_user(data: UserCreate, payload=Depends(require_admin)):
    """Tạo user mới (Admin only)."""
    if data.role not in ('admin', 'viewer'):
        raise HTTPException(400, detail='Role phai la admin hoac viewer')

    if data.tenant_id:
        conn_check = get_mssql_conn()
        cur = conn_check.cursor()
        cur.execute('SELECT 1 FROM Tenants WHERE TenantID = %s AND IsActive = 1', (data.tenant_id,))
        if not cur.fetchone():
            conn_check.close()
            raise HTTPException(400, detail='TenantID khong hop le hoac khong hoat dong')
        conn_check.close()

    tenant_for_user = None if data.role == 'admin' else data.tenant_id

    conn = get_mssql_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM AppUsers WHERE Username = %s', (data.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(400, detail='Username da ton tai')

    password_hash = hash_password(data.password)
    cursor.execute(
        'INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive) VALUES (%s, %s, %s, %s, 1)',
        (data.username, password_hash, tenant_for_user, data.role)
    )
    conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Created user: {data.username} role={data.role} tenant={tenant_for_user}')
    return {'success': True, 'username': data.username}


@router.put('/users/{user_id}')
def update_user(user_id: int, data: UserUpdate, payload=Depends(require_admin)):
    """Cập nhật user (Admin only)."""
    conn = get_mssql_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM AppUsers WHERE UserID = %s', (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(404, detail='User khong ton tai')

    updates = []
    params = []
    if data.password is not None:
        updates.append('PasswordHash = %s')
        params.append(hash_password(data.password))
    if data.role is not None:
        if data.role not in ('admin', 'viewer'):
            conn.close()
            raise HTTPException(400, detail='Role phai la admin hoac viewer')
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
    logger.info(f'[ADMIN] Updated user_id={user_id}')
    return {'success': True}


@router.delete('/users/{user_id}')
def delete_user(user_id: int, payload=Depends(require_admin)):
    """Xóa user (Admin only) — soft delete."""
    conn = get_mssql_conn()
    cursor = conn.cursor()
    cursor.execute('SELECT Username FROM AppUsers WHERE UserID = %s', (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, detail='User khong ton tai')

    if row[0] == 'admin':
        conn.close()
        raise HTTPException(400, detail='Khong the xoa tai khoan admin')

    cursor.execute('UPDATE AppUsers SET IsActive = 0 WHERE UserID = %s', (user_id,))
    conn.commit()
    conn.close()
    logger.info(f'[ADMIN] Deactivated user_id={user_id}')
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
    conn = get_mssql_conn()
    cursor = conn.cursor(as_dict=True)

    if tenant_id:
        cursor.execute(
            'SELECT LogID, TenantID, BatchDate, SourceTable, RunStatus, '
            'RowsExtracted, RowsInserted, RowsRejected, StartTime, EndTime, '
            'DurationSeconds, ErrorMessage FROM ETLLogs '
            'WHERE TenantID = %s ORDER BY StartTime DESC',
            (tenant_id,)
        )
    else:
        cursor.execute(
            'SELECT LogID, TenantID, BatchDate, SourceTable, RunStatus, '
            'RowsExtracted, RowsInserted, RowsRejected, StartTime, EndTime, '
            'DurationSeconds, ErrorMessage FROM ETLLogs ORDER BY StartTime DESC'
        )

    rows = cursor.fetchall()
    conn.close()

    return {
        'logs': [
            {
                'log_id': r['LogID'],
                'tenant_id': r['TenantID'],
                'batch_date': r['BatchDate'].isoformat() if r['BatchDate'] else None,
                'source_table': r['SourceTable'],
                'status': r['RunStatus'],
                'rows_extracted': r['RowsExtracted'],
                'rows_inserted': r['RowsInserted'],
                'rows_rejected': r['RowsRejected'],
                'start_time': r['StartTime'].isoformat() if r['StartTime'] else None,
                'end_time': r['EndTime'].isoformat() if r['EndTime'] else None,
                'duration_seconds': r['DurationSeconds'],
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
    cursor.execute(
        'SELECT WatermarkID, TenantID, TableName, LastRunTime, LastRunStatus, UpdatedAt '
        'FROM ETL_Watermark ORDER BY TenantID, TableName'
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

    # Tổng doanh thu
    if payload.get('role') == 'viewer' and payload.get('tenant_id'):
        tenant_filter = 'WHERE TenantID = %s'
        params = [payload['tenant_id']]
        cursor.execute(
            'SELECT ISNULL(SUM(NetSalesAmount),0), ISNULL(SUM(GrossProfitAmount),0), '
            'COUNT(DISTINCT InvoiceNumber), COUNT(DISTINCT CustomerKey) '
            'FROM FactSales ' + tenant_filter, params
        )
        cursor.execute(
            'SELECT TOP 12 d.Year, d.MonthNumber, ISNULL(SUM(f.NetSalesAmount),0) '
            'FROM FactSales f INNER JOIN DimDate d ON d.DateKey = f.DateKey '
            'WHERE f.TenantID = %s GROUP BY d.Year, d.MonthNumber ORDER BY d.Year DESC, d.MonthNumber DESC',
            params
        )
        cursor.execute(
            'SELECT TOP 5 p.ProductName, SUM(f.Quantity), SUM(f.NetSalesAmount) '
            'FROM FactSales f INNER JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.IsCurrent = 1 '
            'WHERE f.TenantID = %s GROUP BY p.ProductName ORDER BY SUM(f.Quantity) DESC',
            params
        )
        cursor.execute(
            'SELECT COUNT(*) FROM FactInventory i INNER JOIN DimProduct p ON p.ProductKey = i.ProductKey '
            'WHERE i.TenantID = %s AND i.ClosingStock <= ISNULL(i.ReorderPoint, 0)', params
        )
    else:
        cursor.execute(
            'SELECT ISNULL(SUM(NetSalesAmount),0), ISNULL(SUM(GrossProfitAmount),0), '
            'COUNT(DISTINCT InvoiceNumber), COUNT(DISTINCT CustomerKey) FROM FactSales'
        )
        cursor.execute(
            'SELECT TOP 12 d.Year, d.MonthNumber, ISNULL(SUM(f.NetSalesAmount),0) '
            'FROM FactSales f INNER JOIN DimDate d ON d.DateKey = f.DateKey '
            'GROUP BY d.Year, d.MonthNumber ORDER BY d.Year DESC, d.MonthNumber DESC'
        )
        cursor.execute(
            'SELECT TOP 5 p.ProductName, SUM(f.Quantity), SUM(f.NetSalesAmount) '
            'FROM FactSales f INNER JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.IsCurrent = 1 '
            'GROUP BY p.ProductName ORDER BY SUM(f.Quantity) DESC'
        )
        cursor.execute(
            'SELECT COUNT(*) FROM FactInventory i INNER JOIN DimProduct p ON p.ProductKey = i.ProductKey '
            'WHERE i.ClosingStock <= ISNULL(i.ReorderPoint, 0)'
        )

    row = cursor.fetchone()
    monthly = cursor.fetchall()
    top_products = cursor.fetchall()
    low_stock = cursor.fetchone()[0]
    conn.close()

    total_rev = float(row[0]) if row[0] else 0
    total_profit = float(row[1]) if row[1] else 0

    return {
        'kpi': {
            'total_revenue': total_rev,
            'total_profit': total_profit,
            'total_orders': int(row[2]) if row[2] else 0,
            'total_customers': int(row[3]) if row[3] else 0,
            'profit_margin_pct': round(total_profit / total_rev * 100, 2) if total_rev else 0,
            'low_stock_alerts': int(low_stock),
        },
        'monthly_revenue': [
            {'year': r[0], 'month': r[1], 'revenue': float(r[2])} for r in monthly
        ],
        'top_products': [
            {'product': r[0], 'qty': int(r[1]), 'revenue': float(r[2])} for r in top_products
        ],
        'view_scope': payload.get('tenant_id') or 'all',
    }