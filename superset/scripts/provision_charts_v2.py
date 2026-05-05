#!/usr/bin/env python3
"""
Recreate charts với đúng Superset 3.x API format.
Xóa charts cũ (188-217) và tạo charts mới với query format tương thích.
Chạy TRONG container: docker exec dwh_superset python3 /superset_scripts/provision_charts_v2.py
"""
import os
import sys
import time
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

SUPERSET_URL = 'http://localhost:8088'
ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD  = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')

# Dataset IDs (da sync columns roi)
DS = {
    'FactSales':       1,
    'FactInventory':   2,
    'FactPurchase':    3,
    'DimProduct':      4,
    'DimCustomer':     5,
    'DimStore':        6,
    'DimEmployee':     7,
    'DimDate':         8,
    'DM_SalesSummary': 9,
    'DM_CustomerRFM':  10,
}

# Dashboard configs: dash_slug -> dash_id mapping
DASH_SLUG_TO_ID = {
    'doanh-thu':   11,
    'san-pham':    12,
    'ton-kho':     13,
    'khach-hang':  14,
    'nhan-vien':   15,
}

# Charts cho 5 dashboards (30 charts)
DASHBOARDS = [
    {
        'slug': 'doanh-thu', 'title': 'Phan tich Doanh thu',
        'charts': [
            {'name': 'Doanh thu theo thang', 'viz': 'line', 'ds': 'DM_SalesSummary',
             'dims': ['Month'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 100},
            {'name': 'Doanh thu theo quy', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Quarter'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 10},
            {'name': 'So sanh cung ky nam truoc', 'viz': 'line', 'ds': 'DM_SalesSummary',
             'dims': ['Year', 'Month'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 100},
            {'name': 'Doanh thu theo danh muc', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 50},
            {'name': 'Ty le dong gop doanh thu theo danh muc', 'viz': 'pie', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 20},
            {'name': 'TOP 10 san pham ban chay', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['ProductID'], 'metrics': [{'agg': 'SUM', 'col': 'Quantity'}],
             'limit': 10},
            {'name': 'Doanh thu va loi nhuan theo thang', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Month'],
             'metrics': [
                 {'agg': 'SUM', 'col': 'TotalRevenue'},
                 {'agg': 'SUM', 'col': 'TotalProfit'},
             ],
             'limit': 50},
        ],
    },
    {
        'slug': 'san-pham', 'title': 'Phan tich San pham',
        'charts': [
            {'name': 'TOP san pham theo so luong ban', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['ProductID'], 'metrics': [{'agg': 'SUM', 'col': 'Quantity'}],
             'limit': 10},
            {'name': 'TOP san pham theo doanh thu', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['ProductID'], 'metrics': [{'agg': 'SUM', 'col': 'Revenue'}],
             'limit': 10},
            {'name': 'Phan bo doanh thu theo danh muc', 'viz': 'pie', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 20},
            {'name': 'Bien loi nhuan gop theo danh muc', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'agg': 'SUM', 'col': 'TotalProfit'}],
             'limit': 20},
            {'name': 'Doanh thu theo danh muc va thang', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Category', 'Month'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 100},
            {'name': 'Xu huong san pham theo thang', 'viz': 'line', 'ds': 'DM_SalesSummary',
             'dims': ['Month'], 'metrics': [{'agg': 'SUM', 'col': 'TotalRevenue'}],
             'limit': 50},
            {'name': 'Tong so san pham da ban', 'viz': 'big_number', 'ds': 'FactSales',
             'dims': [], 'metrics': [{'agg': 'SUM', 'col': 'Quantity'}],
             'limit': 10},
        ],
    },
    {
        'slug': 'ton-kho', 'title': 'Quan ly Ton kho',
        'charts': [
            {'name': 'Canh bao ton kho duoi nguong', 'viz': 'table', 'ds': 'FactInventory',
             'dims': ['ProductID', 'StoreKey'],
             'metrics': [{'agg': 'SUM', 'col': 'QuantityOnHand'}],
             'limit': 50},
            {'name': 'Ton kho theo cua hang', 'viz': 'bar', 'ds': 'FactInventory',
             'dims': ['StoreKey'], 'metrics': [{'agg': 'SUM', 'col': 'QuantityOnHand'}],
             'limit': 20},
            {'name': 'Xu huong ton kho theo ngay', 'viz': 'line', 'ds': 'FactInventory',
             'dims': ['CheckDate'], 'metrics': [{'agg': 'SUM', 'col': 'QuantityOnHand'}],
             'limit': 100},
            {'name': 'Phan bo ton kho theo san pham', 'viz': 'pie', 'ds': 'FactInventory',
             'dims': ['ProductID'], 'metrics': [{'agg': 'SUM', 'col': 'QuantityOnHand'}],
             'limit': 20},
            {'name': 'TOP san pham ton kho cao nhat', 'viz': 'bar', 'ds': 'FactInventory',
             'dims': ['ProductID'], 'metrics': [{'agg': 'SUM', 'col': 'QuantityOnHand'}],
             'limit': 10},
            {'name': 'Tong so luong ton kho', 'viz': 'big_number', 'ds': 'FactInventory',
             'dims': [], 'metrics': [{'agg': 'SUM', 'col': 'QuantityOnHand'}],
             'limit': 10},
        ],
    },
    {
        'slug': 'khach-hang', 'title': 'Phan tich Khach hang',
        'charts': [
            {'name': 'Phan bo phan khuc khach hang RFM', 'viz': 'pie', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'agg': 'COUNT', 'col': '*'}],
             'limit': 20},
            {'name': 'So luong khach theo phan khuc', 'viz': 'bar', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'agg': 'COUNT', 'col': '*'}],
             'limit': 20},
            {'name': 'Doanh thu theo phan khuc khach hang', 'viz': 'bar', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'agg': 'SUM', 'col': 'Monetary'}],
             'limit': 20},
            {'name': 'TOP khach hang VIP theo doanh thu', 'viz': 'table', 'ds': 'DM_CustomerRFM',
             'dims': ['CustomerID', 'Segment', 'RFMScore'],
             'metrics': [{'agg': 'SUM', 'col': 'Monetary'}],
             'limit': 20},
            {'name': 'Ty le Champions vs At Risk', 'viz': 'pie', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'agg': 'COUNT', 'col': '*'}],
             'limit': 10},
        ],
    },
    {
        'slug': 'nhan-vien', 'title': 'Hieu suat Nhan vien',
        'charts': [
            {'name': 'Doanh so theo nhan vien', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['EmployeeID'], 'metrics': [{'agg': 'SUM', 'col': 'Revenue'}],
             'limit': 20},
            {'name': 'So luong san pham ban theo nhan vien', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['EmployeeID'], 'metrics': [{'agg': 'SUM', 'col': 'Quantity'}],
             'limit': 20},
            {'name': 'Doanh thu theo phuong thuc thanh toan', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['PaymentMethod'], 'metrics': [{'agg': 'SUM', 'col': 'Revenue'}],
             'limit': 10},
            {'name': 'TOP nhan vien xuat sac', 'viz': 'table', 'ds': 'FactSales',
             'dims': ['EmployeeID'],
             'metrics': [
                 {'agg': 'SUM', 'col': 'Revenue'},
                 {'agg': 'SUM', 'col': 'Quantity'},
                 {'agg': 'COUNT', 'col': '*'},
             ],
             'limit': 20},
            {'name': 'So don hang theo nhan vien', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['EmployeeID'], 'metrics': [{'agg': 'COUNT', 'col': '*'}],
             'limit': 20},
        ],
    },
]


def get_token():
    import requests
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/login',
        json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
        timeout=30
    )
    r.raise_for_status()
    return r.json()['access_token']


def build_form_data(viz_type, ds_id, ds_name, dims, metrics, row_limit):
    """Build form_data with Superset 3.x compatible format."""
    metrics_params = []
    for m in metrics:
        col = m['col']
        agg = m['agg']
        if col == '*':
            sql_expr = f'COUNT(*)'
            label = 'COUNT(*)'
        else:
            sql_expr = f'{agg}({col})'
            label = f'{agg}({col})'

        metrics_params.append({
            'expressionType': 'SIMPLE',
            'column': {'name': col} if col != '*' else {},
            'aggregate': agg,
            'sqlExpression': sql_expr,
            'label': label,
            'format': 'SMART_NUMBER',
        })

    params = {
        'viz_type': viz_type,
        'datasource': f'{ds_id}__table',
        'datasource_id': ds_id,
        'datasource_name': ds_name,
        'groupby': dims if dims else None,
        'metrics': metrics_params,
        'row_limit': row_limit,
        'order_desc': True,
        'show_legend': True,
        'color_scheme': 'supersetColors',
        'cache_timeout': 300,
    }

    if viz_type in ('big_number', 'single_metric'):
        params.pop('groupby', None)
    if viz_type == 'line':
        params['x_axis_show'] = True
    if viz_type == 'bar':
        params['show_values'] = True
    if viz_type == 'table':
        params['page_length'] = 50

    return params


def create_chart(token, name, viz_type, ds_id, ds_name, dims, metrics, row_limit, description=''):
    """Tạo chart qua REST API với form_data format."""
    import requests

    form_data = build_form_data(viz_type, ds_id, ds_name, dims, metrics, row_limit)

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/chart/',
        json={
            'slice_name': name,
            'description': description,
            'datasource_id': ds_id,
            'datasource_type': 'table',
            'viz_type': viz_type,
            'params': json.dumps(form_data),
            'cache_timeout': 300,
        },
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )

    if r.status_code in (200, 201):
        chart_id = r.json()['id']
        logger.info(f'  [OK] Chart "{name}" (id={chart_id})')
        return chart_id
    logger.warning(f'  [WARN] Chart "{name}": {r.status_code} -- {r.text[:200]}')
    return 0


def delete_old_charts(token, old_ids):
    """Xóa charts cũ."""
    import requests
    deleted = 0
    for cid in old_ids:
        r = requests.delete(
            f'{SUPERSET_URL}/api/v1/chart/{cid}',
            headers={'Authorization': f'Bearer {token}'},
            timeout=15
        )
        if r.status_code in (200, 204):
            deleted += 1
    logger.info(f'  Deleted {deleted}/{len(old_ids)} old charts')
    return deleted


def update_dashboard_positions(token, dash_slug, chart_ids):
    """Update dashboard position_json."""
    import requests
    import json

    dash_id = DASH_SLUG_TO_ID[dash_slug]

    meta = {}
    for cid in chart_ids:
        meta[f'CHART-{cid}'] = {
            'type': 'CHART',
            'id': f'CHART-{cid}',
            'meta': {'chartId': cid, 'width': 6, 'height': 50},
        }

    children = [f'CHART-{cid}' for cid in chart_ids]
    layout = {
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {
            'type': 'GRID', 'id': 'GRID_ID',
            'children': children, 'parents': ['ROOT_ID'],
            'gridSize': {'default': {'rows': 600, 'columns': 12, 'rowHeight': 50}},
        },
        'DASHBOARD_VERSION_KEY': 'v2',
    }
    layout.update(meta)

    r = requests.put(
        f'{SUPERSET_URL}/api/v1/dashboard/{dash_id}',
        json={'position_json': json.dumps(layout)},
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )

    if r.status_code in (200, 201):
        logger.info(f'  [OK] Dashboard "{dash_slug}" positions updated ({len(chart_ids)} charts)')
    else:
        logger.warning(f'  [WARN] Dashboard "{dash_slug}" position: {r.status_code} -- {r.text[:150]}')


def detach_old_charts_from_dashboards(token, old_chart_ids):
    """Detach old charts from dashboards."""
    from superset.app import create_app
    app = create_app()
    with app.app_context():
        from superset.extensions import db
        from superset.models.dashboard import Dashboard, dashboard_slices

        for dash in db.session.query(Dashboard).filter(Dashboard.id.in_(list(DASH_SLUG_TO_ID.values()))).all():
            for cid in old_chart_ids:
                db.session.query(dashboard_slices).filter_by(
                    dashboard_id=dash.id, slice_id=cid
                ).delete()
        db.session.commit()
        logger.info('  Detached old charts from dashboards')


def attach_charts_to_dashboards(token, dash_slug, chart_ids):
    """Attach new charts to dashboards via DB."""
    from superset.app import create_app
    app = create_app()
    with app.app_context():
        from superset.extensions import db
        from superset.models.dashboard import Dashboard, dashboard_slices
        from sqlalchemy import insert

        dash_id = DASH_SLUG_TO_ID[dash_slug]

        for cid in chart_ids:
            existing = db.session.query(dashboard_slices).filter_by(
                dashboard_id=dash_id, slice_id=cid
            ).first()
            if not existing:
                db.session.execute(insert(dashboard_slices).values(
                    dashboard_id=dash_id, slice_id=cid
                ))
        db.session.commit()
        logger.info(f'  [OK] Attached {len(chart_ids)} charts to dashboard "{dash_slug}"')


def main():
    import requests

    logger.info('=' * 60)
    logger.info('Recreating charts with Superset 3.x compatible format')
    logger.info('=' * 60)

    token = get_token()
    logger.info('[OK] Login successful')

    # Old chart IDs to remove (188-217)
    old_ids = list(range(188, 218))
    logger.info(f'[STEP 1] Deleting old charts (188-217)...')
    delete_old_charts(token, old_ids)

    logger.info('[STEP 2] Detaching old charts from dashboards...')
    detach_old_charts_from_dashboards(token, old_ids)

    logger.info('[STEP 3] Creating new charts...')
    all_new_chart_ids = {}
    total = 0

    for dash_cfg in DASHBOARDS:
        dash_slug = dash_cfg['slug']
        logger.info(f'  Dashboard: {dash_cfg["title"]}')
        chart_ids = []

        for chart_cfg in dash_cfg['charts']:
            ds_name = chart_cfg['ds']
            ds_id = DS[ds_name]
            cid = create_chart(
                token=token,
                name=chart_cfg['name'],
                viz_type=chart_cfg['viz'],
                ds_id=ds_id,
                ds_name=ds_name,
                dims=chart_cfg['dims'],
                metrics=chart_cfg['metrics'],
                row_limit=chart_cfg.get('limit', 100),
                description=chart_cfg.get('desc', ''),
            )
            if cid:
                chart_ids.append(cid)
                total += 1

        all_new_chart_ids[dash_slug] = chart_ids

    logger.info(f'[STEP 4] Updating dashboard positions...')
    for slug, chart_ids in all_new_chart_ids.items():
        attach_charts_to_dashboards(token, slug, chart_ids)
        update_dashboard_positions(token, slug, chart_ids)

    logger.info('=' * 60)
    logger.info(f'Complete! Total new charts: {total}')
    logger.info('Refresh dashboards in Superset UI')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
