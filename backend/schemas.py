from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ============ AUTH ============
class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    UserId: int
    TenantId: Optional[str]  # SuperAdmin has null
    Username: str
    Email: Optional[str]
    Role: str
    IsActive: bool
    CreatedAt: datetime

    class Config:
        from_attributes = True


# ============ TENANT ============
class TenantCreate(BaseModel):
    TenantId: str
    TenantName: str
    Plan: str = "trial"


class TenantResponse(BaseModel):
    TenantId: str
    TenantName: str
    DatabaseName: Optional[str]
    Plan: str
    IsActive: bool
    CreatedAt: datetime

    class Config:
        from_attributes = True


class TenantUpdate(BaseModel):
    TenantName: Optional[str] = None
    Plan: Optional[str] = None
    IsActive: Optional[bool] = None


# ============ USER ============
class UserCreate(BaseModel):
    Username: str
    Password: str
    Email: Optional[str] = None
    Role: str = "User"
    TenantId: Optional[str] = None


class UserUpdate(BaseModel):
    Username: Optional[str] = None
    Email: Optional[str] = None
    Password: Optional[str] = None
    Role: Optional[str] = None
    IsActive: Optional[bool] = None


# ============ ETL ============
class ETLRunResponse(BaseModel):
    RunId: int
    TenantId: str
    Status: str
    RowsProcessed: int
    ErrorMessage: Optional[str]
    StartedAt: datetime
    CompletedAt: Optional[datetime]

    class Config:
        from_attributes = True


# ============ FILE ============
class FileInfo(BaseModel):
    filename: str
    size: int
    uploaded_at: str
    tenant_id: str


# ============ STATS ============
class StatsResponse(BaseModel):
    total_revenue: float
    total_orders: int
    total_customers: int
    top_products: List[dict]


# ============ EMBED ============
class SupersetEmbedTokenResponse(BaseModel):
    token: str
    superset_url: str
    dashboard_id: int
    guest: bool
    mode: str = "shared_rls"
