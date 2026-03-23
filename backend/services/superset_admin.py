"""
Superset Admin API integration.
Handles auto-provisioning of Superset for new tenants:
- Register tenant database in Superset
- Create guest user per tenant
- Create tenant-specific role and assign user

Note: Row-Level Security (RLS) is applied via guest_token's embedded clause
parameter (not a separate API endpoint).
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
    Used to auto-configure Superset when a tenant user first accesses Reports.
    """

    def __init__(self):
        self.base_url = settings.SUPERSET_URL.rstrip("/")
        self.admin_user = settings.SUPERSET_ADMIN_USER
        self.admin_pass = settings.SUPERSET_ADMIN_PASSWORD
        self._admin_token: str | None = None
        self._setup_cache: dict[str, dict] = {}  # tenant_id -> setup result

    async def _admin_login(self) -> str:
        """Login as Superset admin and return access token. Cached per instance."""
        if self._admin_token:
            return self._admin_token  # type: ignore[return-value]

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
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
                        raise Exception("Superset login response missing access_token")
                    self._admin_token = token
                    return token
            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code == 429 and attempt < 2:
                    delay = 1.0 * (2 ** attempt)
                    logger.warning(f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/3)")
                    await asyncio.sleep(delay)
                else:
                    break

        logger.error(f"Superset admin login failed: {last_error}")
        raise Exception(f"Không thể đăng nhập Superset")

    async def _admin_headers(self) -> dict:
        token = await self._admin_login()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _get_database_by_name(self, db_name: str) -> dict | None:
        """Find Superset database by name. Returns dict with id or None."""
        headers = await self._admin_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{self.base_url}/api/v1/database/",
                headers=headers,
            )
            if resp.status_code == 200:
                result = resp.json().get("result", [])
                for db in result:
                    if db.get("database_name") == db_name:
                        return db
            return None

    async def register_tenant_database(self, tenant_id: str, db_name: str) -> int:  # type: ignore[return]
        """
        Register or get tenant's SQL Server database in Superset.
        Returns Superset database id.
        """
        # Check if already registered
        existing = await self._get_database_by_name(db_name)
        if existing:
            logger.info(f"Superset database '{db_name}' already registered (id={existing['id']})")
            return existing["id"]

        # Build SQLAlchemy URI for tenant's DWH database
        sqlalchemy_uri = (
            f"mssql+pyodbc://{settings.MSSQL_USER}:{settings.MSSQL_PASSWORD}"
            f"@{settings.MSSQL_HOST}:{settings.MSSQL_PORT}/{db_name}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )

        headers = await self._admin_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
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

            if resp.status_code == 200:
                db_id = resp.json().get("id")
                logger.info(f"Registered Superset database '{db_name}' (id={db_id})")
                return db_id
            elif resp.status_code == 400:
                # DB might already exist — find by host pattern
                logger.warning(f"Could not register DB '{db_name}': {resp.text}")
                list_resp = await client.get(
                    f"{self.base_url}/api/v1/database/",
                    headers=headers,
                )
                if list_resp.status_code == 200:
                    for db in list_resp.json().get("result", []):
                        params = db.get("parameters", {})
                        if settings.MSSQL_HOST in str(params):
                            return db["id"]
                raise Exception(f"Không thể đăng ký database Superset: {resp.text}")
            else:
                raise Exception(f"Không thể đăng ký database Superset: {resp.status_code}")

    async def _create_or_get_tenant_user(self, tenant_id: str) -> dict:  # type: ignore[return]
        """
        Create or get Superset user for tenant.
        Returns dict with username and id.
        """
        username = f"tenant_{tenant_id}"
        headers = await self._admin_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to create user
            create_resp = await client.post(
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

            if create_resp.status_code == 201:
                user_data = create_resp.json()
                logger.info(f"Created Superset user '{username}' (id={user_data['id']})")
                return user_data
            elif create_resp.status_code == 400:
                # User already exists — get by username
                list_resp = await client.get(
                    f"{self.base_url}/api/v1/security/users/",
                    headers=headers,
                )
                if list_resp.status_code == 200:
                    for u in list_resp.json().get("result", []):
                        if u.get("username") == username:
                            logger.info(f"Superset user '{username}' already exists (id={u['id']})")
                            return u
                    raise Exception(f"Không thể tìm Superset user '{username}'")
                raise Exception(f"Không thể tìm Superset user '{username}'")
            else:
                raise Exception(f"Không thể tạo Superset user: {create_resp.text}")

    async def _create_or_get_tenant_role(self, tenant_id: str) -> dict:  # type: ignore[return]
        """
        Create or get tenant-specific role.
        Returns dict with name and id.
        """
        role_name = f"Tenant_{tenant_id}"
        headers = await self._admin_headers()

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Try to create role
            create_resp = await client.post(
                f"{self.base_url}/api/v1/security/roles/",
                headers=headers,
                json={"name": role_name},
            )

            if create_resp.status_code == 201:
                role_data = create_resp.json()
                logger.info(f"Created Superset role '{role_name}' (id={role_data['id']})")
                return role_data
            elif create_resp.status_code == 400:
                # Role exists — get by name
                list_resp = await client.get(
                    f"{self.base_url}/api/v1/security/roles/",
                    headers=headers,
                )
                if list_resp.status_code == 200:
                    for r in list_resp.json().get("result", []):
                        if r.get("name") == role_name:
                            logger.info(f"Superset role '{role_name}' already exists (id={r['id']})")
                            return r
                    raise Exception(f"Không thể tìm Superset role '{role_name}'")
                raise Exception(f"Không thể tìm Superset role '{role_name}'")
            else:
                raise Exception(f"Không thể tạo Superset role: {create_resp.text}")

    async def _assign_user_to_role(self, username: str, role_id: int):
        """Assign Superset user to a role."""
        headers = await self._admin_headers()
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/v1/security/roles/{role_id}/users/",
                headers=headers,
                json={"username": username},
            )
            if resp.status_code in (200, 201):
                logger.info(f"Assigned Superset user '{username}' to role {role_id}")
            elif resp.status_code == 400 and "already assigned" in resp.text.lower():
                pass  # Already assigned, fine
            else:
                logger.warning(f"Could not assign user to role: {resp.text}")

    async def ensure_tenant_superset_setup(self, tenant_id: str) -> dict:
        """
        Main entry point. Provisions Superset resources for a tenant:
          1. Register tenant database
          2. Create tenant guest user
          3. Create tenant role
          4. Assign user to role
        RLS filtering is handled by guest_token's embedded clause parameter.
        Returns dict with {db_id, role_id, username, db_name} on success.
        """
        # Return cached result if already provisioned
        if tenant_id in self._setup_cache:
            logger.info(f"Superset setup for tenant '{tenant_id}' already cached")
            return self._setup_cache[tenant_id]

        db_name = f"DWH_{tenant_id}"

        # Step 1: Register tenant database
        db_id = await self.register_tenant_database(tenant_id, db_name)

        # Step 2: Create tenant user
        user_data = await self._create_or_get_tenant_user(tenant_id)

        # Step 3: Create tenant role
        role_data = await self._create_or_get_tenant_role(tenant_id)

        # Step 4: Assign user to role
        await self._assign_user_to_role(user_data["username"], role_data["id"])

        logger.info(f"Superset setup complete for tenant '{tenant_id}'")

        result = {
            "db_id": db_id,
            "role_id": role_data["id"],
            "username": user_data["username"],
            "db_name": db_name,
        }
        self._setup_cache[tenant_id] = result
        return result


# Singleton instance
_superset_admin: SupersetAdminService | None = None


def get_superset_admin() -> SupersetAdminService:
    global _superset_admin
    if _superset_admin is None:
        _superset_admin = SupersetAdminService()
    return _superset_admin
