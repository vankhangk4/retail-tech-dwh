#!/usr/bin/env python3
# ============================================================
# FILE: superset/scripts/provision.py
# Mô tả: Provision Superset tự động — datasource, datasets,
#   dashboards, RLS cho DWH Multi-Tenant
#
# Chạy tự động trong superset container (sau khi web server lên)
# ============================================================

import os
import sys
import time
import json
import logging
import argparse
from typing import Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ---- Config from env ----
SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
ADMIN_USER  = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD   = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')

MSSQL_URI = os.environ.get(
    'MSSQL_DATABASE_URL',
    'mssql+pymssql://sa:M1tjtnrx@mssql:1433/DWH_MultiTenant'
)

# ---- Shared session (tự động handle cookies + CSRF) ----
_session = None

def get_session() -> requests.Session:
    global _session
    return _session

def init_session(token: str) -> requests.Session:
    """Tạo session đã có auth token và CSRF cookie."""
    global _session
    _session = requests.Session()
    _session.headers.update({
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    })
    # CSRF was disabled in Superset 3.x via WTF_CSRF_ENABLED=false
    # No CSRF token needed when CSRF is disabled, so skip gracefully
    logger.info('[OK] Session ready (CSRF disabled — no token needed)')
    return _session


def _api(method: str, path: str, **kwargs) -> requests.Response:
    """Gọi Superset API v1 bằng session (tự động mang CSRF cookie)."""
    s = get_session()
    if s:
        return s.request(method, f'{SUPERSET_URL}{path}', **kwargs)
    # Fallback
    return requests.request(method, f'{SUPERSET_URL}{path}', **kwargs)


# ---- Tenants & Tables ----
TENANTS = ['STORE_HN', 'STORE_HCM']

TABLES = [
    ('FactSales',       'dbo', 'Bảng sự kiện bán hàng'),
    ('FactInventory',   'dbo', 'Bảng sự kiện tồn kho'),
    ('FactPurchase',    'dbo', 'Bảng sự kiện nhập hàng'),
    ('DimProduct',      'dbo', 'Chiều sản phẩm'),
    ('DimCustomer',     'dbo', 'Chiều khách hàng'),
    ('DimStore',        'dbo', 'Chiều cửa hàng'),
    ('DimEmployee',     'dbo', 'Chiều nhân viên'),
    ('DimDate',         'dbo', 'Chiều thời gian'),
    ('DM_SalesSummary', 'dbo', 'Datamart tổng hợp doanh thu'),
    ('DM_CustomerRFM',  'dbo', 'Datamart RFM'),
]

DASHBOARDS = [
    {'id': 1, 'slug': 'revenue',    'title': 'Dashboard Doanh thu',
     'charts': [
         {'name': 'Doanh thu theo tháng',  'viz': 'line',      'dataset': 'DM_SalesSummary', 'dims': ['MonthName'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM'}]},
         {'name': 'Doanh thu theo cửa hàng','viz': 'bar',      'dataset': 'DM_SalesSummary', 'dims': ['StoreName'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM'}]},
         {'name': 'TOP sản phẩm bán chạy',  'viz': 'big_number', 'dataset': 'FactSales',        'dims': [],             'metrics': [{'label': 'SUM(Quantity)',      'agg': 'SUM'}]},
         {'name': 'Doanh thu theo danh mục', 'viz': 'pie',      'dataset': 'DM_SalesSummary', 'dims': ['CategoryName'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM'}]},
     ]},
    {'id': 2, 'slug': 'products',   'title': 'Dashboard Sản phẩm',
     'charts': [
         {'name': 'TOP sản phẩm theo số lượng', 'viz': 'bar', 'dataset': 'FactSales', 'dims': ['ProductName'], 'metrics': [{'label': 'SUM(Quantity)', 'agg': 'SUM'}]},
         {'name': 'TOP sản phẩm theo doanh thu', 'viz': 'bar', 'dataset': 'FactSales', 'dims': ['ProductName'], 'metrics': [{'label': 'SUM(Revenue)', 'agg': 'SUM'}]},
     ]},
    {'id': 3, 'slug': 'inventory',  'title': 'Dashboard Tồn kho',
     'charts': [
         {'name': 'Tồn kho thấp — Cảnh báo', 'viz': 'table', 'dataset': 'FactInventory', 'dims': ['ProductName', 'StoreName'], 'metrics': [{'label': 'SUM(ClosingStock)', 'agg': 'SUM'}]},
     ]},
    {'id': 4, 'slug': 'customers', 'title': 'Dashboard Khách hàng',
     'charts': [
         {'name': 'Phân bố phân khúc khách hàng', 'viz': 'pie', 'dataset': 'DM_CustomerRFM', 'dims': ['Segment'], 'metrics': [{'label': 'COUNT(*)', 'agg': 'COUNT'}]},
     ]},
    {'id': 5, 'slug': 'employees', 'title': 'Dashboard Nhân viên',
     'charts': [
         {'name': 'Doanh số theo nhân viên', 'viz': 'bar', 'dataset': 'FactSales', 'dims': ['EmployeeName'], 'metrics': [{'label': 'SUM(Revenue)', 'agg': 'SUM'}]},
     ]},
]

RLS_TABLES = [
    'FactSales', 'FactInventory', 'FactPurchase',
    'DimCustomer', 'DimStore', 'DimEmployee',
    'DM_SalesSummary', 'DM_CustomerRFM',
]


# ============================================================
# Helpers
# ============================================================

def wait_for_superset(max_wait: int = 180) -> bool:
    """Đợi Superset FAB manager khởi tạo xong."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            r = requests.get(f'{SUPERSET_URL}/health', timeout=5)
            if r.status_code == 200:
                # Health OK — thử login thật sự
                login_test = requests.post(
                    f'{SUPERSET_URL}/api/v1/security/login',
                    json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
                    timeout=10
                )
                if login_test.status_code == 200:
                    logger.info('Superset FAB ready')
                    return True
                time.sleep(5)
        except requests.RequestException:
            pass
        time.sleep(3)
    logger.error(f'Superset not ready after {max_wait}s')
    return False


def login() -> str:
    """Login và khởi tạo session với CSRF."""
    for attempt in range(15):
        try:
            r = requests.post(
                f'{SUPERSET_URL}/api/v1/security/login',
                json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
                timeout=15
            )
            if r.status_code == 200:
                token = r.json()['access_token']
                logger.info('[OK] Admin login')
                init_session(token)
                return token
        except requests.RequestException as e:
            logger.warning(f'Login attempt {attempt+1}: {e}')
        time.sleep(3)
    raise RuntimeError('Cannot login to Superset')


# ============================================================
# Step 1: MSSQL Database Connection
# ============================================================

def get_database_id(name: str) -> Optional[int]:
    r = _api('GET', '/api/v1/database/')
    if r.status_code != 200:
        return None
    for db in r.json().get('result', []):
        if db.get('database_name') == name:
            return db['id']
    return None


def create_database_connection() -> int:
    conn_name = 'DWH_MultiTenant_MSSQL'
    existing = get_database_id(conn_name)
    if existing:
        logger.info(f'[SKIP] DB "{conn_name}" (id={existing})')
        return existing

    payload = {
        'database_name': conn_name,
        'sqlalchemy_uri': MSSQL_URI,
        'expose_in_sqllab': True,
        'impersonate_user': False,
        'allow_ctas': False,
        'allow_cvas': False,
        'allow_dml': False,
        'cache_timeout': 300,
        'extra': json.dumps({
            'metadata_params': {},
            'engine_params': {},
            'connect_args': {'TrustServerCertificate': 'yes', 'Encrypt': 'no'},
        }),
    }
    r = _api('POST', '/api/v1/database/', json=payload, timeout=30)
    if r.status_code in (200, 201):
        resp = r.json()
        db_id = resp.get('id') or resp.get('result', {}).get('id')
        logger.info(f'[OK] Created DB "{conn_name}" (id={db_id})')
        return db_id
    elif r.status_code == 422 and 'already exists' in r.text.lower():
        return get_database_id(conn_name) or 0
    else:
        logger.error(f'[FAIL] Create DB: {r.status_code} — {r.text[:200]}')
        raise RuntimeError(f'Cannot create database: {r.text[:200]}')


# ============================================================
# Step 2: Datasets
# ============================================================

def get_dataset_id(table_name: str, schema: str = 'dbo') -> Optional[int]:
    r = _api('GET', '/api/v1/dataset/',
        params={'q': json.dumps({'filters': [{'col': 'table_name', 'opr': 'eq', 'value': table_name}]})},
        timeout=10)
    if r.status_code == 200:
        for ds in r.json().get('result', []):
            if ds.get('table_name') == table_name and ds.get('schema') == schema:
                return ds['id']
    return None


def create_dataset(table_name: str, schema: str, description: str = '') -> int:
    existing = get_dataset_id(table_name, schema)
    if existing:
        logger.info(f'[SKIP] Dataset "{table_name}" (id={existing})')
        return existing

    payload = {
        'dataset': {
            'database_name': 'DWH_MultiTenant_MSSQL',
            'schema': schema,
            'table_name': table_name,
            'description': description,
            'sql': None,
            'is_physical': True,
            'filter_select_enabled': False,
            'cache_timeout': 300,
        }
    }
    r = _api('POST', '/api/v1/dataset/', json=payload, timeout=30)
    if r.status_code in (200, 201):
        ds_id = r.json().get('id') or r.json().get('result', {}).get('id')
        logger.info(f'[OK] Created dataset "{table_name}" (id={ds_id})')
        return ds_id
    elif r.status_code == 422:
        return get_dataset_id(table_name, schema) or 0
    else:
        logger.warning(f'[WARN] Dataset "{table_name}": {r.status_code} — {r.text[:150]}')
        return 0


# ============================================================
# Step 3: Dashboards + Charts
# ============================================================

def get_dashboard_id(slug: str) -> Optional[int]:
    r = _api('GET', '/api/v1/dashboard/')
    if r.status_code == 200:
        for dash in r.json().get('result', []):
            if dash.get('slug') == slug:
                return dash['id']
    return None


def create_chart(dataset_id: int, chart_name: str, viz_type: str,
                 dims: list, metrics: list) -> int:
    agg = metrics[0]['agg'] if metrics else 'SUM'
    label = metrics[0]['label'] if metrics else ''

    params = {
        'viz_type': viz_type,
        'datasource': f'{dataset_id}__table',
        'groupby': dims,
        'metrics': [{'expressionType': 'SIMPLE', 'column': {}, 'aggregate': agg,
                     'sqlExpression': label, 'label': label}] if metrics else None,
        'order_desc': True,
        'row_limit': 100,
        'show_legend': True,
        'color_scheme': 'supersetColors',
    }
    if viz_type in ('big_number', 'single_metric'):
        params.pop('groupby', None)
        if params.get('metrics'):
            params['metrics'] = [params['metrics'][0]]
    if viz_type == 'histogram':
        params['all_columns_x'] = 'RFM_Score'
        params['histogram'] = True
        params.pop('groupby', None)
        params.pop('metrics', None)

    r = _api('POST', '/api/v1/chart/',
        json={
            'slice_name': chart_name,
            'description': '',
            'datasource_id': dataset_id,
            'datasource_type': 'table',
            'viz_type': viz_type,
            'params': json.dumps(params),
            'cache_timeout': 300,
        },
        timeout=30)

    if r.status_code in (200, 201):
        chart_id = r.json()['id']
        logger.info(f'[OK]   Chart "{chart_name}" (id={chart_id})')
        return chart_id
    logger.warning(f'[WARN] Chart "{chart_name}": {r.status_code} — {r.text[:150]}')
    return 0


def build_position(charts: list) -> str:
    children = [f'CHART-{c["id"]}' for c in charts]
    meta = {}
    for c in charts:
        meta[f'CHART-{c["id"]}'] = {
            'type': 'CHART', 'id': f'CHART-{c["id"]}',
            'meta': {'chartId': c['id'], 'width': 6, 'height': 50, 'chartName': c['name']},
        }
    layout = {
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {'type': 'GRID', 'id': 'GRID_ID', 'children': children,
                     'parents': ['ROOT_ID'],
                     'gridSize': {'default': {'rows': 12, 'columns': 12}}},
        'DASHBOARD_VERSION_KEY': 'v2',
    }
    layout.update(meta)
    return json.dumps(layout)


def create_dashboard(title: str, slug: str, description: str,
                     charts: list, owner_id: int = 1) -> int:
    existing = get_dashboard_id(slug)
    if existing:
        logger.info(f'[SKIP] Dashboard "{title}" (id={existing})')
        return existing

    r = _api('POST', '/api/v1/dashboard/',
        json={
            'dashboard_title': title,
            'slug': slug,
            'description': description,
            'published': True,
            'position_data': build_position(charts),
            'owners': [owner_id],
        },
        timeout=30)

    if r.status_code in (200, 201):
        dash_id = r.json()['id']
        logger.info(f'[OK] Created dashboard "{title}" (id={dash_id})')
        return dash_id
    logger.warning(f'[WARN] Dashboard "{title}": {r.status_code} — {r.text[:150]}')
    return 0


# ============================================================
# Step 4: RBAC — TenantViewer Role + RLS Rules
# ============================================================

def get_role_id(name: str) -> Optional[int]:
    r = _api('GET', '/api/v1/security/roles/')
    if r.status_code != 200:
        return None
    for role in r.json().get('result', []):
        if role.get('name') == name:
            return role['id']
    return None


def create_role(name: str) -> int:
    existing = get_role_id(name)
    if existing:
        logger.info(f'[SKIP] Role "{name}" (id={existing})')
        return existing
    r = _api('POST', '/api/v1/security/roles/', json={'name': name}, timeout=15)
    if r.status_code in (200, 201):
        role_id = r.json()['id']
        logger.info(f'[OK] Created role "{name}" (id={role_id})')
        return role_id
    elif r.status_code == 422:
        return get_role_id(name) or 0
    logger.warning(f'[WARN] Role "{name}": {r.status_code}')
    return 0


VIEWER_PERMS = [
    ('can_read', 'dashboard'),
    ('can_read', 'chart'),
    ('can_read', 'dataset'),
    ('can_explore', 'Superset'),
    ('can_read', 'css_template'),
    ('menu_access', 'Dashboards'),
    ('menu_access', 'Charts'),
]


def create_tenant_viewer_role() -> int:
    role_id = create_role('TenantViewer')
    if not role_id:
        return 0

    # Lấy perm map
    r_perm = _api('GET', '/api/v1/permission/', timeout=15)
    perm_map = {}
    if r_perm.status_code == 200:
        for p in r_perm.json().get('result', []):
            key = (p.get('name', ''), p.get('object_ref', ''))
            perm_map[key] = p['id']

    # Lấy current perms
    r_role = _api('GET', f'/api/v1/security/roles/{role_id}', timeout=15)
    current = set()
    if r_role.status_code == 200:
        for p in r_role.json().get('permissions', []):
            current.add((p.get('name', ''), p.get('object_ref', '')))

    for action, resource in VIEWER_PERMS:
        key = (action, resource)
        if key in current:
            continue
        if key not in perm_map:
            logger.warning(f'[WARN] Perm not found: {action} {resource}')
            continue
        r = _api('POST', f'/api/v1/security/roles/{role_id}/permissions',
            json={'permission_ids': [perm_map[key]]}, timeout=15)
        if r.status_code in (200, 201):
            logger.info(f'[OK]   TenantViewer: {action} {resource}')
        else:
            logger.info(f'[SKIP] TenantViewer: {action} {resource} ({r.status_code})')
    return role_id


def create_rls_filters(role_id: int, tenant_id: str):
    """Tạo RLS filter cho mỗi bảng có TenantID."""
    clause = f"TenantID = '{tenant_id}'"
    for table in RLS_TABLES:
        r = _api('POST', '/api/v1/rowlevel_security/',
            json={
                'name': f'RLS_{tenant_id}_{table}',
                'description': f'Row filter: {clause}',
                'filter_type': 'Regular',
                'roles': [role_id],
                'clause': clause,
            },
            timeout=15)
        if r.status_code in (200, 201):
            logger.info(f'[OK]   RLS: {tenant_id}/{table}')
        else:
            logger.info(f'[SKIP] RLS: {tenant_id}/{table} ({r.status_code})')


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip-db', action='store_true')
    parser.add_argument('--skip-datasets', action='store_true')
    parser.add_argument('--skip-dashboards', action='store_true')
    parser.add_argument('--skip-rls', action='store_true')
    args = parser.parse_args()

    logger.info('=' * 60)
    logger.info('Superset Provisioning — DWH Multi-Tenant')
    logger.info('=' * 60)

    if not wait_for_superset():
        logger.warning('Skipping — Superset not ready')
        return 0

    token = login()

    # Step 1: DB connection
    if not args.skip_db:
        logger.info('[STEP 1] MSSQL DB connection...')
        db_id = create_database_connection()
    else:
        db_id = get_database_id('DWH_MultiTenant_MSSQL') or 0
        logger.info('[STEP 1] Skipped')

    # Step 2: Datasets
    ds_ids = {}
    if not args.skip_datasets:
        logger.info('[STEP 2] Datasets...')
        for table_name, schema, desc in TABLES:
            ds_ids[table_name] = create_dataset(table_name, schema, desc)
    else:
        logger.info('[STEP 2] Skipped')

    # Step 3: Dashboards
    if not args.skip_dashboards:
        logger.info('[STEP 3] Dashboards...')
        for dash_cfg in DASHBOARDS:
            charts = []
            for chart_cfg in dash_cfg['charts']:
                ds_id = ds_ids.get(chart_cfg['dataset'], 0)
                if not ds_id:
                    continue
                cid = create_chart(
                    ds_id, chart_cfg['name'], chart_cfg['viz'],
                    chart_cfg['dims'], chart_cfg['metrics'])
                if cid:
                    charts.append({'id': cid, 'name': chart_cfg['name']})
            create_dashboard(dash_cfg['title'], dash_cfg['slug'],
                             dash_cfg.get('description', ''), charts)
    else:
        logger.info('[STEP 3] Skipped')

    # Step 4: RBAC + RLS
    if not args.skip_rls:
        logger.info('[STEP 4] RBAC + RLS...')
        create_tenant_viewer_role()
        for tenant_id in TENANTS:
            role_id = create_role(f'RLS_{tenant_id}')
            if role_id:
                create_rls_filters(role_id, tenant_id)
    else:
        logger.info('[STEP 4] Skipped')

    logger.info('=' * 60)
    logger.info('Provisioning complete!')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
