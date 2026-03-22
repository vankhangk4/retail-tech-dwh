import httpx
from fastapi import APIRouter, Depends, HTTPException
from models.master import User
from api.deps import get_db, get_current_active_user
from config import get_settings

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


async def _create_guest_token(tenant_id: str, db_name: str) -> str:
    """Tạo Superset guest token cho tenant."""
    token = await _get_superset_session()
    guest_url = f"{settings.SUPERSET_URL}/api/v1/security/guest_token"

    payload = {
        "user": {
            "username": f"tenant_{tenant_id}",
            "first_name": "Tenant",
            "last_name": "User",
        },
        "resources": [{"type": "database", "id": 1}],
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

    token = await _create_guest_token(tenant_id, f"DWH_{tenant_id}")
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

    return {
        "dashboard_id": dashboard_id,
        "superset_url": settings.SUPERSET_URL,
        "guest_token": await _create_guest_token(tenant_id, f"DWH_{tenant_id}"),
    }
