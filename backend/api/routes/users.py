from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.master import User, Tenant
from schemas import UserCreate, UserUpdate, UserResponse
from api.deps import get_db, get_current_admin, get_current_superadmin
from core.security import hash_password, get_current_active_user
from models.master import User as UserModel
from services.superset_admin import get_superset_admin
import asyncio

router = APIRouter(tags=["Users"])


# ===== SuperAdmin: quản lý TẤT CẢ users =====
@router.get("/api/admin/users", response_model=list[UserResponse])
async def list_all_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    users = db.query(User).all()
    return users


@router.post("/api/admin/users", response_model=UserResponse)
async def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    if body.Role == "SuperAdmin" and current_user.Role != "SuperAdmin":
        raise HTTPException(status_code=403, detail="Chỉ SuperAdmin mới tạo được SuperAdmin")

    # Validate tenant
    if body.TenantId:
        tenant = db.query(Tenant).filter(Tenant.TenantId == body.TenantId).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant không tồn tại")
    elif body.Role != "SuperAdmin":
        raise HTTPException(status_code=400, detail="User phải thuộc một tenant")

    user = User(
        Username=body.Username,
        Email=body.Email,
        PasswordHash=hash_password(body.Password),
        Role=body.Role,
        TenantId=body.TenantId,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-setup Superset for tenant users (TenantAdmin/User)
    if body.TenantId and body.Role in ("TenantAdmin", "User"):
        try:
            admin = get_superset_admin()
            await admin.ensure_tenant_superset_setup(body.TenantId)
        except Exception as e:
            import logging
            logging.warning(f"Superset auto-setup failed for tenant {body.TenantId}: {e}")

    return user


@router.put("/api/admin/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    if body.Username is not None:
        user.Username = body.Username
    if body.Email is not None:
        user.Email = body.Email
    if body.Password is not None:
        user.PasswordHash = hash_password(body.Password)
    if body.Role is not None:
        if body.Role == "SuperAdmin" and current_user.Role != "SuperAdmin":
            raise HTTPException(status_code=403, detail="Không thể set SuperAdmin")
        user.Role = body.Role
    if body.IsActive is not None:
        user.IsActive = body.IsActive

    db.commit()
    db.refresh(user)
    return user


@router.delete("/api/admin/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin),
):
    user = db.query(User).filter(User.UserId == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")
    if user.UserId == current_user.UserId:
        raise HTTPException(status_code=400, detail="Không thể xóa chính mình")

    db.delete(user)
    db.commit()
    return {"message": "Đã xóa user"}


# ===== TenantAdmin: quản lý users TRONG tenant =====
@router.get("/api/tenant/users", response_model=list[UserResponse])
async def list_tenant_users(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    users = db.query(User).filter(User.TenantId == current_user.TenantId).all()
    return users


@router.post("/api/tenant/users", response_model=UserResponse)
async def create_tenant_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    if current_user.Role != "TenantAdmin":
        raise HTTPException(status_code=403, detail="Chỉ TenantAdmin mới tạo được user")

    user = User(
        Username=body.Username,
        Email=body.Email,
        PasswordHash=hash_password(body.Password),
        Role="User",  # TenantAdmin chỉ tạo được User
        TenantId=current_user.TenantId,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-setup Superset for tenant (one-time: registers DB/user/role/RLS)
    try:
        admin = get_superset_admin()
        await admin.ensure_tenant_superset_setup(current_user.TenantId)
    except Exception as e:
        import logging
        logging.warning(f"Superset auto-setup failed for tenant {current_user.TenantId}: {e}")

    return user


@router.delete("/api/tenant/users/{user_id}")
async def delete_tenant_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin),
):
    if current_user.Role != "TenantAdmin":
        raise HTTPException(status_code=403, detail="Chỉ TenantAdmin")

    user = db.query(User).filter(
        User.UserId == user_id,
        User.TenantId == current_user.TenantId
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    db.delete(user)
    db.commit()
    return {"message": "Đã xóa user"}
