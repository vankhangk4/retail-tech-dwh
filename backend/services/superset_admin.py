"""
Superset Admin API integration.
Handles auto-provisioning of Superset for new tenants:
- Register tenant database in Superset
- Create guest user per tenant
- Create tenant-specific role and assign user
- Clone template dashboard for each tenant

Note: Row-Level Security (RLS) is applied via guest_token's embedded clause
parameter (not a separate API endpoint).
"""

import asyncio
import io
import json
import re
import uuid as uuid_mod
import zipfile
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

    TEMPLATE_DASHBOARD_ID = 1  # Dashboard tạo bởi SuperAdmin làm template

    def __init__(self):
        self.base_url = settings.SUPERSET_URL.rstrip("/")
        self.admin_user = settings.SUPERSET_ADMIN_USER
        self.admin_pass = settings.SUPERSET_ADMIN_PASSWORD
        self._admin_token: str | None = None
        self._csrf_token: str | None = None
        self._client: httpx.AsyncClient | None = None
        self._setup_cache: dict[str, dict] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        """Persistent client that preserves cookies across requests."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    # ----------------------------------------------------------
    # Auth & headers
    # ----------------------------------------------------------

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

    # ----------------------------------------------------------
    # Database
    # ----------------------------------------------------------

    async def _get_database_by_name(self, db_name: str) -> dict | None:
        headers = await self._admin_headers()
        client = await self._get_client()
        resp = await client.get(f"{self.base_url}/api/v1/database/", headers=headers)
        if resp.status_code == 200:
            for db in resp.json().get("result", []):
                if db.get("database_name") == db_name:
                    return db
        return None

    async def register_tenant_database(self, tenant_id: str, db_name: str) -> int:
        existing = await self._get_database_by_name(db_name)
        if existing:
            logger.info(f"DB '{db_name}' already registered (id={existing['id']})")
            return existing["id"]

        sqlalchemy_uri = (
            f"mssql+pyodbc://{settings.MSSQL_USER}:{settings.MSSQL_PASSWORD}"
            f"@{settings.MSSQL_HOST}:{settings.MSSQL_PORT}/{db_name}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )

        headers = await self._admin_headers()
        client = await self._get_client()
        resp = await client.post(
            f"{self.base_url}/api/v1/database/",
            headers=headers,
            json={
                "database_name": db_name,
                "sqlalchemy_uri": sqlalchemy_uri,
                "expose_in_sqllab": True,
                "allow_run_async": False,
            },
        )

        if resp.status_code in (200, 201):
            db_id = resp.json().get("id")
            logger.info(f"Registered DB '{db_name}' (id={db_id})")
            return db_id

        logger.warning(f"Could not register DB '{db_name}': {resp.text}")
        # Fallback: search existing
        list_resp = await client.get(f"{self.base_url}/api/v1/database/", headers=headers)
        if list_resp.status_code == 200:
            for db in list_resp.json().get("result", []):
                if db.get("database_name") == db_name:
                    return db["id"]
        raise Exception(f"Cannot register DB: {resp.text}")

    # ----------------------------------------------------------
    # User & Role
    # ----------------------------------------------------------

    async def _create_or_get_tenant_user(self, tenant_id: str) -> dict:
        username = f"tenant_{tenant_id}"
        headers = await self._admin_headers()
        client = await self._get_client()

        resp = await client.post(
            f"{self.base_url}/api/v1/security/users/",
            headers=headers,
            json={
                "username": username,
                "first_name": "Tenant",
                "last_name": tenant_id,
                "email": f"tenant_{tenant_id}@localhost",
                "roles": [],
            },
        )
        if resp.status_code == 201:
            return resp.json()

        # User exists — find it
        list_resp = await client.get(f"{self.base_url}/api/v1/security/users/", headers=headers)
        if list_resp.status_code == 200:
            for u in list_resp.json().get("result", []):
                if u.get("username") == username:
                    return u
        raise Exception(f"Cannot create/get user '{username}'")

    async def _create_or_get_tenant_role(self, tenant_id: str) -> dict:
        role_name = f"Tenant_{tenant_id}"
        headers = await self._admin_headers()
        client = await self._get_client()

        resp = await client.post(
            f"{self.base_url}/api/v1/security/roles/",
            headers=headers,
            json={"name": role_name},
        )
        if resp.status_code == 201:
            return resp.json()

        list_resp = await client.get(f"{self.base_url}/api/v1/security/roles/", headers=headers)
        if list_resp.status_code == 200:
            for r in list_resp.json().get("result", []):
                if r.get("name") == role_name:
                    return r
        raise Exception(f"Cannot create/get role '{role_name}'")

    async def _assign_user_to_role(self, username: str, role_id: int):
        headers = await self._admin_headers()
        client = await self._get_client()
        resp = await client.post(
            f"{self.base_url}/api/v1/security/roles/{role_id}/users/",
            headers=headers,
            json={"username": username},
        )
        if resp.status_code not in (200, 201):
            logger.warning(f"Could not assign user to role: {resp.text}")

    # ----------------------------------------------------------
    # Dashboard cloning
    # ----------------------------------------------------------

    async def _find_dashboard_by_title(self, title: str) -> dict | None:
        headers = await self._admin_headers()
        client = await self._get_client()
        resp = await client.get(
            f"{self.base_url}/api/v1/dashboard/",
            headers=headers,
            params={
                "q": json.dumps({
                    "filters": [{"col": "dashboard_title", "opr": "eq", "value": title}]
                })
            },
        )
        if resp.status_code == 200:
            results = resp.json().get("result", [])
            if results:
                return results[0]
        return None

    async def _export_dashboard(self, dashboard_id: int) -> bytes:
        headers = await self._admin_headers()
        client = await self._get_client()
        resp = await client.get(
            f"{self.base_url}/api/v1/dashboard/export/",
            headers=headers,
            params={"q": f"[{dashboard_id}]"},
        )
        resp.raise_for_status()
        return resp.content

    def _remap_zip_for_tenant(
        self, zip_bytes: bytes, tenant_id: str, db_name: str
    ) -> bytes:
        uuid_pattern = re.compile(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        )
        tenant_uri = (
            f"mssql+pyodbc://{settings.MSSQL_USER}:{settings.MSSQL_PASSWORD}"
            f"@{settings.MSSQL_HOST}:{settings.MSSQL_PORT}/{db_name}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )

        uuid_map: dict[str, str] = {}
        in_zip = zipfile.ZipFile(io.BytesIO(zip_bytes))
        all_content: dict[str, str | None] = {}

        for name in in_zip.namelist():
            try:
                content = in_zip.read(name).decode("utf-8")
                all_content[name] = content
                for old_uuid in uuid_pattern.findall(content):
                    if old_uuid not in uuid_map:
                        seed = f"{tenant_id}:{old_uuid}"
                        uuid_map[old_uuid] = str(uuid_mod.uuid5(uuid_mod.NAMESPACE_DNS, seed))
            except UnicodeDecodeError:
                all_content[name] = None

        out_buffer = io.BytesIO()
        with zipfile.ZipFile(out_buffer, "w", zipfile.ZIP_DEFLATED) as out_zip:
            for name, content in all_content.items():
                if content is None:
                    out_zip.writestr(name, in_zip.read(name))
                    continue
                for old_uuid, new_uuid in uuid_map.items():
                    content = content.replace(old_uuid, new_uuid)
                if name.startswith("databases/"):
                    content = re.sub(r"(database_name:)\s*.*", f"\\1 {db_name}", content)
                    content = re.sub(r"(sqlalchemy_uri:)\s*.*", f"\\1 {tenant_uri}", content)
                if name.startswith("dashboards/"):
                    content = re.sub(r"(dashboard_title:)\s*.*", f"\\1 Dashboard_{tenant_id}", content)
                    content = re.sub(r"(slug:)\s*.*", f"\\1 dashboard-{tenant_id}", content)
                out_zip.writestr(name, content)
        in_zip.close()
        return out_buffer.getvalue()

    async def _import_dashboard(self, zip_bytes: bytes) -> bool:
        headers = await self._admin_headers()
        headers.pop("Content-Type", None)
        client = await self._get_client()
        resp = await client.post(
            f"{self.base_url}/api/v1/dashboard/import/",
            headers=headers,
            files={"formData": ("dashboard.zip", zip_bytes, "application/zip")},
            data={"overwrite": "true"},
        )
        if resp.status_code == 200:
            logger.info("Dashboard imported successfully")
            return True
        logger.error(f"Dashboard import failed: {resp.status_code} {resp.text}")
        return False

    async def _get_or_create_tenant_dashboard(
        self, tenant_id: str, db_id: int, db_name: str
    ) -> int:
        dashboard_title = f"Dashboard_{tenant_id}"

        existing = await self._find_dashboard_by_title(dashboard_title)
        if existing:
            logger.info(f"Dashboard '{dashboard_title}' exists (id={existing['id']})")
            return existing["id"]

        try:
            logger.info(f"Cloning template dashboard for tenant '{tenant_id}'...")
            zip_data = await self._export_dashboard(self.TEMPLATE_DASHBOARD_ID)
            tenant_zip = self._remap_zip_for_tenant(zip_data, tenant_id, db_name)
            success = await self._import_dashboard(tenant_zip)
            if success:
                new_dash = await self._find_dashboard_by_title(dashboard_title)
                if new_dash:
                    logger.info(f"Created dashboard '{dashboard_title}' (id={new_dash['id']})")
                    return new_dash["id"]
        except Exception as e:
            logger.error(f"Failed to clone dashboard for tenant {tenant_id}: {e}")

        logger.warning(f"Fallback to template dashboard for tenant {tenant_id}")
        return self.TEMPLATE_DASHBOARD_ID

    # ----------------------------------------------------------
    # Main entry point
    # ----------------------------------------------------------

    async def ensure_tenant_superset_setup(self, tenant_id: str) -> dict:
        if tenant_id in self._setup_cache:
            return self._setup_cache[tenant_id]

        db_name = f"DWH_{tenant_id}"
        db_id = await self.register_tenant_database(tenant_id, db_name)
        user_data = await self._create_or_get_tenant_user(tenant_id)
        role_data = await self._create_or_get_tenant_role(tenant_id)
        await self._assign_user_to_role(user_data["username"], role_data["id"])
        dashboard_id = await self._get_or_create_tenant_dashboard(tenant_id, db_id, db_name)

        logger.info(f"Superset setup complete for tenant '{tenant_id}'")
        result = {
            "db_id": db_id,
            "role_id": role_data["id"],
            "username": user_data["username"],
            "db_name": db_name,
            "dashboard_id": dashboard_id,
        }
        self._setup_cache[tenant_id] = result
        return result


_superset_admin: SupersetAdminService | None = None


def get_superset_admin() -> SupersetAdminService:
    global _superset_admin
    if _superset_admin is None:
        _superset_admin = SupersetAdminService()
    return _superset_admin
