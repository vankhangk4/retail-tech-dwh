"""
Unit tests cho api/auth.py — password hashing và JWT token logic.
Không cần kết nối DB (các function thuần Python).
"""
import os
import pytest
from datetime import datetime, timezone

import jwt
from fastapi import HTTPException

# env phải được set trước khi import module (xem conftest.py)
from api.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    ACCESS_EXPIRE,
    REFRESH_EXPIRE,
    JWT_SECRET,
    ALGORITHM,
)


# ─────────────────────────────────────────────
# Password hashing
# ─────────────────────────────────────────────

class TestPasswordHashing:
    def test_hash_returns_string(self):
        assert isinstance(hash_password('mypassword'), str)

    def test_hash_not_plaintext(self):
        assert hash_password('mypassword') != 'mypassword'

    def test_bcrypt_prefix(self):
        hashed = hash_password('mypassword')
        assert hashed.startswith('$2b$') or hashed.startswith('$2a$')

    def test_verify_correct_password(self):
        hashed = hash_password('secret123')
        assert verify_password('secret123', hashed) is True

    def test_verify_wrong_password(self):
        hashed = hash_password('secret123')
        assert verify_password('wrongpassword', hashed) is False

    def test_verify_empty_password(self):
        hashed = hash_password('secret123')
        assert verify_password('', hashed) is False

    def test_two_hashes_of_same_password_differ(self):
        """bcrypt dùng random salt nên 2 hash cùng password phải khác nhau."""
        h1 = hash_password('password')
        h2 = hash_password('password')
        assert h1 != h2
        assert verify_password('password', h1)
        assert verify_password('password', h2)

    def test_verify_invalid_hash_returns_false(self):
        assert verify_password('anything', 'not-a-valid-hash') is False


# ─────────────────────────────────────────────
# JWT access token
# ─────────────────────────────────────────────

class TestAccessToken:
    def test_create_returns_string(self):
        token = create_access_token(1, 'alice', 'STORE_HN', 'viewer')
        assert isinstance(token, str)
        assert len(token) > 0

    def test_payload_user_id(self):
        token = create_access_token(42, 'alice', 'STORE_HN', 'viewer')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['user_id'] == 42

    def test_payload_username(self):
        token = create_access_token(1, 'alice', 'STORE_HN', 'viewer')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['username'] == 'alice'

    def test_payload_tenant_id(self):
        token = create_access_token(1, 'alice', 'STORE_HCM', 'viewer')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['tenant_id'] == 'STORE_HCM'

    def test_payload_role(self):
        token = create_access_token(1, 'alice', 'STORE_HN', 'admin')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['role'] == 'admin'

    def test_payload_type_is_access(self):
        token = create_access_token(1, 'alice', 'STORE_HN', 'viewer')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['type'] == 'access'

    def test_superadmin_null_tenant(self):
        token = create_access_token(99, 'superadmin', None, 'superadmin')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['tenant_id'] is None
        assert payload['role'] == 'superadmin'

    def test_expiry_is_8_hours(self):
        token = create_access_token(1, 'alice', 'STORE_HN', 'viewer')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        iat = payload['iat']
        exp = payload['exp']
        diff_seconds = exp - iat
        assert abs(diff_seconds - ACCESS_EXPIRE.total_seconds()) < 5


# ─────────────────────────────────────────────
# JWT refresh token
# ─────────────────────────────────────────────

class TestRefreshToken:
    def test_create_returns_string(self):
        token = create_refresh_token(1, 'alice')
        assert isinstance(token, str)

    def test_payload_type_is_refresh(self):
        token = create_refresh_token(1, 'alice')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['type'] == 'refresh'

    def test_payload_user_id(self):
        token = create_refresh_token(7, 'bob')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        assert payload['user_id'] == 7

    def test_expiry_is_7_days(self):
        token = create_refresh_token(1, 'alice')
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        diff_seconds = payload['exp'] - payload['iat']
        assert abs(diff_seconds - REFRESH_EXPIRE.total_seconds()) < 5


# ─────────────────────────────────────────────
# decode_token
# ─────────────────────────────────────────────

class TestDecodeToken:
    def test_decode_valid_token(self):
        token = create_access_token(5, 'alice', 'STORE_HCM', 'admin')
        result = decode_token(token)
        assert result.user_id == 5
        assert result.username == 'alice'
        assert result.tenant_id == 'STORE_HCM'
        assert result.role == 'admin'

    def test_decode_invalid_token_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_token('invalid.token.value')
        assert exc.value.status_code == 401

    def test_decode_garbage_string_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            decode_token('notavalidjwttoken')
        assert exc.value.status_code == 401

    def test_decode_expired_token_raises_401(self):
        expired_payload = {
            'user_id': 1,
            'username': 'alice',
            'tenant_id': 'STORE_HN',
            'role': 'viewer',
            'exp': datetime(2020, 1, 1, tzinfo=timezone.utc),
            'iat': datetime(2020, 1, 1, tzinfo=timezone.utc),
            'type': 'access',
        }
        expired_token = jwt.encode(expired_payload, JWT_SECRET, algorithm=ALGORITHM)
        with pytest.raises(HTTPException) as exc:
            decode_token(expired_token)
        assert exc.value.status_code == 401

    def test_decode_wrong_secret_raises_401(self):
        token = jwt.encode(
            {'user_id': 1, 'username': 'x', 'tenant_id': None, 'role': 'viewer',
             'exp': 9999999999, 'iat': 0, 'type': 'access'},
            'wrong-secret-key-here-!!',
            algorithm='HS256'
        )
        with pytest.raises(HTTPException) as exc:
            decode_token(token)
        assert exc.value.status_code == 401
