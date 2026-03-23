from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.master import Tenant, User, ETLRun
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

    # Delete database first
    delete_tenant_database(tenant.DatabaseName)

    # Delete ETL runs for this tenant
    db.query(ETLRun).filter(ETLRun.TenantId == tenant_id).delete()

    # Delete all users in this tenant
    db.query(User).filter(User.TenantId == tenant_id).delete()

    # Delete tenant record
    db.delete(tenant)
    db.commit()
    return {"message": f"Đã xóa tenant {tenant_id}"}


def _run_sql_script(cursor, sql_text: str):
    """Split by GO and execute each batch."""
    # Remove USE statements (already connected to target DB)
    lines = []
    for line in sql_text.split('\n'):
        stripped = line.strip()
        if stripped.upper().startswith('USE ') or stripped.upper().startswith('GO'):
            continue
        lines.append(line)
    cleaned = '\n'.join(lines)
    # Split by GO and execute
    for batch in cleaned.split('GO'):
        batch = batch.strip()
        if batch:
            try:
                cursor.execute(batch)
            except Exception as e:
                print(f"SQL error: {e}")


def _init_tenant_db(db_name: str):
    """Khởi tạo schema cho tenant database."""
    import os
    settings = get_settings()

    # Connect to master DB to create new database
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={settings.MSSQL_HOST},{settings.MSSQL_PORT};"
        f"UID={settings.MSSQL_USER};PWD={settings.MSSQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str, autocommit=True)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE [{db_name}]")
        cursor.close()
        conn.close()

        # Reconnect to the new database
        conn_str_new = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={settings.MSSQL_HOST},{settings.MSSQL_PORT};"
            f"DATABASE={db_name};"
            f"UID={settings.MSSQL_USER};PWD={settings.MSSQL_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str_new, autocommit=True)
        cursor = conn.cursor()

        sql_dir = "/app/sql"
        if os.path.exists(sql_dir):
            for folder in ["01_init", "02_staging", "03_system", "04_dim", "05_fact", "06_datamart"]:
                folder_path = os.path.join(sql_dir, folder)
                if os.path.exists(folder_path):
                    for filename in sorted(os.listdir(folder_path)):
                        if filename.endswith(".sql"):
                            filepath = os.path.join(folder_path, filename)
                            with open(filepath, "r", encoding="utf-8") as f:
                                sql_text = f.read()
                            _run_sql_script(cursor, sql_text)

        cursor.close()
        conn.close()
        print(f"Tenant DB [{db_name}] initialized successfully")
    except Exception as e:
        print(f"Error initializing tenant DB: {e}")
