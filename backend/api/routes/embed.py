import httpx
from fastapi import APIRouter, Depends, HTTPException
from models.master import User
from api.deps import get_db, get_current_active_user
from config import get_settings
from services.superset_admin import get_superset_admin

router = APIRouter(prefix="/api/embed", tags=["Embed"])
settings = get_settings()


async def _get_superset_session() -> str:
    """Đăng nhập Superset và lấy CSRF token."""
    login_url = f"{settings.SUPERSET_URL}/api/v1/security/login"
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            login_url,
            json={
                "username": settings.SUPERSET_ADMIN_USER,
                "password": settings.SUPERSET_ADMIN_PASSWORD,
                "provider": "db",
            },
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Không thể đăng nhập Superset")
        data = resp.json()
        return data.get("access_token", "")


async def _create_guest_token(tenant_id: str, db_name: str, db_id: int | None = None) -> str:
    """Tạo Superset guest token cho tenant với RLS filter."""
    token = await _get_superset_session()
    guest_url = f"{settings.SUPERSET_URL}/api/v1/security/guest_token"

    # Use registered database id, or fallback to 1
    resources = [{"type": "database", "id": db_id or 1}]

    payload = {
        "user": {
            "username": f"tenant_{tenant_id}",
            "first_name": "Tenant",
            "last_name": "User",
        },
        "resources": resources,
        "rls": [
            {
                "clause": f"tenant_id = '{tenant_id}'",
            }
        ],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            guest_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

        if resp.status_code == 200:
            return resp.json().get("token", "")
        # Fallback: return empty token, frontend sẽ dùng admin credentials
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
    try:
        admin = get_superset_admin()
        result = await admin.ensure_tenant_superset_setup(tenant_id)
        db_id = result.get("db_id")
    except Exception:
        pass  # Guest token fallback still works without explicit DB registration

    token = await _create_guest_token(tenant_id, db_name, db_id)
    return {
        "token": token,
        "superset_url": settings.SUPERSET_URL,
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
    try:
        admin = get_superset_admin()
        result = await admin.ensure_tenant_superset_setup(tenant_id)
        db_id = result.get("db_id")
    except Exception:
        pass

    return {
        "dashboard_id": dashboard_id,
        "superset_url": settings.SUPERSET_URL,
        "guest_token": await _create_guest_token(tenant_id, db_name, db_id),
    }
