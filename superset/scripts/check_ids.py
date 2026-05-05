#!/usr/bin/env python3
import requests, os
SUPERSET_URL = 'http://localhost:8088'
r = requests.post(f'{SUPERSET_URL}/api/v1/security/login', json={'username': 'admin', 'password': 'M1tjtnrx', 'provider': 'db'}, timeout=15)
token = r.json()['access_token']
r = requests.get(f'{SUPERSET_URL}/api/v1/dashboard/', headers={'Authorization': f'Bearer {token}'}, timeout=15)
print(f"Status: {r.status_code}")
d = r.json()
print(f"Total dashboards: {d.get('count', 0)}")
for dash in d.get('result', []):
    print(f"  id={dash['id']} slug={dash['slug']} title={dash['dashboard_title']}")

# Check chart 79
r2 = requests.get(f'{SUPERSET_URL}/api/v1/chart/79/', headers={'Authorization': f'Bearer {token}'}, timeout=15)
print(f"\nChart 79 status: {r2.status_code}")
if r2.status_code == 200:
    c = r2.json()
    print(f"  Title: {c.get('slice_name')}")
    print(f"  Dashboard: {c.get('dash_id')}")
else:
    print(f"  Response: {r2.text[:200]}")
