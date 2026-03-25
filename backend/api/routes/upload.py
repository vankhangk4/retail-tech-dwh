import os
import aiofiles
import asyncio
import pyodbc
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from sqlalchemy.orm import Session
from models.master import User, ETLRun
from api.deps import get_db, get_current_active_user
from config import get_settings
from core.tenant import get_master_session
from datetime import datetime

router = APIRouter(prefix="/api/upload", tags=["Upload"])
settings = get_settings()


def _resolve_tenant_id(
    current_user: User,
    impersonate_tenant: str | None = None,
) -> str | None:
    """SuperAdmin có thể impersonate tenant qua header X-Impersonate-Tenant."""
    if current_user.Role == "SuperAdmin" and impersonate_tenant:
        return impersonate_tenant
    return current_user.TenantId


@router.post("")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    # Determine tenant folder
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    tenant_folder = os.path.join(settings.UPLOAD_DIR, tenant_id)
    os.makedirs(tenant_folder, exist_ok=True)

    # Save file
    filepath = os.path.join(tenant_folder, file.filename)
    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {
        "filename": file.filename,
        "size": len(content),
        "uploaded_at": datetime.utcnow().isoformat(),
        "tenant_id": tenant_id,
    }


@router.delete("/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    filepath = os.path.join(settings.UPLOAD_DIR, tenant_id, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File không tồn tại")

    # 1. Xóa file vật lý
    os.remove(filepath)

    # 2. Xóa dữ liệu SQL Server - dùng 1 Connection DUY NHẤT
    dwh_conn_str = settings.mssql_conn_str + f"Database={settings.SHARED_DWH_DB};"
    conn = pyodbc.connect(dwh_conn_str)
    cursor = conn.cursor()
    try:
        # Tắt FK constraints tạm thời để xóa dim table có cross-references
        cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? NOCHECK CONSTRAINT all'")
        # Thứ tự: DM -> Fact (tất cả) -> Dim (tất cả)
        # KHÔNG xóa DimDate (bảng dùng chung toàn hệ thống)
        tables_to_clean = [
            "DM_SalesDailySummary", "DM_InventoryAlert",
            "FactSales", "FactInventory", "FactPurchase",
            "DimProduct", "DimCustomer", "DimStore",
            "DimEmployee", "DimSupplier",
        ]
        for tbl in tables_to_clean:
            cursor.execute(f"""
                IF OBJECT_ID('dbo.{tbl}', 'U') IS NOT NULL
                DELETE FROM dbo.{tbl} WHERE TenantId = ?
            """, (tenant_id,))
        # Bật lại FK constraints
        cursor.execute("EXEC sp_MSforeachtable 'ALTER TABLE ? WITH CHECK CHECK CONSTRAINT all'")
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi xóa dữ liệu DWH: {e}")
    finally:
        cursor.close()
        conn.close()

    # 3. Xóa ETL run records trong PostgreSQL (thực hiện SAU CÙNG)
    with get_master_session() as db:
        db.query(ETLRun).filter(ETLRun.TenantId == tenant_id).delete()
        db.commit()

    return {"message": f"Đã xóa file '{filename}' và toàn bộ dữ liệu liên quan"}


@router.get("")
async def list_files(
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    tenant_folder = os.path.join(settings.UPLOAD_DIR, tenant_id)
    if not os.path.exists(tenant_folder):
        return []

    # Use asyncio.to_thread to avoid blocking the event loop
    def _sync_list():
        files = []
        for f in os.listdir(tenant_folder):
            fp = os.path.join(tenant_folder, f)
            stat = os.stat(fp)
            files.append({
                "filename": f,
                "size": stat.st_size,
                "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "tenant_id": tenant_id,
            })
        return files

    files = await asyncio.to_thread(_sync_list)
    return files
