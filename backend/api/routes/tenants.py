from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.master import Tenant, User, ETLRun
from schemas import TenantCreate, TenantResponse, TenantUpdate
from api.deps import get_db, get_current_superadmin
from config import get_settings

router = APIRouter(prefix="/api/admin/tenants", tags=["Tenants"])
settings = get_settings()


@router.get("", response_model=list[TenantResponse])
async def list_tenants(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    tenants = db.query(Tenant).all()
    return tenants


@router.post("", response_model=TenantResponse)
async def create_tenant(
    body: TenantCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    # Check if tenant exists
    existing = db.query(Tenant).filter(Tenant.TenantId == body.TenantId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tenant đã tồn tại")

    # Shared database model: no per-tenant DB creation
    db_name = settings.SHARED_DWH_DB

    # Create tenant record
    tenant = Tenant(
        TenantId=body.TenantId,
        TenantName=body.TenantName,
        DatabaseName=db_name,
        Plan=body.Plan,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    print(f"[TENANT] Tenant record created: {body.TenantId}")
    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    tenant = db.query(Tenant).filter(Tenant.TenantId == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant không tồn tại")

    # Shared database model: do not delete physical DB

    # Delete ETL runs for this tenant
    db.query(ETLRun).filter(ETLRun.TenantId == tenant_id).delete()

    # Delete all users in this tenant
    db.query(User).filter(User.TenantId == tenant_id).delete()

    # Delete tenant record
    db.delete(tenant)
    db.commit()
    return {"message": f"Đã xóa tenant {tenant_id}"}
