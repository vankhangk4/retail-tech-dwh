#!/usr/bin/env python3
import requests, json

SUPERSET_URL = 'http://localhost:8088'
r = requests.post(f'{SUPERSET_URL}/api/v1/security/login',
    json={'username': 'admin', 'password': 'M1tjtnrx', 'provider': 'db'}, timeout=15)
token = r.json()['access_token']
h = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

# Try different filter approaches
print("=== GET /api/v1/chart/ ===")
r = requests.get(f'{SUPERSET_URL}/api/v1/chart/', headers=h, timeout=15)
print(f"  Status: {r.status_code}, count={r.json().get('count', 0)}")

# Try with datasource_id filter
print("\n=== GET /api/v1/chart/ with datasource_id=9 ===")
r = requests.get(f'{SUPERSET_URL}/api/v1/chart/?q=(filters:!((\"col\":\"datasource_id\",\"opr\":\"eq\",\"value\":9)))',
    headers=h, timeout=15)
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  count={d.get('count', 0)}")

# Try with recent filter
print("\n=== GET /api/v1/chart/ last modified ===")
r = requests.get(f'{SUPERSET_URL}/api/v1/chart/?q=(order_column:changed_on_delta_humanized,order_direction:desc,page:0,page_size:50)',
    headers=h, timeout=15)
print(f"  Status: {r.status_code}")
d = r.json()
print(f"  count={d.get('count', 0)}, result_len={len(d.get('result', []))}")

# Check datasets API
print("\n=== GET /api/v1/dataset/9 ===")
r = requests.get(f'{SUPERSET_URL}/api/v1/dataset/9/', headers=h, timeout=15)
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    ds = r.json()
    print(f"  name: {ds.get('result', {}).get('table_name')}")

# Check if chart 79 is directly accessible
print("\n=== GET /api/v1/chart/79/ ===")
r = requests.get(f'{SUPERSET_URL}/api/v1/chart/79/', headers=h, timeout=15)
print(f"  Status: {r.status_code}")
if r.status_code == 200:
    c = r.json()
    print(f"  name: {c.get('result', {}).get('slice_name')}")
else:
    print(f"  body: {r.text[:200]}")

# Get chart info from list
print("\n=== GET /api/v1/chart/?q=(filters:!((\"col\":\"id\",\"opr\":\"eq\",\"value\":79))) ===")
r = requests.get(f'{SUPERSET_URL}/api/v1/chart/?q=(filters:!((\"col\":\"id\",\"opr\":\"eq\",\"value\":79)))',
    headers=h, timeout=15)
print(f"  Status: {r.status_code}, count={r.json().get('count', 0)}")