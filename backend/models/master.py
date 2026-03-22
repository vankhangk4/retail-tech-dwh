from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class Tenant(Base):
    __tablename__ = "Tenants"

    TenantId = Column(String(50), primary_key=True)
    TenantName = Column(String(200), nullable=False)
    DatabaseName = Column(String(100), nullable=False, unique=True)
    Plan = Column(String(20), default="trial")
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)
    UpdatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="tenant")


class User(Base):
    __tablename__ = "Users"

    UserId = Column(Integer, primary_key=True, autoincrement=True)
    TenantId = Column(String(50), ForeignKey("Tenants.TenantId"), nullable=True)  # SuperAdmin has null
    Username = Column(String(100), nullable=False, unique=False)
    Email = Column(String(150), nullable=True)
    PasswordHash = Column(String(255), nullable=False)
    Role = Column(String(20), nullable=False)  # SuperAdmin, TenantAdmin, User
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")


class ETLRun(Base):
    __tablename__ = "ETLRuns"

    RunId = Column(Integer, primary_key=True, autoincrement=True)
    TenantId = Column(String(50), ForeignKey("Tenants.TenantId"), nullable=False)
    TriggeredBy = Column(Integer, ForeignKey("Users.UserId"), nullable=True)
    Status = Column(String(20), default="PENDING")  # PENDING, RUNNING, SUCCESS, FAILED
    RowsProcessed = Column(Integer, default=0)
    ErrorMessage = Column(String(1000), nullable=True)
    StartedAt = Column(DateTime, default=datetime.utcnow)
    CompletedAt = Column(DateTime, nullable=True)
