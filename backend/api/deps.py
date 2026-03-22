from fastapi import Depends
from sqlalchemy.orm import Session
from core.tenant import get_master_session
from core.security import get_current_active_user
from models.master import User


def get_db():
    with get_master_session() as session:
        yield session


def get_current_admin(current_user: User = Depends(get_current_active_user)):
    if current_user.Role not in ["SuperAdmin", "TenantAdmin"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Yêu cầu quyền Admin")
    return current_user


def get_current_superadmin(current_user: User = Depends(get_current_active_user)):
    if current_user.Role != "SuperAdmin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Yêu cầu quyền SuperAdmin")
    return current_user
