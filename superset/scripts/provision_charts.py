#!/usr/bin/env python3
"""
Chart Provisioning Script - Theo de cuong Nguyen Van Khang
Tao day du charts cho 5 dashboard: Doanh thu, San pham, Ton kho, Khach hang, Nhan vien
Dua tren FR-17 -> FR-22 trong de cuong do an tot nghiep.
"""

import os
import sys
import json
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD  = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')
SUPERSET_URL = 'http://localhost:8088'

# Dataset IDs (da biet tu Superset DB)
DS = {
    'DM_SalesSummary': 9,
    'DM_CustomerRFM':  10,
    'FactSales':       1,
    'FactInventory':    2,
    'FactPurchase':     3,
    'DimProduct':       4,
    'DimCustomer':      5,
    'DimStore':         6,
    'DimEmployee':      7,
    'DimDate':          8,
}

# Charts cho 5 Dashboard
DASHBOARDS = [
    {
        'id': 1, 'slug': 'doanh-thu', 'title': 'Phan tich Doanh thu',
        'charts': [
            {'name': 'Doanh thu theo thang', 'viz': 'line', 'ds': 'DM_SalesSummary',
             'dims': ['Month'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Bieu do duong doanh thu theo thang', 'limit': 100},
            {'name': 'Doanh thu theo quy', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Quarter'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'So sanh doanh thu giua cac quy', 'limit': 10},
            {'name': 'So sanh cung ky nam truoc', 'viz': 'line', 'ds': 'DM_SalesSummary',
             'dims': ['Year', 'Month'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'So sanh doanh thu cung thang giua cac nam', 'limit': 100},
            {'name': 'Doanh thu theo danh muc', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Doanh thu theo danh muc san pham', 'limit': 50},
            {'name': 'Ty le dong gop doanh thu theo danh muc', 'viz': 'pie', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Pie chart ty le dong gop doanh thu theo danh muc', 'limit': 20},
            {'name': 'TOP 10 san pham ban chay', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['ProductID'], 'metrics': [{'label': 'SUM(Quantity)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'TOP 10 san pham co so luong ban cao nhat', 'limit': 10},
            {'name': 'Doanh thu va loi nhuan theo thang', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Month'],
             'metrics': [
                 {'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'},
                 {'label': 'SUM(TotalProfit)', 'agg': 'SUM', 'format': 'SMART_NUMBER'},
             ],
             'desc': 'Stacked bar - doanh thu va loi nhuan gop theo thang', 'limit': 50},
        ],
    },
    {
        'id': 2, 'slug': 'san-pham', 'title': 'Phan tich San pham',
        'charts': [
            {'name': 'TOP san pham theo so luong ban', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['ProductID'], 'metrics': [{'label': 'SUM(Quantity)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'TOP san pham theo so luong ban ra', 'limit': 10},
            {'name': 'TOP san pham theo doanh thu', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['ProductID'], 'metrics': [{'label': 'SUM(Revenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'TOP san pham theo tong doanh thu', 'limit': 10},
            {'name': 'Phan bo doanh thu theo danh muc', 'viz': 'pie', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Phan bo doanh thu theo danh muc san pham', 'limit': 20},
            {'name': 'Bien loi nhuan gop theo danh muc', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Category'], 'metrics': [{'label': 'SUM(TotalProfit)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Bien loi nhuan gop theo tung danh muc san pham', 'limit': 20},
            {'name': 'Doanh thu theo danh muc va thang', 'viz': 'bar', 'ds': 'DM_SalesSummary',
             'dims': ['Category', 'Month'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Doanh thu theo danh muc x thang', 'limit': 100},
            {'name': 'Xu huong san pham theo thang', 'viz': 'line', 'ds': 'DM_SalesSummary',
             'dims': ['Month'], 'metrics': [{'label': 'SUM(TotalRevenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Xu huong doanh thu san pham theo thang', 'limit': 50},
            {'name': 'Tong so san pham da ban', 'viz': 'big_number', 'ds': 'FactSales',
             'dims': [], 'metrics': [{'label': 'SUM(Quantity)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Tong so luong san pham da ban', 'limit': 10},
        ],
    },
    {
        'id': 3, 'slug': 'ton-kho', 'title': 'Quan ly Ton kho',
        'charts': [
            {'name': 'Canh bao ton kho duoi nguong', 'viz': 'table', 'ds': 'FactInventory',
             'dims': ['ProductID', 'StoreKey'],
             'metrics': [{'label': 'SUM(QuantityOnHand)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'San pham co QuantityOnHand nho hon hoac bang ReorderLevel',
             'limit': 50},
            {'name': 'Ton kho theo cua hang', 'viz': 'bar', 'ds': 'FactInventory',
             'dims': ['StoreKey'], 'metrics': [{'label': 'SUM(QuantityOnHand)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Tong ton kho theo tung cua hang', 'limit': 20},
            {'name': 'Xu huong ton kho theo ngay', 'viz': 'line', 'ds': 'FactInventory',
             'dims': ['CheckDate'], 'metrics': [{'label': 'SUM(QuantityOnHand)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Xu huong thay doi ton kho theo thoi gian', 'limit': 100},
            {'name': 'Phan bo ton kho theo san pham', 'viz': 'pie', 'ds': 'FactInventory',
             'dims': ['ProductID'], 'metrics': [{'label': 'SUM(QuantityOnHand)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Ty le ton kho theo san pham', 'limit': 20},
            {'name': 'TOP san pham ton kho cao nhat', 'viz': 'bar', 'ds': 'FactInventory',
             'dims': ['ProductID'], 'metrics': [{'label': 'SUM(QuantityOnHand)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'TOP san pham co ton kho cao nhat', 'limit': 10},
            {'name': 'Tong so luong ton kho', 'viz': 'big_number', 'ds': 'FactInventory',
             'dims': [], 'metrics': [{'label': 'SUM(QuantityOnHand)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Tong so luong ton kho hien tai', 'limit': 10},
        ],
    },
    {
        'id': 4, 'slug': 'khach-hang', 'title': 'Phan tich Khach hang',
        'charts': [
            {'name': 'Phan bo phan khuc khach hang RFM', 'viz': 'pie', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'label': 'COUNT(*)', 'agg': 'COUNT', 'format': 'SMART_NUMBER'}],
             'desc': 'Phan bo khach hang theo RFM segment (Champions, Loyal, At Risk, Lost, Potential)',
             'limit': 20},
            {'name': 'So luong khach theo phan khuc', 'viz': 'bar', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'label': 'COUNT(*)', 'agg': 'COUNT', 'format': 'SMART_NUMBER'}],
             'desc': 'So luong khach hang theo tung phan khuc RFM', 'limit': 20},
            {'name': 'Doanh thu theo phan khuc khach hang', 'viz': 'bar', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'label': 'SUM(Monetary)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Tong doanh thu theo tung phan khuc RFM', 'limit': 20},
            {'name': 'TOP khach hang VIP theo doanh thu', 'viz': 'table', 'ds': 'DM_CustomerRFM',
             'dims': ['CustomerID', 'Segment', 'RFMScore'],
             'metrics': [{'label': 'SUM(Monetary)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'TOP khach hang theo tong doanh thu', 'limit': 20},
            {'name': 'Ty le Champions vs At Risk', 'viz': 'pie', 'ds': 'DM_CustomerRFM',
             'dims': ['Segment'], 'metrics': [{'label': 'COUNT(*)', 'agg': 'COUNT', 'format': 'SMART_NUMBER'}],
             'desc': 'So sanh Champions (khach tot) vs At Risk (kha nguy mat)',
             'limit': 10},
        ],
    },
    {
        'id': 5, 'slug': 'nhan-vien', 'title': 'Hieu suat Nhan vien',
        'charts': [
            {'name': 'Doanh so theo nhan vien', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['EmployeeID'], 'metrics': [{'label': 'SUM(Revenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Tong doanh thu theo tung nhan vien', 'limit': 20},
            {'name': 'So luong san pham ban theo nhan vien', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['EmployeeID'], 'metrics': [{'label': 'SUM(Quantity)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'So luong san pham da ban theo nhan vien', 'limit': 20},
            {'name': 'Doanh thu theo phuong thuc thanh toan', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['PaymentMethod'], 'metrics': [{'label': 'SUM(Revenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'}],
             'desc': 'Phan bo doanh thu theo phuong thuc thanh toan', 'limit': 10},
            {'name': 'TOP nhan vien xuat sac', 'viz': 'table', 'ds': 'FactSales',
             'dims': ['EmployeeID'],
             'metrics': [
                 {'label': 'SUM(Revenue)', 'agg': 'SUM', 'format': 'SMART_NUMBER'},
                 {'label': 'SUM(Quantity)', 'agg': 'SUM', 'format': 'SMART_NUMBER'},
                 {'label': 'COUNT(*)', 'agg': 'COUNT', 'format': 'SMART_NUMBER'},
             ],
             'desc': 'TOP nhan vien theo doanh thu va so luong ban', 'limit': 20},
            {'name': 'So don hang theo nhan vien', 'viz': 'bar', 'ds': 'FactSales',
             'dims': ['EmployeeID'], 'metrics': [{'label': 'COUNT(*)', 'agg': 'COUNT', 'format': 'SMART_NUMBER'}],
             'desc': 'So don hang theo tung nhan vien', 'limit': 20},
        ],
    },
]


def get_token():
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/login',
        json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
        timeout=15
    )
    if r.status_code != 200:
        raise RuntimeError(f'Login failed: {r.status_code} {r.text}')
    return r.json()['access_token']


def create_chart(token, name, viz_type, ds_name, dims, metrics, row_limit=100, description=''):
    ds_id = DS[ds_name]

    metrics_params = []
    for m in metrics:
        metrics_params.append({
            'expressionType': 'SIMPLE',
            'column': {},
            'aggregate': m['agg'],
            'sqlExpression': m['label'],
            'label': m['label'],
            'format': m.get('format', 'SMART_NUMBER'),
        })

    params = {
        'viz_type': viz_type,
        'datasource': f'{ds_id}__table',
        'groupby': dims if dims else None,
        'metrics': metrics_params,
        'row_limit': row_limit,
        'order_desc': True,
        'show_legend': True,
        'color_scheme': 'supersetColors',
    }

    if viz_type in ('big_number', 'single_metric'):
        params.pop('groupby', None)
    if viz_type == 'line':
        params['x_axis_show'] = True
    if viz_type == 'bar':
        params['show_values'] = True

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/chart/',
        json={
            'slice_name': name,
            'description': description,
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
        logger.info(f'  [OK] Chart "{name}" (id={chart_id}, viz={viz_type})')
        return chart_id
    logger.warning(f'  [WARN] Chart "{name}": {r.status_code} -- {r.text[:200]}')
    return 0


def create_dashboard(token, title, slug, description, chart_ids):
    payload = {
        'dashboard_title': title,
        'slug': slug,
        'published': True,
        'owners': [1],
    }

    r = requests.post(
        f'{SUPERSET_URL}/api/v1/dashboard/',
        json=payload,
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )

    if r.status_code in (200, 201):
        dash_id = r.json()['id']
        logger.info(f'  [OK] Dashboard "{title}" (id={dash_id})')
        return dash_id
    logger.warning(f'  [WARN] Dashboard "{title}": {r.status_code} -- {r.text[:200]}')
    return 0


def main():
    logger.info('=' * 60)
    logger.info('Chart Provisioning -- Theo de cuong Nguyen Van Khang')
    logger.info('5 Dashboards voi 29 charts')
    logger.info('=' * 60)

    token = get_token()
    total_charts = 0

    for dash_cfg in DASHBOARDS:
        dash_title = dash_cfg['title']
        logger.info(f'\n[Dashboard] {dash_title} ({len(dash_cfg["charts"])} charts)')

        chart_ids = []
        for chart_cfg in dash_cfg['charts']:
            cid = create_chart(
                token=token,
                name=chart_cfg['name'],
                viz_type=chart_cfg['viz'],
                ds_name=chart_cfg['ds'],
                dims=chart_cfg['dims'],
                metrics=chart_cfg['metrics'],
                row_limit=chart_cfg.get('limit', 100),
                description=chart_cfg.get('desc', ''),
            )
            chart_ids.append(cid)
            if cid:
                total_charts += 1

        dash_id = create_dashboard(
            token=token,
            title=dash_title,
            slug=dash_cfg['slug'],
            description=dash_cfg.get('description', ''),
            chart_ids=chart_ids,
        )

    logger.info('\n' + '=' * 60)
    logger.info(f'Complete! Total charts created: {total_charts}')
    logger.info('=' * 60)


if __name__ == '__main__':
    main()
