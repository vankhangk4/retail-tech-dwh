from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
from core.security import verify_password, create_access_token, get_current_active_user, blacklist_token, oauth2_scheme, _cache_invalidate
from core.tenant import get_master_session
from models.master import User
from schemas import LoginRequest, Token, UserResponse
from api.deps import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_master_session() as db:
        user = db.query(User).filter(User.Username == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản không tồn tại",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, user.PasswordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.IsActive:
            raise HTTPException(status_code=400, detail="Tài khoản đã bị vô hiệu hóa")

        access_token = create_access_token(
            data={
                "sub": str(user.UserId),
                "tenant_id": user.TenantId,
                "role": user.Role,
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
async def login_json(body: LoginRequest):
    with get_master_session() as db:
        user = db.query(User).filter(User.Username == body.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tài khoản không tồn tại",
            )
        if not verify_password(body.password, user.PasswordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai password",
            )
        if not user.IsActive:
            raise HTTPException(status_code=400, detail="Tài khoản đã bị vô hiệu hóa")

        access_token = create_access_token(
            data={
                "sub": str(user.UserId),
                "tenant_id": user.TenantId,
                "role": user.Role,
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklist_token(token)
    _cache_invalidate(token)
    logger.info(f"Token blacklisted and cache invalidated: {token[:20]}...")
    return {"msg": "Đăng xuất thành công"}
