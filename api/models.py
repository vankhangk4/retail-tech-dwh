# ============================================================
# FILE: api/models.py
# Mô tả: Pydantic models cho Auth Gateway
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Request model cho endpoint /login"""
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Response model cho endpoint /login"""
    access_token: str
    token_type: str = 'bearer'
    expires_in: int = 28800  # 8 giờ


class DashboardTokenRequest(BaseModel):
    """Request model cho endpoint /dashboard-token"""
    pass  # Token được gửi qua Header Authorization Bearer


class DashboardTokenResponse(BaseModel):
    """Response model cho endpoint /dashboard-token"""
    dashboard_url: str
    dashboard_id: int
    guest_token: str
    token_type: str = 'bearer'
    expires_in: int = 3600  # 1 giờ


class UserInfo(BaseModel):
    """Response model cho /me"""
    user_id: int
    username: str
    tenant_id: Optional[str]
    role: str
    is_active: bool


class RegisterRequest(BaseModel):
    """Request model cho endpoint /register"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)
    role: str = Field(default='viewer')
    tenant_id: Optional[str] = None


class TokenPayload(BaseModel):
    """JWT payload model"""
    user_id: int
    username: str
    tenant_id: Optional[str]
    role: str
    exp: int
