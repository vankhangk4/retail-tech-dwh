#!/usr/bin/env python3
"""
Sync dataset columns từ MSSQL vào Superset.
Chạy sau khi containers đã up, trước khi user truy cập dashboards.
"""
import os
import sys
import time
import logging
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://localhost:8088')
ADMIN_USER   = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD    = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')

# Dataset IDs cần sync
DATASETS = [
    {'id': 1,  'name': 'FactSales'},
    {'id': 2,  'name': 'FactInventory'},
    {'id': 3,  'name': 'FactPurchase'},
    {'id': 4,  'name': 'DimProduct'},
    {'id': 5,  'name': 'DimCustomer'},
    {'id': 6,  'name': 'DimStore'},
    {'id': 7,  'name': 'DimEmployee'},
    {'id': 8,  'name': 'DimDate'},
    {'id': 9,  'name': 'DM_SalesSummary'},
    {'id': 10, 'name': 'DM_CustomerRFM'},
]


def get_token():
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/login',
        json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
        timeout=30
    )
    r.raise_for_status()
    return r.json()['access_token']


def refresh_dataset(token, ds_id: int, ds_name: str) -> bool:
    """Gọi GET /api/v1/dataset/{id}/ refresh để trigger column sync."""
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    # Method 1: GET /dataset/{id}/ — có thể trigger metadata refresh
    r1 = requests.get(
        f'{SUPERSET_URL}/api/v1/dataset/{ds_id}/',
        headers=headers,
        timeout=30
    )

    if r1.status_code != 200:
        logger.warning(f'  [{ds_name}] GET dataset failed: {r1.status_code}')
    else:
        logger.info(f'  [{ds_name}] GET dataset: OK')

    # Method 2: POST /dataset/{id}/refresh — refresh schema columns
    r2 = requests.post(
        f'{SUPERSET_URL}/api/v1/dataset/{ds_id}/refresh/',
        headers=headers,
        timeout=60
    )

    if r2.status_code in (200, 201):
        logger.info(f'  [{ds_name}] Refresh: OK')
        return True
    else:
        logger.warning(f'  [{ds_name}] Refresh: {r2.status_code} — {r2.text[:200]}')

    # Method 3: PUT /dataset/{id}/ — update metadata
    payload = {
        'dataset': {
            'database_name': 'DWH_MultiTenant_MSSQL',
            'schema': 'dbo',
            'table_name': ds_name,
            'sql': None,
            'is_physical': True,
            'filter_select_enabled': False,
        }
    }
    r3 = requests.put(
        f'{SUPERSET_URL}/api/v1/dataset/{ds_id}/',
        headers=headers,
        json=payload,
        timeout=30
    )
    if r3.status_code in (200, 201):
        logger.info(f'  [{ds_name}] PUT dataset: OK (triggered re-parse)')
        return True
    else:
        logger.warning(f'  [{ds_name}] PUT dataset: {r3.status_code} — {r3.text[:200]}')
        return False


def main():
    logger.info('=' * 60)
    logger.info('Syncing dataset columns from MSSQL')
    logger.info('=' * 60)

    # Wait for Superset to be ready
    logger.info('Waiting for Superset...')
    for i in range(30):
        try:
            r = requests.get(f'{SUPERSET_URL}/health', timeout=5)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(2)
    else:
        logger.error('Superset not ready')
        return 1

    token = get_token()
    logger.info('[OK] Login successful')

    success = 0
    for ds in DATASETS:
        ok = refresh_dataset(token, ds['id'], ds['name'])
        if ok:
            success += 1
        # Throttle to avoid overwhelming the server
        time.sleep(2)

    logger.info('=' * 60)
    logger.info(f'Sync complete: {success}/{len(DATASETS)} datasets refreshed')
    logger.info('Dashboards should now work in Superset UI')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())