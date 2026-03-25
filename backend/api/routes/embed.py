import re
from fastapi import APIRouter, Depends, Header, HTTPException
from models.master import User
from api.deps import get_current_active_user
from config import get_settings
from schemas import SupersetEmbedTokenResponse
from services.superset_admin import get_superset_admin

router = APIRouter(prefix="/api/embed", tags=["Embed"])
settings = get_settings()
_TENANT_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]+$")


def _resolve_tenant_id(
    current_user: User,
    impersonate_tenant: str | None = None,
) -> str | None:
    """SuperAdmin có thể impersonate tenant qua header X-Impersonate-Tenant."""
    if current_user.Role == "SuperAdmin" and impersonate_tenant:
        return impersonate_tenant
    return current_user.TenantId


def _sanitize_tenant_id(tenant_id: str) -> str:
    if not _TENANT_ID_REGEX.match(tenant_id):
        raise HTTPException(status_code=400, detail="Tenant ID không hợp lệ")
    return tenant_id.replace("'", "''")


async def _create_guest_token(tenant_id: str, dashboard_id: int) -> str:
    """Tạo Superset guest token với RLS filter theo TenantId."""
    admin = get_superset_admin()
    token = await admin._admin_login()
    csrf = await admin._get_csrf_token()
    client = await admin._get_client()

    safe_tenant_id = _sanitize_tenant_id(tenant_id)
    guest_url = f"{settings.SUPERSET_URL}/api/v1/security/guest_token/"

    payload = {
        "user": {
            "username": f"tenant_{tenant_id}",
            "first_name": "Tenant",
            "last_name": "User",
        },
        "resources": [{"type": "dashboard", "id": str(dashboard_id)}],
        "rls": [{"clause": f"TenantId = '{safe_tenant_id}'"}],
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


@router.get("/superset-token", response_model=SupersetEmbedTokenResponse)
async def get_superset_guest_token(
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    dashboard_id = settings.SUPERSET_SHARED_DASHBOARD_ID
    token = await _create_guest_token(tenant_id, dashboard_id)

    return {
        "token": token,
        "superset_url": settings.SUPERSET_URL,
        "dashboard_id": dashboard_id,
        "guest": True,
        "mode": "shared_rls",
    }


@router.get("/dashboard/{dashboard_id}")
async def get_dashboard_embed_info(
    dashboard_id: int,
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    """Trả về thông tin embed dashboard shared với RLS theo tenant."""
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    # Luôn dùng shared dashboard ID từ config, bỏ per-tenant dashboard.
    shared_dashboard_id = settings.SUPERSET_SHARED_DASHBOARD_ID

    return {
        "dashboard_id": shared_dashboard_id,
        "superset_url": settings.SUPERSET_URL,
        "guest_token": await _create_guest_token(tenant_id, shared_dashboard_id),
    }
