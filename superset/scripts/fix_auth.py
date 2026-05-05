#!/usr/bin/env python3
"""
Fix Superset authentication by ensuring admin user has proper credentials
and testing the authentication flow.
"""

import os
import sys
import requests
import json

# Configuration
SUPERSET_URL = os.environ.get('SUPERSET_URL', 'http://superset:8088')
ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')

def test_api_login():
    """Test login via API with provider field."""
    url = f'{SUPERSET_URL}/api/v1/security/login'
    payload = {
        'username': ADMIN_USER,
        'password': ADMIN_PWD,
        'provider': 'db'
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f'✓ API Login successful, token: {token[:50]}...')
            return token
        else:
            print(f'✗ API Login failed: {response.status_code} {response.text}')
            return None
    except Exception as e:
        print(f'✗ API Login error: {e}')
        return None


def test_dashboard_access(token):
    """Test dashboard access with auth token."""
    if not token:
        print('✗ No token, skipping dashboard test')
        return False

    url = f'{SUPERSET_URL}/api/v1/dashboard/1'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            dashboard = data.get('result', {})
            print(f'✓ Dashboard access successful: {dashboard.get("dashboard_title")}')
            return True
        else:
            print(f'✗ Dashboard access failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'✗ Dashboard access error: {e}')
        return False


def test_charts_access(token):
    """Test charts access with auth token."""
    if not token:
        print('✗ No token, skipping charts test')
        return False

    url = f'{SUPERSET_URL}/api/v1/chart/'
    headers = {'Authorization': f'Bearer {token}'}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('result', []))
            print(f'✓ Charts access successful: {count} charts available')
            return True
        else:
            print(f'✗ Charts access failed: {response.status_code}')
            return False
    except Exception as e:
        print(f'✗ Charts access error: {e}')
        return False


if __name__ == '__main__':
    print('[AUTH-FIX] Testing Superset authentication...')
    print(f'[AUTH-FIX] URL: {SUPERSET_URL}')
    print(f'[AUTH-FIX] User: {ADMIN_USER}')
    print()

    # Test API login
    token = test_api_login()
    print()

    # Test dashboard access
    test_dashboard_access(token)
    print()

    # Test charts access
    test_charts_access(token)
    print()

    if token:
        print('[AUTH-FIX] ✓ Authentication is working!')
        print(f'[AUTH-FIX] Use this token for API calls:')
        print(f'[AUTH-FIX]   Authorization: Bearer {token}')
        sys.exit(0)
    else:
        print('[AUTH-FIX] ✗ Authentication failed')
        sys.exit(1)
