#!/usr/bin/env python3
"""
Script khởi tạo SuperAdmin đầu tiên.
Chạy: python -m app.init_superadmin --password MySecret@123
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.security import hash_password, create_access_token
from core.tenant import get_master_session
from models.master import User


def init_superadmin(
    username: str = "admin",
    password: str = "",
    email: str = "admin@system.local",
):
    """Tạo SuperAdmin đầu tiên."""
    if not password:
        print("ERROR: --password is required")
        return

    with get_master_session() as db:
        existing = db.query(User).filter(User.Username == username).first()
        if existing:
            print(f"SuperAdmin '{username}' đã tồn tại (UserId={existing.UserId})")
            return

        user = User(
            Username=username,
            Email=email,
            PasswordHash=hash_password(password),
            Role="SuperAdmin",
            TenantId=None,
            IsActive=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"Tạo SuperAdmin thành công!")
        print(f"  Username: {username}")
        print(f"  Password: {password}")
        print(f"  UserId:   {user.UserId}")
        print(f"  Role:     {user.Role}")
        print(f"\nĐăng nhập tại: POST /api/auth/login")
        print(f"  Body (JSON): {{'username': '{username}', 'password': '{password}'}}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Khởi tạo SuperAdmin")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", required=True)
    parser.add_argument("--email", default="admin@system.local")
    args = parser.parse_args()

    init_superadmin(args.username, args.password, args.email)
