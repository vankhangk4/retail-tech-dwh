#!/usr/bin/env python3
# ============================================================
# generate_dirty_data.py
# Sinh dữ liệu "bẩn" - chưa làm sạch - để test ETL
# Các lỗi có trong dữ liệu:
# - NULL values
# - Duplicate rows
# - Trailing/leading spaces
# - Inconsistent date formats
# - Upper/lower case mixing
# - Special characters
# - Missing foreign key references
# ============================================================
import argparse
import logging
import random
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dirty_data")

# Seed
parser = argparse.ArgumentParser()
parser.add_argument("--seed", type=int, default=None)
parser.add_argument("--fresh", action="store_true")
args = parser.parse_args()

seed = int(time.time()) if args.fresh or args.seed is None else args.seed
random.seed(seed)
np.random.seed(seed)
print(f"[dirty_data] Using seed: {seed}")

OUTPUT_DIR = Path(__file__).parent
OUTPUT_DIR.mkdir(exist_ok=True)

YEAR = 2025

# ============================================================
# DIRTY: Stores - có spaces thừa, duplicate
# ============================================================
STORES = [
    {"MaCH": "  CH001  ", "TenCH": "TechStore Hà Nội  ", "LoaiHinh": "Flagship", "DiaChi": "123 Trần Duy Hưng, Cầu Giấy", "QuanHuyen": "Cầu Giấy", "ThanhPho": "Hà Nội", "NgayKhaiTruong": "2020-03-15", "QuanLy": "Nguyễn Văn An", "DienTich_m2": 250.0},
    {"MaCH": "CH002", "TenCH": "TechStore Đà Nẵng", "LoaiHinh": "Chi nhánh", "DiaChi": "45 Lê Duẩn, Hải Châu", "QuanHuyen": "Hải Châu", "ThanhPho": "Đà Nẵng", "NgayKhaiTruong": "2021-06-01", "QuanLy": "Trần Thị Bình", "DienTich_m2": 180.0},
    {"MaCH": "CH001", "TenCH": "TechStore Hà Nội", "LoaiHinh": "Flagship", "DiaChi": "123 Trần Duy Hưng, Cầu Giấy", "QuanHuyen": "Cầu Giấy", "ThanhPho": "Hà Nội", "NgayKhaiTruong": "2020-03-15", "QuanLy": "Nguyễn Văn An", "DienTich_m2": 250.0},
    {"MaCH": "CH003", "TenCH": "", "LoaiHinh": "Flagship", "DiaChi": "78 Nguyễn Trãi, Q.1", "QuanHuyen": "Quận 1", "ThanhPho": "TP.HCM", "NgayKhaiTruong": "2019-01-10", "QuanLy": "Lê Minh Cường", "DienTich_m2": 320.0},
    {"MaCH": "CH004", "TenCH": "TechStore Cần Thơ", "LoaiHinh": "Chi nhánh", "DiaChi": "", "QuanHuyen": "Ninh Kiều", "ThanhPho": "Cần Thơ", "NgayKhaiTruong": "2022-04-20", "QuanLy": "Phạm Thị Dung", "DienTich_m2": 150.0},
    {"MaCH": "CH005", "TenCH": "TechStore Hải Phòng", "LoaiHinh": "Chi nhánh", "DiaChi": "34 Lê Lợi, Lê Chân", "QuanHuyen": "Lê Chân", "ThanhPho": "Hải Phòng", "NgayKhaiTruong": "N/A", "QuanLy": "Hoàng Văn Đức", "DienTich_m2": None},
    {"MaCH": "ch006", "TenCH": "TechStore Bình Dương", "LoaiHinh": "Chi nhánh", "DiaChi": "55 Đại lộ Bình Dương", "QuanHuyen": "Thủ Dầu Một", "ThanhPho": "Bình Dương", "NgayKhaiTruong": "2023-06-15", "QuanLy": "Võ Thị Lan", "DienTich_m2": 120.0},
]

PAYMENT_METHODS = ["Tiền mặt", "Chuyển khoản", "Quẹt thẻ", "Ví điện tử", "Momo", "VNPay"]
SALES_CHANNELS = ["InStore", "InStore", "InStore", "InStore", "Online"]
CITIES = ["Hà Nội", "TP.HCM", "Đà Nẵng", "Cần Thơ", "Hải Phòng"]
CUSTOMER_TYPES = ["Lẻ", "Lẻ", "Lẻ", "Doanh nghiệp", "VIP"]
GENDERS = ["M", "F", "U"]


def generate_dirty_customers():
    records = []
    for i in range(35):
        fn = random.choice(["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"])
        ln = random.choice(["An", "Bình", "Cường", "Dung", "Minh"])

        phone = None if random.random() < 0.1 else f"09{random.randint(10000000, 99999999)}"
        email = None if random.random() < 0.15 else f"kh{i+1}@email.com"
        dob = None if random.random() < 0.2 else f"{random.randint(1980,2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        if random.random() < 0.3:
            join_date = f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(2020,2025)}"
        else:
            join_date = f"{random.randint(2020,2025)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        records.append({
            "MaKH": f"KH{i+1:03d}",
            "HoTen": f"  {fn} {ln}  " if random.random() < 0.3 else f"{fn} {ln}",
            "GioiTinh": random.choice(GENDERS + ["Nam", "Nữ"]),
            "NgaySinh": dob,
            "DienThoai": phone,
            "Email": email,
            "ThanhPho": random.choice(CITIES),
            "LoaiKH": random.choice(CUSTOMER_TYPES),
            "DiemTichLuy": random.randint(0, 5000000) if random.random() > 0.1 else None,
            "NgayDangKy": join_date,
        })
    return pd.DataFrame(records)


def generate_dirty_sales():
    records = []
    num_days = 60
    start_date = date(YEAR, 1, 1)

    for day_offset in range(num_days):
        current_date = start_date + timedelta(days=day_offset)
        num_invoices = random.randint(10, 30)

        for inv_num in range(num_invoices):
            inv_id = f"HD{current_date.strftime('%Y%m%d')}{inv_num+1:04d}"

            if random.random() < 0.05:
                store_code = f"CH{random.randint(100, 999)}"
            else:
                store_code = f"CH00{random.randint(1,5)}"

            if random.random() < 0.05:
                product_code = f"SP{random.randint(100, 999)}"
            else:
                product_code = f"SP{random.randint(1,20):03d}"

            if random.random() < 0.2:
                sale_date = f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{current_date.year}"
            elif random.random() < 0.1:
                sale_date = current_date.strftime("%d-%m-%Y")
            else:
                sale_date = current_date.strftime("%Y-%m-%d")

            qty = None if random.random() < 0.03 else random.randint(1, 5)
            discount = 0 if random.random() < 0.1 else random.randint(0, 500000)
            payment = None if random.random() < 0.08 else random.choice(PAYMENT_METHODS)

            records.append({
                "MaHoaDon": inv_id,
                "MaSP": product_code,
                "MaKH": f"KH{random.randint(1, 30):03d}",
                "MaCH": store_code,
                "MaNV": f"NV{random.randint(1, 20):03d}",
                "NgayBan": sale_date,
                "SoLuong": qty,
                "DonGiaBan": random.randint(500000, 30000000),
                "ChietKhau": discount,
                "ThueSuat": random.choice([0.10, 0.08, None]),
                "PhuongThucTT": payment,
                "KenhBan": random.choice(SALES_CHANNELS),
                "IsHoanTra": random.randint(0, 1) if random.random() > 0.9 else 0,
            })
    return pd.DataFrame(records)


def generate_dirty_employees():
    records = []
    first_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng"]
    last_names = ["An", "Bình", "Cường", "Dung", "Hùng"]

    for i in range(22):
        fn = random.choice(first_names)
        ln = random.choice(last_names)

        dept = None if random.random() < 0.1 else random.choice(["Kinh doanh", "Kỹ thuật", "Kế toán"])
        pos = random.choice(["Nhân viên", "Trưởng ca", "Kỹ thuật"])

        if random.random() < 0.2:
            hire = f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(2019,2025)}"
        else:
            hire = f"{random.randint(2019,2025)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"

        records.append({
            "MaNV": f"  NV{i+1:03d}  " if random.random() < 0.2 else f"NV{i+1:03d}",
            "HoTen": f"{fn} {ln}",
            "PhongBan": dept,
            "ChucVu": pos,
            "MaCH": f"CH00{random.randint(1,5)}",
            "NgayVaoLam": hire,
        })
    return pd.DataFrame(records)


def save_dirty_csv(df, filename):
    filepath = OUTPUT_DIR / filename
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    logger.info(f"Saved DIRTY: {filename} ({len(df)} rows)")


def main():
    logger.info("=" * 60)
    logger.info("  DIRTY DATA GENERATION STARTED")
    logger.info("=" * 60)

    customers = generate_dirty_customers()
    sales = generate_dirty_sales()
    employees = generate_dirty_employees()
    stores = pd.DataFrame(STORES)

    save_dirty_csv(customers, "DanhSachKhachHang_Dirty.csv")
    save_dirty_csv(sales, "BaoCaoDoanhThu_Dirty.csv")
    save_dirty_csv(employees, "DanhSachNhanVien_Dirty.csv")
    save_dirty_csv(stores, "DanhSachCuaHang_Dirty.csv")

    logger.info("")
    logger.info("=" * 60)
    logger.info("  DIRTY DATA ISSUES:")
    logger.info("  - Trailing/leading spaces in codes and names")
    logger.info("  - Duplicate rows (CH001, KH001-035, NV001-022)")
    logger.info("  - NULL values in phone, email, DOB, qty, discount")
    logger.info("  - Inconsistent date formats (YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY)")
    logger.info("  - Missing FK references (MaCH=CH100, MaSP=SP500)")
    logger.info("  - Inconsistent case (ch006 vs CH006)")
    logger.info("  - Empty string values")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
