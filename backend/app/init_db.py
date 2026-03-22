#!/usr/bin/env python3
"""
Khởi tạo master database (DWH_Master) - chạy khi backend start.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.master import Base, Tenant, User, ETLRun
from models.database import get_master_engine
from core.security import hash_password
from core.tenant import get_master_session
from config import get_settings

settings = get_settings()


def init_db():
    """Tạo tables trong master DB."""
    engine = get_master_engine()
    Base.metadata.create_all(bind=engine)
    print("Master database tables created successfully.")


def init_superadmin():
    """Tạo SuperAdmin đầu tiên nếu chưa có."""
    admin_password = settings.DEFAULT_ADMIN_PASSWORD
    if not admin_password:
        print("DEFAULT_ADMIN_PASSWORD not set in env, skipping SuperAdmin creation.")
        return

    with get_master_session() as db:
        existing = db.query(User).filter(User.Username == "admin").first()
        if existing:
            print(f"SuperAdmin 'admin' đã tồn tại (UserId={existing.UserId})")
            return

        user = User(
            Username="admin",
            Email="admin@system.local",
            PasswordHash=hash_password(admin_password),
            Role="SuperAdmin",
            TenantId=None,
            IsActive=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Tạo SuperAdmin thành công! UserId={user.UserId}")


if __name__ == "__main__":
    init_db()
    init_superadmin()
