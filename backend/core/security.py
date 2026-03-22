from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_settings
from models.database import get_master_engine

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    engine = get_master_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        from models.master import User
        user = db.query(User).filter(User.UserId == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User không tồn tại")
        return user
    finally:
        db.close()


async def get_current_active_user(current_user = Depends(get_current_user)):
    if not current_user.IsActive:
        raise HTTPException(status_code=400, detail="User đã bị vô hiệu hóa")
    return current_user


def require_role(*roles):
    async def role_checker(current_user = Depends(get_current_active_user)):
        if current_user.Role not in roles:
            raise HTTPException(status_code=403, detail="Không có quyền truy cập")
        return current_user
    return role_checker
