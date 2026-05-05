#!/usr/bin/env python3
import requests, os, json

r = requests.post('http://localhost:8088/api/v1/security/login',
    json={'username': 'admin', 'password': 'M1tjtnrx', 'provider': 'db'}, timeout=15)
token = r.json()['access_token']

# Check with and without filters
headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/json'}

# Try with page params
r2 = requests.get('http://localhost:8088/api/v1/chart/?q=(page:0,page_size:100)',
    headers=headers, timeout=15)
print(f"Status: {r2.status_code}")
d = r2.json()
print(f"Keys: {list(d.keys())}")
print(f"Count: {d.get('count', 0)}")
print(f"Result len: {len(d.get('result', []))}")

# Check the raw text
print(f"First 300 chars: {r2.text[:300]}")
