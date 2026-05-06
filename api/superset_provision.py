"""
Superset multi-tenant provisioning.

Mỗi tenant trong DWH ↔ một role `RLS_<tenant_id>` trong Superset có RLS clause
`TenantID = '<tenant_id>'` áp dụng cho tất cả dataset có cột TenantID.

Mỗi user (admin/viewer) tạo qua auth-gateway ↔ một user trong Superset
được gán role `TenantViewer` (fallback `Gamma`) + role `RLS_<tenant_id>`
của tenant tương ứng, nên luôn bị RLS lọc đúng tenant.
"""
import os
import re
import logging
from typing import Optional

import psycopg2
from werkzeug.security import generate_password_hash

logger = logging.getLogger(__name__)
TENANT_ID_RE = re.compile(r'^[A-Za-z0-9_]{1,20}$')

# Datasets cần áp RLS (có cột TenantID). Nếu thêm dataset mới có TenantID thì
# bổ sung vào đây — danh sách phải khớp tên table_name trong Superset.
RLS_DATASETS = [
    'FactSales', 'FactInventory', 'FactPurchase',
    'DimCustomer', 'DimStore', 'DimEmployee',
    'DM_SalesSummary', 'DM_ProductPerformance', 'DM_CustomerRFM',
    'DM_InventoryAlert', 'DM_EmployeePerformance',
    'V_SalesEnriched',
]


def _get_pg_conn():
    """Kết nối tới PostgreSQL của Superset (chứa metadata: roles, users, RLS)."""
    return psycopg2.connect(
        host=os.environ.get('SUPERSET_DB_HOST', 'superset-db'),
        port=int(os.environ.get('SUPERSET_DB_PORT', 5432)),
        user=os.environ.get('SUPERSET_DB_USER', 'superset'),
        password=os.environ.get('SUPERSET_DB_PASSWORD', 'superset123'),
        dbname=os.environ.get('SUPERSET_DB_NAME', 'superset'),
    )


def _get_or_create_role(cur, role_name: str) -> int:
    cur.execute('SELECT id FROM ab_role WHERE name = %s', (role_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute('INSERT INTO ab_role (name) VALUES (%s) RETURNING id', (role_name,))
    return cur.fetchone()[0]


def _get_role_id(cur, role_name: str) -> Optional[int]:
    cur.execute('SELECT id FROM ab_role WHERE name = %s', (role_name,))
    row = cur.fetchone()
    return row[0] if row else None


def _validate_tenant_id(tenant_id: str) -> bool:
    if not TENANT_ID_RE.match(tenant_id):
        logger.error(f'[SUPERSET] Invalid tenant_id for RLS: {tenant_id!r}')
        return False
    return True


def _ensure_assoc(cur, table_name: str, left_col: str, right_col: str,
                  left_id: int, right_id: int) -> None:
    cur.execute(
        f'SELECT 1 FROM {table_name} WHERE {left_col} = %s AND {right_col} = %s',
        (left_id, right_id)
    )
    if not cur.fetchone():
        cur.execute(
            f'INSERT INTO {table_name} ({left_col}, {right_col}) VALUES (%s, %s)',
            (left_id, right_id)
        )


def provision_tenant(tenant_id: str) -> bool:
    """Tạo role `RLS_<tenant_id>` + RLS rule trên tất cả dataset có cột TenantID.

    Idempotent — gọi lại sẽ skip những phần đã tồn tại.
    """
    if not _validate_tenant_id(tenant_id):
        return False

    role_name = f'RLS_{tenant_id}'
    clause = f"TenantID = '{tenant_id}'"

    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()

        role_id = _get_or_create_role(cur, role_name)

        # Lấy table_id của các dataset cần áp RLS
        cur.execute(
            'SELECT id, table_name FROM tables WHERE table_name = ANY(%s)',
            (RLS_DATASETS,)
        )
        tables = cur.fetchall()
        if not tables:
            logger.warning(f'[SUPERSET] No datasets found — bỏ qua RLS provision cho {tenant_id}')
            conn.rollback()
            return False

        for tbl_id, tbl_name in tables:
            rls_name = f'{role_name}_{tbl_name}'
            cur.execute(
                'SELECT id FROM row_level_security_filters WHERE name = %s',
                (rls_name,)
            )
            existing = cur.fetchone()
            if existing:
                rls_id = existing[0]
                cur.execute(
                    'UPDATE row_level_security_filters SET clause = %s WHERE id = %s',
                    (clause, rls_id)
                )
            else:
                cur.execute(
                    'INSERT INTO row_level_security_filters '
                    '(name, description, clause, filter_type) '
                    "VALUES (%s, %s, %s, 'Regular') RETURNING id",
                    (rls_name, f'Row filter: {clause}', clause)
                )
                rls_id = cur.fetchone()[0]

            # Liên kết RLS với role
            _ensure_assoc(cur, 'rls_filter_roles', 'rls_filter_id', 'role_id', rls_id, role_id)
            # Liên kết RLS với table
            _ensure_assoc(cur, 'rls_filter_tables', 'rls_filter_id', 'table_id', rls_id, tbl_id)

        conn.commit()
        logger.info(f'[SUPERSET] Provisioned tenant role {role_name} ({len(tables)} datasets)')
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f'[SUPERSET] provision_tenant({tenant_id}) failed: {e}')
        return False
    finally:
        if conn:
            conn.close()


def provision_user(username: str, password: str, tenant_id: Optional[str],
                   email: Optional[str] = None) -> bool:
    """Tạo user trong Superset, gán role TenantViewer/Gamma + RLS_<tenant_id>.

    - Superadmin (tenant_id=None): gán role `Admin`.
    - Idempotent — user đã tồn tại sẽ update password + roles.
    """
    email = email or f'{username}@dwh.local'
    pw_hash = generate_password_hash(password, method='pbkdf2:sha256')

    if tenant_id:
        if not provision_tenant(tenant_id):
            logger.error(f'[SUPERSET] Cannot provision user {username}: tenant RLS missing ({tenant_id})')
            return False

    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()

        cur.execute('SELECT id FROM ab_user WHERE username = %s', (username,))
        row = cur.fetchone()
        if row:
            user_id = row[0]
            cur.execute(
                'UPDATE ab_user SET password = %s, active = TRUE, email = %s WHERE id = %s',
                (pw_hash, email, user_id)
            )
        else:
            cur.execute(
                "INSERT INTO ab_user (first_name, last_name, username, password, email, "
                "active, login_count, fail_login_count, created_on, changed_on) "
                "VALUES (%s, '', %s, %s, %s, TRUE, 0, 0, NOW(), NOW()) RETURNING id",
                (username, username, pw_hash, email)
            )
            user_id = cur.fetchone()[0]

        # Xác định danh sách role theo tenant
        if tenant_id:
            viewer_role = 'TenantViewer' if _get_role_id(cur, 'TenantViewer') else 'Gamma'
            role_names = [viewer_role, f'RLS_{tenant_id}']
        else:
            role_names = ['Admin']

        # Xóa role cũ rồi gán lại — đảm bảo idempotent + đúng tenant
        cur.execute('DELETE FROM ab_user_role WHERE user_id = %s', (user_id,))
        for rname in role_names:
            rid = _get_role_id(cur, rname)
            if rid is None:
                raise RuntimeError(f'Role {rname} not found')
            cur.execute(
                'INSERT INTO ab_user_role (user_id, role_id) VALUES (%s, %s)',
                (user_id, rid)
            )

        conn.commit()
        logger.info(f'[SUPERSET] Provisioned user {username} (tenant={tenant_id}, roles={role_names})')
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f'[SUPERSET] provision_user({username}) failed: {e}')
        return False
    finally:
        if conn:
            conn.close()


def deactivate_user(username: str) -> bool:
    """Soft-delete user trong Superset."""
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()
        cur.execute('UPDATE ab_user SET active = FALSE WHERE username = %s', (username,))
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f'[SUPERSET] deactivate_user({username}) failed: {e}')
        return False
    finally:
        if conn:
            conn.close()


def deprovision_tenant(tenant_id: str) -> bool:
    """Xóa role + RLS rules của tenant. Idempotent."""
    if not _validate_tenant_id(tenant_id):
        return False

    role_name = f'RLS_{tenant_id}'
    conn = None
    try:
        conn = _get_pg_conn()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM row_level_security_filters WHERE name LIKE %s",
            (f'{role_name}_%',)
        )
        rls_ids = [r[0] for r in cur.fetchall()]

        for rid in rls_ids:
            cur.execute('DELETE FROM rls_filter_roles WHERE rls_filter_id = %s', (rid,))
            cur.execute('DELETE FROM rls_filter_tables WHERE rls_filter_id = %s', (rid,))
            cur.execute('DELETE FROM row_level_security_filters WHERE id = %s', (rid,))

        # Role: chỉ xóa nếu không còn user nào dùng
        rid = _get_role_id(cur, role_name)
        if rid:
            cur.execute('SELECT COUNT(*) FROM ab_user_role WHERE role_id = %s', (rid,))
            if cur.fetchone()[0] == 0:
                cur.execute('DELETE FROM ab_role WHERE id = %s', (rid,))

        conn.commit()
        logger.info(f'[SUPERSET] Deprovisioned tenant {tenant_id}')
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f'[SUPERSET] deprovision_tenant({tenant_id}) failed: {e}')
        return False
    finally:
        if conn:
            conn.close()
