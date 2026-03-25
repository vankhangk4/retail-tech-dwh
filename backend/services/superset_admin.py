"""
Superset Admin API integration (shared dashboard model).

Current architecture:
- One shared Data Warehouse database for all tenants
- One shared Superset dashboard
- Tenant isolation enforced by Guest Token RLS clause (TenantId)
"""

import asyncio
import httpx
import logging
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SupersetAdminService:
    """
    Thin wrapper around Superset Admin REST API (v1).
    Uses a persistent httpx client to maintain session cookies (required for CSRF).
    """

    def __init__(self):
        self.base_url = settings.SUPERSET_URL.rstrip("/")
        self.admin_user = settings.SUPERSET_ADMIN_USER
        self.admin_pass = settings.SUPERSET_ADMIN_PASSWORD
        self._admin_token: str | None = None
        self._csrf_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Persistent client that preserves cookies across requests."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def _admin_login(self) -> str:
        if self._admin_token:
            return self._admin_token

        client = await self._get_client()
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                resp = await client.post(
                    f"{self.base_url}/api/v1/security/login",
                    json={
                        "username": self.admin_user,
                        "password": self.admin_pass,
                        "provider": "db",
                    },
                )
                resp.raise_for_status()
                token = resp.json().get("access_token")
                if not token:
                    raise Exception("Superset login: no access_token")
                self._admin_token = token
                return token
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429 and attempt < 2:
                    await asyncio.sleep(1.0 * (2 ** attempt))
                else:
                    break
        raise Exception(f"Superset login failed: {last_error}")

    async def _get_csrf_token(self) -> str:
        if self._csrf_token:
            return self._csrf_token
        token = await self._admin_login()
        client = await self._get_client()
        resp = await client.get(
            f"{self.base_url}/api/v1/security/csrf_token/",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == 200:
            self._csrf_token = resp.json().get("result", "")
        return self._csrf_token or ""

    async def _admin_headers(self) -> dict:
        token = await self._admin_login()
        csrf = await self._get_csrf_token()
        h = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Referer": self.base_url,
        }
        if csrf:
            h["X-CSRFToken"] = csrf
        return h

    async def ensure_tenant_superset_setup(self, tenant_id: str) -> dict:
        """
        Backward-compatible no-op for shared dashboard architecture.
        Kept to avoid breaking older callers.
        """
        logger.info(
            "Shared Superset mode active; skipping per-tenant Superset provisioning for tenant '%s'",
            tenant_id,
        )
        return {
            "db_name": settings.SHARED_DWH_DB,
            "dashboard_id": settings.SUPERSET_SHARED_DASHBOARD_ID,
        }


_superset_admin: SupersetAdminService | None = None


def get_superset_admin() -> SupersetAdminService:
    global _superset_admin
    if _superset_admin is None:
        _superset_admin = SupersetAdminService()
    return _superset_admin
