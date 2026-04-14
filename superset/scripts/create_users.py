# ============================================================
# FILE: superset/scripts/create_users.py
# Mô tả: Script tạo Superset users hàng loạt cho mỗi tenant
# với RBAC + Row Level Security
# ============================================================
# Cách sử dụng:
#   python superset/scripts/create_users.py
#
# Yêu cầu:
#   pip install requests
#   export SUPERSET_URL=http://localhost:8088
#   export SUPERSET_ADMIN_USER=admin
#   export SUPERSET_ADMIN_PWD=your_admin_password
# ============================================================

import os
import sys
import requests

SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
ADMIN_USER   = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD    = os.environ.get('SUPERSET_ADMIN_PWD', 'admin')


def get_admin_token() -> str:
    """Lấy Superset admin token."""
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/login',
        json={
            'username': ADMIN_USER,
            'password': ADMIN_PWD,
            'provider': 'db'
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()['access_token']


def get_role(token: str, role_name: str) -> dict:
    """Lấy role info theo tên."""
    r = requests.get(
        f'{SUPERSET_URL}/api/v1/security/roles/',
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    r.raise_for_status()
    roles = r.json()['result']
    return next((x for x in roles if x['name'] == role_name), None)


def create_role(token: str, role_name: str) -> int:
    """Tạo mới role và trả về role ID."""
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/roles/',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': role_name},
        timeout=30
    )
    if r.status_code == 422:
        # Role đã tồn tại
        existing = get_role(token, role_name)
        return existing['id']
    r.raise_for_status()
    return r.json()['id']


def create_user(
    token: str,
    tenant_id: str,
    username: str,
    email: str,
    password: str
) -> None:
    """
    Tạo user cho tenant với các role:
      - TenantViewer: quyền đọc dashboard
      - RLS_{tenant_id}: filter theo tenant_id
    """
    # Lấy role IDs
    tenant_viewer = get_role(token, 'TenantViewer')
    rls_role      = get_role(token, f'RLS_{tenant_id}')

    if not tenant_viewer:
        print(f'[WARN] TenantViewer role not found — skipping {username}')
        return
    if not rls_role:
        print(f'[WARN] RLS_{tenant_id} role not found — skipping {username}')
        return

    roles = [tenant_viewer['id'], rls_role['id']]

    payload = {
        'username': username,
        'email': email,
        'password': password,
        'active': True,
        'roles': roles,
    }

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/users/',
        headers={'Authorization': f'Bearer {token}'},
        json=payload,
        timeout=30
    )

    if r.status_code == 422:
        print(f'[SKIP] User already exists: {username}')
        return

    if r.status_code not in (200, 201):
        print(f'[ERROR] Failed to create {username}: {r.status_code} — {r.text}')
        return

    print(f'[OK] Created user {username} for {tenant_id}')


def create_rls_rules(token: str) -> None:
    """Tạo Row Level Security rules cho mỗi tenant và bảng."""
    tables = [
        'FactSales', 'FactInventory', 'FactPurchase',
        'DimCustomer', 'DimStore', 'DimEmployee',
        'DM_SalesSummary', 'DM_CustomerRFM'
    ]
    tenants = ['STORE_HN', 'STORE_HCM']

    for tenant_id in tenants:
        rls_role = get_role(token, f'RLS_{tenant_id}')
        if not rls_role:
            print(f'[WARN] RLS role not found: RLS_{tenant_id}')
            continue

        role_id = rls_role['id']

        for table in tables:
            payload = {
                'name': f'RLS_{tenant_id}_{table}',
                'description': f'Row filter: tenant_id = {tenant_id}',
                'filter_type': 'Regular',
                'roles': [role_id],
                'clause': f"tenant_id = '{tenant_id}'",
            }
            r = requests.post(
                f'{SUPERSET_URL}/api/v1/rowlevel_security/',
                headers={'Authorization': f'Bearer {token}'},
                json=payload,
                timeout=30
            )
            if r.status_code in (200, 201):
                print(f'[OK] RLS rule: {tenant_id}/{table}')
            else:
                print(f'[SKIP] RLS rule {tenant_id}/{table}: {r.status_code}')


def main():
    print('=' * 60)
    print('Superset Multi-Tenant User Setup')
    print('=' * 60)

    # Login
    try:
        admin_token = get_admin_token()
        print('[OK] Admin login successful')
    except Exception as e:
        print(f'[ERROR] Admin login failed: {e}')
        sys.exit(1)

    # Tạo RLS roles
    for tenant_id in ['STORE_HN', 'STORE_HCM']:
        create_role(admin_token, f'RLS_{tenant_id}')
        print(f'[OK] Created RLS role: RLS_{tenant_id}')

    # Tạo RLS rules
    create_rls_rules(admin_token)

    # Tạo users
    users = [
        # (tenant_id, username, email, password)
        ('STORE_HN', 'manager_hn',   'hn@company.com',   'Pass@HN123'),
        ('STORE_HCM', 'manager_hcm',  'hcm@company.com', 'Pass@HCM123'),
        ('STORE_HN', 'analyst_hn',    'hn.analyst@company.com', 'Pass@HN456'),
        ('STORE_HCM', 'analyst_hcm',  'hcm.analyst@company.com', 'Pass@HCM456'),
    ]

    for tenant_id, username, email, pwd in users:
        create_user(admin_token, tenant_id, username, email, pwd)

    print('=' * 60)
    print('Setup complete!')
    print('Manual steps needed in Superset UI:')
    print('  1. Create TenantViewer role with read-only permissions')
    print('  2. Assign RLS roles + TenantViewer to each tenant user')
    print('=' * 60)


if __name__ == '__main__':
    main()
