#!/usr/bin/env python3
"""Update dashboards with chart positions so they show up in the UI."""
import os, sys, json, requests

SUPERSET_URL = 'http://localhost:8088'
ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD  = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')

# Dashboard configs with their chart IDs
DASHBOARDS = [
    {
        'id': 11, 'title': 'Phan tich Doanh thu',
        'chart_ids': [79, 80, 81, 82, 83, 84, 85],
    },
    {
        'id': 12, 'title': 'Phan tich San pham',
        'chart_ids': [86, 87, 88, 89, 90, 91, 92],
    },
    {
        'id': 13, 'title': 'Quan ly Ton kho',
        'chart_ids': [93, 94, 95, 96, 97, 98],
    },
    {
        'id': 14, 'title': 'Phan tich Khach hang',
        'chart_ids': [99, 100, 101, 102, 103],
    },
    {
        'id': 15, 'title': 'Hieu suat Nhan vien',
        'chart_ids': [104, 105, 106, 107, 108],
    },
]

def get_token():
    r = requests.post(
        f'{SUPERSET_URL}/api/v1/security/login',
        json={'username': ADMIN_USER, 'password': ADMIN_PWD, 'provider': 'db'},
        timeout=15
    )
    return r.json()['access_token']

def build_position(chart_ids):
    """Build dashboard position JSON for Superset 3.x."""
    children = [f'CHART-{cid}' for cid in chart_ids]
    meta = {}
    for cid in chart_ids:
        meta[f'CHART-{cid}'] = {
            'type': 'CHART',
            'id': f'CHART-{cid}',
            'meta': {
                'chartId': cid,
                'width': 6,
                'height': 50,
            },
        }
    layout = {
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {
            'type': 'GRID',
            'id': 'GRID_ID',
            'children': children,
            'parents': ['ROOT_ID'],
        },
        'DASHBOARD_VERSION_KEY': 'v2',
    }
    layout.update(meta)
    return json.dumps(layout)

def update_dashboard(token, dash_id, title, chart_ids):
    position = build_position(chart_ids)

    r = requests.put(
        f'{SUPERSET_URL}/api/v1/dashboard/{dash_id}/',
        json={
            'position_json': position,
        },
        headers={'Authorization': f'Bearer {token}'},
        timeout=30
    )

    if r.status_code in (200, 201):
        print(f'  [OK] Dashboard "{title}" (id={dash_id}) updated with {len(chart_ids)} charts')
    else:
        print(f'  [WARN] Dashboard "{title}" (id={dash_id}): {r.status_code} -- {r.text[:200]}')

def main():
    token = get_token()
    for dash in DASHBOARDS:
        update_dashboard(token, dash['id'], dash['title'], dash['chart_ids'])

if __name__ == '__main__':
    main()
