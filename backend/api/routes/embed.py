import httpx
from fastapi import APIRouter, Depends, HTTPException
from models.master import User
from api.deps import get_db, get_current_active_user
from config import get_settings
from services.superset_admin import get_superset_admin

router = APIRouter(prefix="/api/embed", tags=["Embed"])
settings = get_settings()


async def _create_guest_token(
    tenant_id: str, db_name: str, dashboard_id: int | None = None, db_id: int | None = None
) -> str:
    """Tạo Superset guest token cho tenant với RLS filter.

    Reuses the cached admin token from SupersetAdminService singleton
    to avoid hitting Superset login rate limits.
    """
    admin = get_superset_admin()
    token = await admin._admin_login()
    csrf = await admin._get_csrf_token()
    client = await admin._get_client()

    guest_url = f"{settings.SUPERSET_URL}/api/v1/security/guest_token/"

    resources = []
    if dashboard_id:
        resources.append({"type": "dashboard", "id": str(dashboard_id)})

    payload = {
        "user": {
            "username": f"tenant_{tenant_id}",
            "first_name": "Tenant",
            "last_name": "User",
        },
        "resources": resources,
        "rls": [],
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Referer": settings.SUPERSET_URL,
    }
    if csrf:
        headers["X-CSRFToken"] = csrf

    resp = await client.post(guest_url, headers=headers, json=payload)

    if resp.status_code == 200:
        return resp.json().get("token", "")
    return ""


@router.get("/superset-token")
async def get_superset_guest_token(
    current_user: User = Depends(get_current_active_user),
):
    tenant_id = current_user.TenantId
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    db_name = f"DWH_{tenant_id}"

    # Lazy provision: ensure tenant is set up in Superset on first access
    db_id = None
    dashboard_id = None
    try:
        admin = get_superset_admin()
        result = await admin.ensure_tenant_superset_setup(tenant_id)
        db_id = result.get("db_id")
        dashboard_id = result.get("dashboard_id")
    except Exception:
        pass  # Guest token fallback still works without explicit DB registration

    token = await _create_guest_token(tenant_id, db_name, dashboard_id, db_id)
    return {
        "token": token,
        "superset_url": settings.SUPERSET_URL,
        "dashboard_id": dashboard_id or 1,
        "guest": True,
    }


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard_embed_info(
    dashboard_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Trả về thông tin embed dashboard."""
    tenant_id = current_user.TenantId
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    db_name = f"DWH_{tenant_id}"

    db_id = None
    tenant_dashboard_id = None
    try:
        admin = get_superset_admin()
        result = await admin.ensure_tenant_superset_setup(tenant_id)
        db_id = result.get("db_id")
        tenant_dashboard_id = result.get("dashboard_id")
    except Exception:
        pass

    # Use tenant's dashboard if available, otherwise use requested ID
    final_dashboard_id = tenant_dashboard_id or dashboard_id

    return {
        "dashboard_id": final_dashboard_id,
        "superset_url": settings.SUPERSET_URL,
        "guest_token": await _create_guest_token(tenant_id, db_name, final_dashboard_id, db_id),
    }

