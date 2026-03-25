import os
import shutil
import pyodbc
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

    # Khởi tạo SQL Server connection
    dwh_conn_str = settings.mssql_conn_str + f"Database={settings.SHARED_DWH_DB};"
    conn = pyodbc.connect(dwh_conn_str)
    cursor = conn.cursor()

    try:
        # 1. Xóa DWH data - KHÔNG commit
        tables_to_clean = [
            "DM_SalesDailySummary", "DM_InventoryAlert",
            "FactSales", "FactInventory", "FactPurchase",
            "DimProduct", "DimCustomer", "DimEmployee",
            "DimSupplier", "DimStore",
        ]
        for tbl in tables_to_clean:
            cursor.execute(f"""
                IF OBJECT_ID('dbo.{tbl}', 'U') IS NOT NULL
                DELETE FROM dbo.{tbl} WHERE TenantId = ?
            """, (tenant_id,))

        # 2. Xóa Postgres records - KHÔNG commit
        db.query(ETLRun).filter(ETLRun.TenantId == tenant_id).delete()
        db.query(User).filter(User.TenantId == tenant_id).delete()
        db.query(Tenant).filter(Tenant.TenantId == tenant_id).delete()

        # 3. CHỐT HẠ: Cả 2 DB đều OK → commit cùng lúc
        conn.commit()
        db.commit()

        # 4. XÓA FILE VẬT LÝ CUỐI CÙNG
        tenant_upload_dir = os.path.join(settings.UPLOAD_DIR, tenant_id)
        if os.path.exists(tenant_upload_dir):
            try:
                shutil.rmtree(tenant_upload_dir)
            except Exception as file_e:
                print(f"Warning: Tenant DB deleted but failed to delete files for {tenant_id}: {file_e}")

        return {"message": f"Đã xóa tenant {tenant_id} và toàn bộ dữ liệu liên quan"}

    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi xóa tenant: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
