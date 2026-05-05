#!/usr/bin/env python3
import requests, os
SUPERSET_URL = 'http://localhost:8088'
r = requests.post(f'{SUPERSET_URL}/api/v1/security/login', json={'username': 'admin', 'password': 'M1tjtnrx', 'provider': 'db'}, timeout=15)
token = r.json()['access_token']

# List all charts
r = requests.get(f'{SUPERSET_URL}/api/v1/chart/', headers={'Authorization': f'Bearer {token}'}, timeout=15)
d = r.json()
print(f"Total charts: {d.get('count', 0)}")
for c in d.get('result', []):
    print(f"  id={c['id']} slice_name={c['slice_name']} dash_id={c.get('dash_id')}")