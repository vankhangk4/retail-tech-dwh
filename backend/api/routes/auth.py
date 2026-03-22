from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.security import verify_password, create_access_token, get_current_active_user
from core.tenant import get_master_session
from models.master import User
from schemas import LoginRequest, Token, UserResponse
from api.deps import get_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_master_session() as db:
        user = db.query(User).filter(User.Username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.PasswordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai username hoặc password",
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
        if not user or not verify_password(body.password, user.PasswordHash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sai username hoặc password",
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
