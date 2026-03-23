from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import sessionmaker
from config import get_settings
import logging
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    logger.addHandler(h)

from core.tenant import get_master_engine, _get_master_sessionlocal

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Token blacklist for logout
_blacklisted_tokens: set = set()
_blacklist_lock = threading.Lock()


def blacklist_token(token: str):
    with _blacklist_lock:
        _blacklisted_tokens.add(token)


def is_token_blacklisted(token: str) -> bool:
    with _blacklist_lock:
        return token in _blacklisted_tokens


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
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã bị thu hồi",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Per-token user cache (avoids DB query on every /auth/me call) ───────────
_user_cache: dict = {}
_cache_lock = threading.Lock()
_CACHE_TTL_SECONDS = 30  # short TTL: valid for a request burst, clears on logout


def _cache_get(token: str):
    with _cache_lock:
        entry = _user_cache.get(token)
        if entry is None:
            return None
        if datetime.utcnow().timestamp() - entry["cached_at"] > _CACHE_TTL_SECONDS:
            del _user_cache[token]
            return None
        return entry["user"]


def _cache_set(token: str, user):
    with _cache_lock:
        _user_cache[token] = {
            "user": user,
            "cached_at": datetime.utcnow().timestamp(),
        }


def _cache_invalidate(token: str):
    """Remove a token from cache (called on logout)."""
    with _cache_lock:
        _user_cache.pop(token, None)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Try cache first — avoids DB hit for every /auth/me request
    cached_user = _cache_get(token)
    if cached_user is not None:
        return cached_user

    payload = decode_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token không hợp lệ")

    engine = get_master_engine()
    SessionLocal = _get_master_sessionlocal()
    db = SessionLocal()

    try:
        from models.master import User
        user = db.query(User).filter(User.UserId == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User không tồn tại")

        # Cache for subsequent requests in this burst
        _cache_set(token, user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi xác thực: {str(e)}")
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
