#!/usr/bin/env python3
# ============================================================
# FILE: superset/scripts/provision.py
# Mô tả: Provision Superset tự động — tạo datasource,
#   datasets, dashboards, RLS cho DWH Multi-Tenant
#
# Chạy tự động trong superset-init container
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

# MSSQL connection
MSSQL_URI = os.environ.get(
    'MSSQL_DATABASE_URL',
    'mssql+pymssql://sa:M1tjtnrx@mssql:1433/DWH_MultiTenant'
)

# ---- Tenants & Tables ----
TENANTS = ['STORE_HN', 'STORE_HCM']

TABLES = [
    # (table_name, schema, description)
    ('FactSales',       'dbo', 'Bảng sự kiện bán hàng — grain: 1 dòng mỗi sản phẩm mỗi hóa đơn'),
    ('FactInventory',   'dbo', 'Bảng sự kiện tồn kho theo ngày'),
    ('FactPurchase',    'dbo', 'Bảng sự kiện nhập hàng'),
    ('DimProduct',      'dbo', 'Chiều sản phẩm (SCD Type 2)'),
    ('DimCustomer',     'dbo', 'Chiều khách hàng (SCD Type 2, có TenantID)'),
    ('DimStore',        'dbo', 'Chiều cửa hàng (có TenantID)'),
    ('DimEmployee',     'dbo', 'Chiều nhân viên (có TenantID)'),
    ('DimDate',         'dbo', 'Chiều thời gian (2015–2030)'),
    ('DM_SalesSummary', 'dbo', 'Datamart tổng hợp doanh thu theo ngày/cửa hàng/danh mục'),
    ('DM_CustomerRFM',  'dbo', 'Datamart RFM phân tích khách hàng'),
]

# Dashboard configs
DASHBOARDS = [
    {
        'id': 1,
        'slug': 'revenue',
        'title': 'Dashboard Doanh thu',
        'description': 'Phân tích doanh thu theo ngày, tuần, tháng, cửa hàng và danh mục sản phẩm',
        'charts': [
            {
                'name': 'Doanh thu theo tháng',
                'viz': 'line',
                'dataset': 'DM_SalesSummary',
                'dims': ['MonthName'],
                'metrics': [
                    {'label': 'SUM(TotalRevenue)', 'label_vn': 'Tổng Doanh thu'},
                    {'label': 'SUM(TotalProfit)',  'label_vn': 'Lợi nhuận gộp'},
                ],
            },
            {
                'name': 'Doanh thu theo cửa hàng',
                'viz': 'bar',
                'dataset': 'DM_SalesSummary',
                'dims': ['StoreName'],
                'metrics': [{'label': 'SUM(TotalRevenue)', 'label_vn': 'Doanh thu'}],
            },
            {
                'name': 'TOP 10 sản phẩm bán chạy',
                'viz': 'big_number',
                'dataset': 'FactSales',
                'dims': [],
                'metrics': [{'label': 'SUM(Quantity)', 'label_vn': 'Tổng số lượng bán'}],
            },
            {
                'name': 'Doanh thu theo danh mục',
                'viz': 'pie',
                'dataset': 'DM_SalesSummary',
                'dims': ['CategoryName'],
                'metrics': [{'label': 'SUM(TotalRevenue)', 'label_vn': 'Doanh thu'}],
            },
        ],
    },
    {
        'id': 2,
        'slug': 'products',
        'title': 'Dashboard Sản phẩm',
        'description': 'TOP sản phẩm bán chạy, biên lợi nhuận gộp, tỷ lệ chiết khấu',
        'charts': [
            {
                'name': 'Biên lợi nhuận theo sản phẩm',
                'viz': 'line',
                'dataset': 'FactSales',
                'dims': ['ProductName'],
                'metrics': [{'label': 'SUM(GrossProfitAmount)/SUM(Quantity)', 'label_vn': 'LN/Đơn vị'}],
            },
            {
                'name': 'TOP sản phẩm theo số lượng',
                'viz': 'bar',
                'dataset': 'FactSales',
                'dims': ['ProductName'],
                'metrics': [{'label': 'SUM(Quantity)', 'label_vn': 'Số lượng'}],
            },
        ],
    },
    {
        'id': 3,
        'slug': 'inventory',
        'title': 'Dashboard Tồn kho',
        'description': 'Cảnh báo tồn kho dưới ngưỡng, xu hướng nhập/xuất kho',
        'charts': [
            {
                'name': 'Tồn kho thấp — Cảnh báo',
                'viz': 'table',
                'dataset': 'FactInventory',
                'dims': ['ProductName', 'StoreName'],
                'metrics': [{'label': 'ClosingStock', 'label_vn': 'Tồn kho'}],
            },
        ],
    },
    {
        'id': 4,
        'slug': 'customers',
        'title': 'Dashboard Khách hàng',
        'description': 'Phân tích phân khúc RFM — Champions, Loyal, At Risk, Lost',
        'charts': [
            {
                'name': 'Phân bố phân khúc khách hàng',
                'viz': 'pie',
                'dataset': 'DM_CustomerRFM',
                'dims': ['Segment'],
                'metrics': [{'label': 'COUNT(*)', 'label_vn': 'Số khách hàng'}],
            },
            {
                'name': 'RFM Score phân bố',
                'viz': 'histogram',
                'dataset': 'DM_CustomerRFM',
                'dims': [],
                'metrics': [{'label': 'RFM_Score', 'label_vn': 'RFM Score'}],
            },
        ],
    },
    {
        'id': 5,
        'slug': 'employees',
        'title': 'Dashboard Nhân viên',
        'description': 'Hiệu suất nhân viên — doanh số, số giao dịch, biên lợi nhuận',
        'charts': [
            {
                'name': 'Doanh số theo nhân viên',
                'viz': 'bar',
                'dataset': 'FactSales',
                'dims': ['FullName'],
                'metrics': [{'label': 'SUM(NetSalesAmount)', 'label_vn': 'Doanh số'}],
            },
        ],
    },
]


# ============================================================
# Helpers
# ============================================================

def wait_for_superset(max_wait: int = 120) -> bool:
    """Đợi Superset web service sẵn sàng."""
    start = time.time()
    while time.time() - start < max_wait:
        try:
            r = requests.get(f'{SUPERSET_URL}/health', timeout=5)
            if r.status_code == 200:
                logger.info('Superset is ready')
                return True
        except requests.RequestException:
            pass
        time.sleep(3)
    logger.error(f'Superset not ready after {max_wait}s')
    return False


def login() -> str:
    """Lấy admin access token."""
    for attempt in range(10):
        try:
            r = requests.post(
                f'{SUPERSET_URL}/api/v1/security/login',
                json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
                timeout=15
            )
            if r.status_code == 200:
                logger.info('[OK] Admin login successful')
                return r.json()['access_token']
        except requests.RequestException as e:
            logger.warning(f'Login attempt {attempt+1} failed: {e}')
        time.sleep(3)

    raise RuntimeError('Cannot login to Superset')


def hdrs(token: str) -> dict:
    return {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}


# ============================================================
# Step 1: Create MSSQL Database Connection
# ============================================================

def get_database_id(token: str, name: str) -> Optional[int]:
    """Tìm database connection ID theo tên."""
    r = requests.get(f'{SUPERSET_URL}/api/v1/database/', headers=hdrs(token))
    if r.status_code != 200:
        return None
    for db in r.json()['result']:
        if db['database_name'] == name:
            return db['id']
    return None


def create_database_connection(token: str) -> int:
    """Tạo MSSQL database connection trong Superset."""
    conn_name = 'DWH_MultiTenant_MSSQL'

    existing = get_database_id(token, conn_name)
    if existing:
        logger.info(f'[SKIP] Database connection "{conn_name}" already exists (id={existing})')
        return existing

    # Mask password in URI for logging
    uri_clean = MSSQL_URI.replace(os.environ.get('MSSQL_SA_PASSWORD', 'M1tjtnrx'), '***')

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/database/',
        headers=hdrs(token),
        json={
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
                'connect_args': {
                    'TrustServerCertificate': 'yes',
                    'Encrypt': 'no',
                }
            }),
        },
        timeout=30
    )

    if r.status_code == 200:
        db_id = r.json()['id']
        logger.info(f'[OK] Created database connection "{conn_name}" (id={db_id})')
        return db_id
    elif r.status_code == 422 and 'already exists' in r.text.lower():
        return get_database_id(token, conn_name)
    else:
        logger.error(f'[FAIL] Create database: {r.status_code} — {r.text}')
        raise RuntimeError(f'Cannot create database connection: {r.text}')


# ============================================================
# Step 2: Create Datasets
# ============================================================

def get_dataset_id(token: str, table_name: str, schema: str = 'dbo') -> Optional[int]:
    """Tìm dataset ID theo table name."""
    r = requests.get(
        f'{SUPERSET_URL}/api/v1/dataset/',
        headers=hdrs(token),
        params={'q': json.dumps({'filters': [{'col': 'table_name', 'opr': 'eq', 'value': table_name}]})},
        timeout=10
    )
    if r.status_code == 200:
        result = r.json().get('result', [])
        for ds in result:
            if ds.get('table_name') == table_name and ds.get('schema') == schema:
                return ds['id']
    return None


def create_dataset(token: str, db_id: int, table_name: str, schema: str, description: str = '') -> int:
    """Tạo dataset từ bảng MSSQL."""
    existing = get_dataset_id(token, table_name, schema)
    if existing:
        logger.info(f'[SKIP] Dataset "{table_name}" already exists (id={existing})')
        return existing

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/dataset/',
        headers=hdrs(token),
        json={
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
        },
        timeout=30
    )

    if r.status_code in (200, 201):
        ds_id = r.json().get('id') or r.json().get('result', {}).get('id')
        logger.info(f'[OK] Created dataset "{table_name}" (id={ds_id})')
        return ds_id
    elif r.status_code == 422:
        # Try alternate API format
        return get_dataset_id(token, table_name, schema) or 0
    else:
        logger.warning(f'[WARN] Dataset "{table_name}": {r.status_code} — {r.text[:200]}'  )
        return 0


# ============================================================
# Step 3: Create Dashboards + Charts
# ============================================================

def get_dashboard_id(token: str, slug: str) -> Optional[int]:
    """Tìm dashboard ID theo slug."""
    r = requests.get(f'{SUPERSET_URL}/api/v1/dashboard/', headers=hdrs(token))
    if r.status_code == 200:
        for dash in r.json()['result']:
            if dash.get('slug') == slug:
                return dash['id']
    return None


def create_chart(
    token: str,
    db_id: int,
    dataset_id: int,
    chart_name: str,
    viz_type: str,
    dims: list,
    metrics: list,
    table_name: str,
) -> int:
    """Tạo một chart trong Superset."""
    # Build metrics list for params
    metrics_list = [{'expressionType': 'SIMPLE', 'column': {}, 'aggregate': m['label'].split('(')[0] if '(' in m['label'] else 'SUM', 'sqlExpression': m['label'], 'label': m['label']} for m in metrics]

    # Build groupby
    groupby = dims

    # Build datasource string
    datasource = f'{dataset_id}__table'

    params = {
        'viz_type': viz_type,
        'datasource': datasource,
        'groupby': groupby,
        'metrics': metrics_list if metrics_list else None,
        'order_desc': True,
        'row_limit': 100,
        'show_legend': True,
        'color_scheme': 'supersetColors',
    }

    # Big number doesn't need groupby
    if viz_type in ('big_number', 'single_metric'):
        params.pop('groupby', None)
        if metrics_list:
            params['metrics'] = [metrics_list[0]]

    # Histogram needs different config
    if viz_type == 'histogram':
        params['all_columns_x'] = 'RFM_Score'
        params['histogram'] = True
        params.pop('groupby', None)
        params.pop('metrics', None)

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/chart/',
        headers=hdrs(token),
        json={
            'slice_name': chart_name,
            'description': '',
            'datasource_id': dataset_id,
            'datasource_type': 'table',
            'viz_type': viz_type,
            'params': json.dumps(params),
            'cache_timeout': 300,
        },
        timeout=30
    )

    if r.status_code in (200, 201):
        chart_id = r.json()['id']
        logger.info(f'[OK]   Created chart "{chart_name}" (id={chart_id})')
        return chart_id
    elif r.status_code == 422:
        logger.warning(f'[WARN] Chart "{chart_name}" validation error: {r.text[:200]}')
        return 0
    else:
        logger.warning(f'[WARN] Chart "{chart_name}": {r.status_code} — {r.text[:200]}')
        return 0


def build_position_data(chart_ids: list[int]) -> str:
    """Build Superset dashboard grid layout JSON string."""
    if not chart_ids:
        return json.dumps({'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']}, 'GRID_ID': {'type': 'GRID', 'id': 'GRID_ID', 'children': [], 'parents': ['ROOT_ID']}, 'DASHBOARD_VERSION_KEY': 'v2'})

    children = [f'CHART-{cid}' for cid in chart_ids]
    chart_meta = {}
    for i, cid in enumerate(chart_ids):
        chart_meta[f'CHART-{cid}'] = {
            'type': 'CHART',
            'id': f'CHART-{cid}',
            'meta': {
                'chartId': cid,
                'width': 6,
                'height': 50,
                'chartName': f'chart_{cid}',
            }
        }

    layout = {
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {
            'type': 'GRID', 'id': 'GRID_ID',
            'children': children,
            'parents': ['ROOT_ID'],
            'gridSize': {'default': {'rows': 12, 'columns': 12},
                         'xl': {'rows': 12, 'columns': 12}},
        },
        'DASHBOARD_VERSION_KEY': 'v2',
    }
    layout.update(chart_meta)

    return json.dumps(layout)


def create_dashboard(
    token: str,
    title: str,
    slug: str,
    description: str,
    chart_ids: list[int],
    owner_id: int = 1,
) -> int:
    """Tạo dashboard với các chart đã tạo."""
    existing = get_dashboard_id(token, slug)
    if existing:
        logger.info(f'[SKIP] Dashboard "{title}" already exists (id={existing})')
        return existing

    position_data = build_position_data(chart_ids)

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/dashboard/',
        headers=hdrs(token),
        json={
            'dashboard_title': title,
            'slug': slug,
            'description': description,
            'published': True,
            'position_data': position_data,
            'owners': [owner_id],
        },
        timeout=30
    )

    if r.status_code in (200, 201):
        dash_id = r.json()['id']
        logger.info(f'[OK] Created dashboard "{title}" (id={dash_id})')
        return dash_id
    else:
        logger.warning(f'[WARN] Dashboard "{title}": {r.status_code} — {r.text[:200]}')
        return 0


# ============================================================
# Step 4: Create RLS Roles + Rules
# ============================================================

def get_role_id(token: str, role_name: str) -> Optional[int]:
    """Tìm role ID theo tên."""
    r = requests.get(f'{SUPERSET_URL}/api/v1/security/roles/', headers=hdrs(token))
    if r.status_code != 200:
        return None
    for role in r.json()['result']:
        if role['name'] == role_name:
            return role['id']
    return None


def create_rls_role(token: str, role_name: str) -> int:
    """Tạo RLS role."""
    existing = get_role_id(token, role_name)
    if existing:
        logger.info(f'[SKIP] Role "{role_name}" already exists (id={existing})')
        return existing

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/roles/',
        headers=hdrs(token),
        json={'name': role_name},
        timeout=15
    )
    if r.status_code == 200:
        role_id = r.json()['id']
        logger.info(f'[OK] Created role "{role_name}" (id={role_id})')
        return role_id
    elif r.status_code == 422:
        return get_role_id(token, role_name) or 0
    else:
        logger.warning(f'[WARN] Role "{role_name}": {r.status_code}')
        return 0


def create_rls_filter(token: str, name: str, clause: str, role_id: int):
    """Tạo RLS filter rule."""
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/rowlevel_security/',
        headers=hdrs(token),
        json={
            'name': name,
            'description': f'Row filter: {clause}',
            'filter_type': 'Regular',
            'roles': [role_id],
            'clause': clause,
        },
        timeout=15
    )
    if r.status_code in (200, 201):
        logger.info(f'[OK]   RLS rule: {name}')
    else:
        logger.info(f'[SKIP] RLS rule "{name}": {r.status_code}')


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Provision Superset DWH Multi-Tenant')
    parser.add_argument('--skip-db', action='store_true', help='Skip database connection creation')
    parser.add_argument('--skip-datasets', action='store_true', help='Skip dataset creation')
    parser.add_argument('--skip-dashboards', action='store_true', help='Skip dashboard creation')
    parser.add_argument('--skip-rls', action='store_true', help='Skip RLS setup')
    args = parser.parse_args()

    logger.info('=' * 60)
    logger.info('Superset Provisioning — DWH Multi-Tenant')
    logger.info('=' * 60)

    if not wait_for_superset():
        logger.warning('Superset not ready — skipping provisioning')
        return 0

    token = login()
    logger.info(f'Superset URL: {SUPERSET_URL}')

    # ── Step 1: Database Connection ──────────────────────────────
    if not args.skip_db:
        logger.info('[STEP 1] Creating MSSQL database connection...')
        db_id = create_database_connection(token)
    else:
        logger.info('[STEP 1] Skipped')
        db_id = get_database_id(token, 'DWH_MultiTenant_MSSQL')

    # ── Step 2: Datasets ─────────────────────────────────────────
    dataset_ids = {}
    if not args.skip_datasets:
        logger.info('[STEP 2] Creating datasets...')
        for table_name, schema, desc in TABLES:
            ds_id = create_dataset(token, db_id, table_name, schema, desc)
            dataset_ids[table_name] = ds_id
    else:
        logger.info('[STEP 2] Skipped')

    # ── Step 3: Dashboards ────────────────────────────────────────
    dashboard_ids = {}
    if not args.skip_dashboards:
        logger.info('[STEP 3] Creating dashboards and charts...')
        for dash_cfg in DASHBOARDS:
            logger.info(f'  Dashboard: {dash_cfg["title"]}')
            chart_ids = []
            for chart_cfg in dash_cfg['charts']:
                table_name = chart_cfg['dataset']
                ds_id = dataset_ids.get(table_name, 0)
                if not ds_id:
                    logger.warning(f'    [SKIP] Dataset "{table_name}" not found')
                    continue

                chart_id = create_chart(
                    token, db_id, ds_id,
                    chart_name=chart_cfg['name'],
                    viz_type=chart_cfg['viz'],
                    dims=chart_cfg['dims'],
                    metrics=chart_cfg['metrics'],
                    table_name=table_name,
                )
                if chart_id:
                    chart_ids.append(chart_id)

            dash_id = create_dashboard(
                token,
                title=dash_cfg['title'],
                slug=dash_cfg['slug'],
                description=dash_cfg['description'],
                chart_ids=chart_ids,
            )
            dashboard_ids[dash_cfg['id']] = dash_id

        logger.info('[STEP 3] Dashboard summary:')
        for dash_id, dash_num in zip(dashboard_ids.values(), range(1, len(DASHBOARDS)+1)):
            logger.info(f'  Dashboard {dash_num}: id={dash_id}')
    else:
        logger.info('[STEP 3] Skipped')

    # ── Step 4: RLS ──────────────────────────────────────────────
    if not args.skip_rls:
        logger.info('[STEP 4] Creating RLS roles and filters...')
        # Tables that have TenantID column for RLS
        tenant_tables = [
            'FactSales', 'FactInventory', 'FactPurchase',
            'DimCustomer', 'DimStore', 'DimEmployee',
            'DM_SalesSummary', 'DM_CustomerRFM',
        ]

        for tenant_id in TENANTS:
            role_name = f'RLS_{tenant_id}'
            role_id = create_rls_role(token, role_name)
            if not role_id:
                continue
            logger.info(f'  Tenant: {tenant_id}')
            for table in tenant_tables:
                create_rls_filter(
                    token,
                    name=f'RLS_{tenant_id}_{table}',
                    clause=f"TenantID = '{tenant_id}'",
                    role_id=role_id,
                )
        logger.info('[STEP 4] RLS setup complete')
    else:
        logger.info('[STEP 4] Skipped')

    logger.info('=' * 60)
    logger.info('Provisioning complete!')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
