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
    embedded_dashboard_uuid: Optional[str] = None
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


class UserProfile(BaseModel):
    """Full profile response — trả về từ /me/profile"""
    user_id: int
    username: str
    display_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    avatar_data: Optional[str]
    tenant_id: Optional[str]
    role: str
    is_active: bool
    created_at: Optional[str]


class UpdateProfileRequest(BaseModel):
    """Request cập nhật hồ sơ"""
    display_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)


class ChangePasswordRequest(BaseModel):
    """Request đổi mật khẩu"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class AvatarUploadRequest(BaseModel):
    """Request upload avatar — base64 data URL"""
    avatar_data: str


class LoginHistoryItem(BaseModel):
    """Một bản ghi lịch sử đăng nhập"""
    history_id: int
    login_at: str
    ip_address: Optional[str]
    user_agent: Optional[str]
    status: str
