#!/usr/bin/env python3
# ============================================================
# FILE: superset/scripts/provision_v2.py
# Mô tả: Provision Superset trực tiếp bằng Superset SDK (programmatic)
#   thay vì REST API vì Superset 3.x không expose /security/roles/ endpoint
#
# Chạy tự động trong superset container sau khi web server lên
# ============================================================

import os
import sys
import time
import json
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ---- Config from env ----
ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD  = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')

MSSQL_URI = os.environ.get(
    'MSSQL_DATABASE_URL',
    'mssql+pymssql://sa:M1tjtnrx@mssql:1433/DWH_MultiTenant'
)

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
    {'id': 1, 'slug': 'revenue',   'title': 'Dashboard Doanh thu',
     'charts': [
         {'name': 'Doanh thu theo tháng',   'viz': 'line',       'dataset': 'DM_SalesSummary', 'dims': ['MonthName'],         'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM'}]},
         {'name': 'Doanh thu theo cửa hàng','viz': 'bar',       'dataset': 'DM_SalesSummary', 'dims': ['StoreName'],         'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM'}]},
         {'name': 'TOP sản phẩm bán chạy',  'viz': 'big_number', 'dataset': 'FactSales',       'dims': [],                   'metrics': [{'label': 'SUM(Quantity)',      'agg': 'SUM'}]},
         {'name': 'Doanh thu theo danh mục','viz': 'pie',       'dataset': 'DM_SalesSummary', 'dims': ['CategoryName'],     'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM'}]},
     ]},
    {'id': 2, 'slug': 'products',  'title': 'Dashboard Sản phẩm',
     'charts': [
         {'name': 'TOP sản phẩm theo số lượng','viz': 'bar', 'dataset': 'FactSales',   'dims': ['ProductName'], 'metrics': [{'label': 'SUM(Quantity)', 'agg': 'SUM'}]},
         {'name': 'TOP sản phẩm theo doanh thu','viz': 'bar', 'dataset': 'FactSales', 'dims': ['ProductName'], 'metrics': [{'label': 'SUM(Revenue)',  'agg': 'SUM'}]},
     ]},
    {'id': 3, 'slug': 'inventory','title': 'Dashboard Tồn kho',
     'charts': [
         {'name': 'Tồn kho thấp — Cảnh báo', 'viz': 'table', 'dataset': 'FactInventory', 'dims': ['ProductName', 'StoreName'], 'metrics': [{'label': 'SUM(ClosingStock)', 'agg': 'SUM'}]},
     ]},
    {'id': 4, 'slug': 'customers','title': 'Dashboard Khách hàng',
     'charts': [
         {'name': 'Phân bố phân khúc khách hàng', 'viz': 'pie', 'dataset': 'DM_CustomerRFM', 'dims': ['Segment'], 'metrics': [{'label': 'COUNT(*)', 'agg': 'COUNT'}]},
     ]},
    {'id': 5, 'slug': 'employees','title': 'Dashboard Nhân viên',
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
# Superset programmatic access
# ============================================================

def get_superset_app():
    """Khởi tạo Superset Flask app (must run from /app directory)."""
    from superset.app import create_app
    return create_app()


# ============================================================
# Step 1: MSSQL Database Connection
# ============================================================

def get_database_by_name(db_name: str) -> object:
    """Tìm database theo tên."""
    from superset.extensions import db
    from superset.models.core import Database
    return db.session.query(Database).filter_by(database_name=db_name).first()


def create_database_connection() -> object:
    """Tạo/kết nối MSSQL database trong Superset."""
    from superset.extensions import db
    from superset.models.core import Database

    conn_name = 'DWH_MultiTenant_MSSQL'
    existing = get_database_by_name(conn_name)
    if existing:
        logger.info(f'[SKIP] DB "{conn_name}" (id={existing.id})')
        return existing

    db_model = Database(
        database_name=conn_name,
        sqlalchemy_uri=MSSQL_URI,
        expose_in_sqllab=True,
        allow_ctas=False,
        allow_cvas=False,
        allow_dml=False,
        cache_timeout=300,
        extra=json.dumps({
            'metadata_params': {},
            'engine_params': {},
            'connect_args': {'TrustServerCertificate': 'yes', 'Encrypt': 'no'},
        }),
    )
    db.session.add(db_model)
    db.session.commit()
    db.session.refresh(db_model)
    logger.info(f'[OK] Created DB "{conn_name}" (id={db_model.id})')
    return db_model


# ============================================================
# Step 2: Datasets
# ============================================================

def get_dataset_by_name(table_name: str, schema: str, db_id: int) -> object:
    """Tìm dataset theo table name và schema."""
    from superset.extensions import db
    from superset.connectors.sqla.models import SqlaTable
    return db.session.query(SqlaTable).filter_by(
        table_name=table_name, schema=schema, database_id=db_id
    ).first()


def create_dataset(db_model: object, table_name: str, schema: str,
                   description: str) -> object:
    """Tạo dataset trong Superset."""
    from superset.extensions import db
    from superset.connectors.sqla.models import SqlaTable

    existing = get_dataset_by_name(table_name, schema, db_model.id)
    if existing:
        logger.info(f'[SKIP] Dataset "{table_name}" (id={existing.id})')
        return existing

    ds = SqlaTable(
        table_name=table_name,
        schema=schema,
        database_id=db_model.id,
        description=description,
        cache_timeout=300,
    )
    db.session.add(ds)
    db.session.commit()
    db.session.refresh(ds)
    logger.info(f'[OK] Created dataset "{table_name}" (id={ds.id})')
    return ds


# ============================================================
# Step 3: Dashboards + Charts
# ============================================================

def get_dashboard_by_slug(slug: str) -> object:
    from superset.extensions import db
    from superset.models.dashboard import Dashboard
    return db.session.query(Dashboard).filter_by(slug=slug).first()


def get_admin_user() -> object:
    from superset.extensions import db
    from flask_appbuilder.security.sqla.models import User
    return db.session.query(User).filter_by(username=ADMIN_USER).first()


def create_chart(ds_id: int, chart_name: str, viz_type: str,
                 dims: list, metrics: list, owner_id: int = 1) -> int:
    """Tạo chart trực tiếp vào database (bypass REST API permission issues)."""
    from superset.extensions import db
    from superset.models import sql_lab
    try:
        # Import using different approaches for compatibility
        try:
            from superset.models.slice import Slice
        except ImportError:
            try:
                from superset.models.core import Slice
            except ImportError:
                # Try importing through sql_lab models
                from sqlalchemy import create_engine, MetaData, Table
                from sqlalchemy.orm import sessionmaker
                # Fallback to API if we can't find Slice model
                raise ImportError("Cannot find Slice model - will use REST API fallback")

        agg = metrics[0]['agg'] if metrics else 'SUM'
        label = metrics[0]['label'] if metrics else ''

        params = {
            'viz_type': viz_type,
            'datasource': f'{ds_id}__table',
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

        chart = Slice(
            slice_name=chart_name,
            description='',
            datasource_id=ds_id,
            datasource_type='table',
            viz_type=viz_type,
            params=json.dumps(params),
            cache_timeout=300,
        )
        db.session.add(chart)
        db.session.commit()
        db.session.refresh(chart)
        logger.info(f'[OK]   Chart "{chart_name}" (id={chart.id})')
        return chart.id
    except ImportError as ie:
        logger.info(f'[INFO] Using REST API fallback (programmatic failed): {str(ie)[:50]}')
        # Fallback to REST API approach
        return _create_chart_via_api(ds_id, chart_name, viz_type, dims, metrics)
    except Exception as e:
        logger.warning(f'[WARN] Chart "{chart_name}": {str(e)[:150]}')
        db.session.rollback()
        return 0


def _create_chart_via_api(ds_id: int, chart_name: str, viz_type: str,
                          dims: list, metrics: list) -> int:
    """Fallback: Tạo chart qua REST API (only if programmatic fails)."""
    import requests

    resp = requests.post(
        'http://localhost:8088/api/v1/security/login',
        json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
        timeout=15
    )
    if resp.status_code != 200:
        logger.warning(f'Cannot login: {resp.status_code}')
        return 0

    token = resp.json()['access_token']
    agg = metrics[0]['agg'] if metrics else 'SUM'
    label = metrics[0]['label'] if metrics else ''

    params = {
        'viz_type': viz_type,
        'datasource': f'{ds_id}__table',
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

    r = requests.post(
        'http://localhost:8088/api/v1/chart/',
        json={
            'slice_name': chart_name,
            'description': '',
            'datasource_id': ds_id,
            'datasource_type': 'table',
            'viz_type': viz_type,
            'params': json.dumps(params),
            'cache_timeout': 300,
        },
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
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
    """Tạo dashboard trực tiếp vào database (bypass REST API permission issues)."""
    from superset.extensions import db

    existing = get_dashboard_by_slug(slug)
    if existing:
        logger.info(f'[SKIP] Dashboard "{title}" (id={existing.id})')
        return existing.id

    try:
        # Import Dashboard model
        try:
            from superset.models.dashboard import Dashboard
        except ImportError:
            from superset.models.core import Dashboard

        # Build position/layout for charts
        position = build_position(charts)

        dash = Dashboard(
            dashboard_title=title,
            slug=slug,
            description=description,
            position_json=position,
            published=True,
        )
        db.session.add(dash)
        db.session.commit()
        db.session.refresh(dash)

        logger.info(f'[OK] Created dashboard "{title}" (id={dash.id})')
        return dash.id
    except ImportError as ie:
        logger.info(f'[INFO] Using REST API fallback (programmatic failed): {str(ie)[:50]}')
        return _create_dashboard_via_api(title, slug, description, charts, owner_id)
    except Exception as e:
        logger.warning(f'[WARN] Dashboard "{title}": {str(e)[:150]}')
        db.session.rollback()
        return 0


def _create_dashboard_via_api(title: str, slug: str, description: str,
                              charts: list, owner_id: int = 1) -> int:
    """Fallback: Tạo dashboard qua REST API (only if programmatic fails)."""
    import requests

    resp = requests.post(
        'http://localhost:8088/api/v1/security/login',
        json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
        timeout=15
    )
    if resp.status_code != 200:
        logger.warning(f'Cannot login for dashboard: {resp.status_code}')
        return 0

    token = resp.json()['access_token']

    payload = {
        'dashboard_title': title,
        'slug': slug,
        'published': True,
        'owners': [owner_id],
    }

    r = requests.post(
        'http://localhost:8088/api/v1/dashboard/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )
    if r.status_code in (200, 201):
        dash_id = r.json()['id']
        logger.info(f'[OK] Created dashboard "{title}" (id={dash_id})')
        return dash_id
    logger.warning(f'[WARN] Dashboard "{title}": {r.status_code} — {r.text[:150]}')
    return 0


# ============================================================
# Step 4: RBAC — TenantViewer + RLS Roles (Programmatic)
# ============================================================

def create_role(name: str) -> object:
    """Tạo role trong Superset."""
    from superset.extensions import db
    from superset.extensions import security_manager as sm

    existing = sm.find_role(name)
    if existing:
        logger.info(f'[SKIP] Role "{name}" (id={existing.id})')
        return existing

    sm.add_role(name)
    db.session.commit()
    role = sm.find_role(name)
    logger.info(f'[OK] Created role "{name}"')
    return role


VIEWER_PERMS = [
    ('can_read', 'dashboard'),
    ('can_read', 'chart'),
    ('can_read', 'dataset'),
    ('can_explore', 'Superset'),
    ('can_read', 'css_template'),
    ('menu_access', 'Dashboards'),
    ('menu_access', 'Charts'),
]

# Admin user permissions (can create, edit, delete charts + dashboards)
ADMIN_PERMS = [
    ('can_read', 'dashboard'),
    ('can_write', 'dashboard'),
    ('can_create_modal', 'dashboard'),
    ('can_delete', 'dashboard'),
    ('can_read', 'chart'),
    ('can_write', 'chart'),
    ('can_create_modal', 'chart'),
    ('can_delete', 'chart'),
    ('can_read', 'dataset'),
    ('can_write', 'dataset'),
    ('can_create_modal', 'dataset'),
    ('can_delete', 'dataset'),
    ('can_explore', 'Superset'),
    ('can_read', 'css_template'),
    ('can_write', 'css_template'),
    ('menu_access', 'Dashboards'),
    ('menu_access', 'Charts'),
    ('menu_access', 'Datasets'),
]


def assign_admin_permissions(admin_user: object) -> bool:
    """Gán Admin role cho admin user (nó có tất cả permissions)."""
    from superset.extensions import db
    from superset.extensions import security_manager as sm

    # Tìm hoặc tạo Admin role
    admin_role = sm.find_role('Admin')
    if not admin_role:
        admin_role = sm.add_role('Admin')
        logger.info('[OK]   Created Admin role')
    else:
        logger.info('[OK]   Admin role exists')

    # Gán Admin role cho admin user nếu chưa có
    if admin_role not in admin_user.roles:
        admin_user.roles.append(admin_role)
        db.session.commit()
        logger.info('[OK]   Admin role assigned to admin user')
    else:
        logger.info('[SKIP] Admin user already has Admin role')

    return True


def create_tenant_viewer_role() -> object:
    """Tạo TenantViewer role với viewer permissions."""
    from superset.extensions import db
    from superset.extensions import security_manager as sm

    role = create_role('TenantViewer')
    if not role:
        return None

    for action, resource in VIEWER_PERMS:
        pv = sm.find_permission_view_menu(action, resource)
        if pv and pv not in role.permissions:
            sm.add_permission_role(role, pv)
            logger.info(f'[OK]   TenantViewer: {action} {resource}')
        else:
            logger.info(f'[SKIP] TenantViewer: {action} {resource}')

    db.session.commit()
    return role


def get_table_by_name(table_name: str, schema: str = 'dbo') -> object:
    """Tìm table model trong Superset."""
    from superset.extensions import db
    from superset.connectors.sqla.models import SqlaTable
    return db.session.query(SqlaTable).filter_by(
        table_name=table_name, schema=schema
    ).first()


def create_rls_filters(rls_role: object, tenant_id: str):
    """Tạo RLS filter cho mỗi bảng có TenantID."""
    from superset.extensions import db
    from superset.connectors.sqla.models import RowLevelSecurityFilter as RLS, SqlaTable

    clause = f"TenantID = '{tenant_id}'"

    for table_name in RLS_TABLES:
        table = db.session.query(SqlaTable).filter_by(
            table_name=table_name, schema='dbo'
        ).first()
        if not table:
            logger.info(f'[SKIP] Table "{table_name}" not found — create dataset first')
            continue

        # Check existing RLS
        existing = db.session.query(RLS).filter_by(
            name=f'RLS_{tenant_id}_{table_name}'
        ).first()
        if existing:
            logger.info(f'[SKIP] RLS: {tenant_id}/{table_name}')
            continue

        rls = RLS(
            name=f'RLS_{tenant_id}_{table_name}',
            description=f'Row filter: {clause}',
            filter_type='Regular',
            roles=[rls_role],
            tables=[table],
            clause=clause,
        )
        db.session.add(rls)
        db.session.commit()
        logger.info(f'[OK]   RLS: {tenant_id}/{table_name}')


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
    logger.info('Superset Provisioning v2 — DWH Multi-Tenant (Programmatic)')
    logger.info('=' * 60)

    app = get_superset_app()
    with app.app_context():
        # Verify admin user
        admin = get_admin_user()
        if not admin:
            logger.error('Admin user not found!')
            return 1
        logger.info(f'[OK] Admin user: {admin.username} (id={admin.id})')

        # Ensure admin has all necessary permissions
        logger.info('[STEP 0] Assigning admin permissions...')
        assign_admin_permissions(admin)

        # Step 1: DB connection (programmatic)
        if not args.skip_db:
            logger.info('[STEP 1] MSSQL DB connection...')
            db_model = create_database_connection()
        else:
            db_model = get_database_by_name('DWH_MultiTenant_MSSQL')
            if not db_model:
                logger.error('DB not found. Run with --skip-db=false first.')
                return 1
            logger.info('[STEP 1] Skipped')

        # Step 2: Datasets
        ds_ids = {}
        if not args.skip_datasets:
            logger.info('[STEP 2] Datasets...')
            for table_name, schema, desc in TABLES:
                ds = create_dataset(db_model, table_name, schema, desc)
                ds_ids[table_name] = ds.id if ds else 0
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
                                 dash_cfg.get('description', ''), charts,
                                 owner_id=admin.id)
        else:
            logger.info('[STEP 3] Skipped')

        # Assign dashboards to admin user
        logger.info('[STEP 3B] Assigning dashboards to admin...')
        from superset.extensions import db
        from superset.models.dashboard import Dashboard
        dashboards = db.session.query(Dashboard).all()
        for dash in dashboards:
            if admin not in dash.owners:
                dash.owners.append(admin)
                logger.info(f'[OK]   Dashboard "{dash.dashboard_title}" assigned to admin')
        db.session.commit()

        # Step 4: RBAC + RLS
        if not args.skip_rls:
            logger.info('[STEP 4] RBAC + RLS...')
            viewer_role = create_tenant_viewer_role()
            for tenant_id in TENANTS:
                rls_role = create_role(f'RLS_{tenant_id}')
                if rls_role:
                    create_rls_filters(rls_role, tenant_id)
        else:
            logger.info('[STEP 4] Skipped')

    logger.info('=' * 60)
    logger.info('Provisioning complete!')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
