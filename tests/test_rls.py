"""
Unit tests cho tenant isolation / RLS logic.
Kiểm tra JWT payload → RLS clause mapping mà không cần DB hay Superset thực.
"""
import pytest
import jwt
from fastapi import HTTPException

from api.auth import (
    create_access_token,
    decode_token,
    JWT_SECRET,
    ALGORITHM,
)


# ─────────────────────────────────────────────
# Tenant Isolation qua JWT payload
# ─────────────────────────────────────────────

class TestTenantIsolationViaToken:
    def test_viewer_token_contains_tenant_id(self):
        """TenantViewer phải có tenant_id trong token."""
        token = create_access_token(1, 'viewer1', 'STORE_HN', 'viewer')
        payload = decode_token(token)
        assert payload.tenant_id == 'STORE_HN'
        assert payload.role == 'viewer'

    def test_superadmin_token_has_null_tenant(self):
        """SuperAdmin không thuộc tenant nào → tenant_id = None."""
        token = create_access_token(99, 'admin', None, 'superadmin')
        payload = decode_token(token)
        assert payload.tenant_id is None
        assert payload.role == 'superadmin'

    def test_different_tenants_get_different_tokens(self):
        """2 viewers của 2 tenant khác nhau → token khác nhau."""
        token_hn  = create_access_token(1, 'user_hn',  'STORE_HN',  'viewer')
        token_hcm = create_access_token(2, 'user_hcm', 'STORE_HCM', 'viewer')
        assert token_hn != token_hcm

    def test_tenant_hn_cannot_use_hcm_rls(self):
        """Token của STORE_HN không nên cho phép truy cập STORE_HCM."""
        token = create_access_token(1, 'user_hn', 'STORE_HN', 'viewer')
        payload = decode_token(token)
        # RLS clause cho STORE_HN
        rls_clause = f"TenantID = '{payload.tenant_id}'"
        assert 'STORE_HN' in rls_clause
        assert 'STORE_HCM' not in rls_clause

    def test_superadmin_rls_clause_is_unrestricted(self):
        """SuperAdmin (tenant=None) nhận RLS 1=1 (không filter)."""
        token = create_access_token(99, 'admin', None, 'superadmin')
        payload = decode_token(token)
        if payload.role in ('superadmin', 'admin') and payload.tenant_id is None:
            rls_clause = '1=1'
        else:
            rls_clause = f"TenantID = '{payload.tenant_id}'"
        assert rls_clause == '1=1'

    def test_viewer_rls_clause_has_tenant_filter(self):
        """TenantViewer nhận RLS WHERE TenantID='X'."""
        token = create_access_token(2, 'viewer2', 'STORE_HCM', 'viewer')
        payload = decode_token(token)
        if payload.role in ('superadmin', 'admin') and payload.tenant_id is None:
            rls_clause = '1=1'
        else:
            rls_clause = f"TenantID = '{payload.tenant_id}'"
        assert rls_clause == "TenantID = 'STORE_HCM'"


# ─────────────────────────────────────────────
# Token không thể bị giả mạo
# ─────────────────────────────────────────────

class TestTokenSecurity:
    def test_tampered_tenant_id_fails_decode(self):
        """Thay đổi tenant_id trong token → decode phải fail."""
        token = create_access_token(1, 'user', 'STORE_HN', 'viewer')
        parts = token.split('.')
        # Decode payload và thay tenant
        import base64, json
        padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload_bytes = base64.urlsafe_b64decode(padded)
        payload = json.loads(payload_bytes)
        payload['tenant_id'] = 'STORE_HCM'  # giả mạo
        new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        tampered_token = f'{parts[0]}.{new_payload}.{parts[2]}'
        with pytest.raises(HTTPException) as exc:
            decode_token(tampered_token)
        assert exc.value.status_code == 401

    def test_tampered_role_fails_decode(self):
        """Thay đổi role viewer → superadmin trong token → decode phải fail."""
        token = create_access_token(1, 'user', 'STORE_HN', 'viewer')
        parts = token.split('.')
        import base64, json
        padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        payload['role'] = 'superadmin'  # leo quyền
        new_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
        tampered_token = f'{parts[0]}.{new_payload}.{parts[2]}'
        with pytest.raises(HTTPException) as exc:
            decode_token(tampered_token)
        assert exc.value.status_code == 401

    def test_empty_token_raises(self):
        with pytest.raises(HTTPException):
            decode_token('')

    def test_none_token_raises(self):
        with pytest.raises((HTTPException, Exception)):
            decode_token(None)


# ─────────────────────────────────────────────
# Multi-tenant data isolation logic
# ─────────────────────────────────────────────

class TestMultiTenantIsolation:
    def test_each_tenant_gets_own_rls(self):
        """Mỗi tenant có RLS clause riêng biệt."""
        tenants = ['STORE_HN', 'STORE_HCM', 'STORE_DN']
        clauses = set()
        for tid in tenants:
            token = create_access_token(1, f'user_{tid}', tid, 'viewer')
            payload = decode_token(token)
            clauses.add(f"TenantID = '{payload.tenant_id}'")
        assert len(clauses) == 3  # 3 clause khác nhau

    def test_superadmin_sees_all_data(self):
        """SuperAdmin dùng clause 1=1 → không bị filter."""
        token = create_access_token(99, 'admin', None, 'superadmin')
        payload = decode_token(token)
        is_unrestricted = (
            payload.role in ('superadmin', 'admin') and
            payload.tenant_id is None
        )
        assert is_unrestricted is True

    def test_viewer_cannot_be_superadmin(self):
        """viewer role không thể bypass RLS."""
        token = create_access_token(1, 'user', 'STORE_HN', 'viewer')
        payload = decode_token(token)
        is_unrestricted = (
            payload.role in ('superadmin', 'admin') and
            payload.tenant_id is None
        )
        assert is_unrestricted is False
