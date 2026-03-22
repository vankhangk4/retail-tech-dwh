from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.master import Tenant, User
from schemas import TenantCreate, TenantResponse, TenantUpdate
from api.deps import get_db, get_current_superadmin
from core.tenant import create_tenant_database, delete_tenant_database
from core.security import hash_password
from config import get_settings
import pyodbc

router = APIRouter(prefix="/api/admin/tenants", tags=["Tenants"])


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

    # Create database
    db_name = f"DWH_{body.TenantId}"
    success = create_tenant_database(db_name)
    if not success:
        raise HTTPException(status_code=500, detail="Không thể tạo database")

    # Run init SQL scripts in the new database
    _init_tenant_db(db_name)

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

    # Delete database
    delete_tenant_database(tenant.DatabaseName)

    # Delete tenant record
    db.query(User).filter(User.TenantId == tenant_id).delete()
    db.delete(tenant)
    db.commit()
    return {"message": f"Đã xóa tenant {tenant_id}"}


def _init_tenant_db(db_name: str):
    """Khởi tạo schema cho tenant database."""
    settings = get_settings()
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={settings.MSSQL_HOST},{settings.MSSQL_PORT};"
        f"UID={settings.MSSQL_USER};PWD={settings.MSSQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Read and execute init SQL
        import os
        sql_dir = "/app/sql"
        if os.path.exists(sql_dir):
            for folder in ["01_init", "02_staging", "03_system", "04_dim", "05_fact", "06_datamart"]:
                folder_path = os.path.join(sql_dir, folder)
                if os.path.exists(folder_path):
                    for filename in sorted(os.listdir(folder_path)):
                        if filename.endswith(".sql"):
                            filepath = os.path.join(folder_path, filename)
                            with open(filepath, "r", encoding="utf-8") as f:
                                sql = f.read()
                            # Replace USE DWH_RetailTech with new db
                            sql = sql.replace("DWH_RetailTech", db_name)
                            for stmt in sql.split("GO"):
                                stmt = stmt.strip()
                                if stmt:
                                    try:
                                        cursor.execute(stmt)
                                    except Exception as e:
                                        print(f"SQL error: {e}")
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing tenant DB: {e}")
