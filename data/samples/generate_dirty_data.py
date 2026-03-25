#!/usr/bin/env python3
# ============================================================
# generate_dirty_data.py
# Sinh dữ liệu "bẩn" nhưng có pattern thực tế hơn để test ETL
# Các lỗi có chủ đích:
# - NULL values
# - Duplicate rows
# - Trailing/leading spaces
# - Inconsistent date formats
# - Upper/lower case mixing
# - Missing/invalid FK references
# - Outlier giá trị
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
START_DATE = date(YEAR, 1, 1)
END_DATE = date(YEAR, 12, 31)

# ============================================================
# BASE MASTER DATA (thực tế hơn)
# ============================================================
STORES = [
    {
        "MaCH": "CH001",
        "TenCH": "TechStore Hà Nội",
        "LoaiHinh": "Flagship",
        "DiaChi": "123 Trần Duy Hưng, Cầu Giấy",
        "QuanHuyen": "Cầu Giấy",
        "ThanhPho": "Hà Nội",
        "NgayKhaiTruong": "2020-03-15",
        "QuanLy": "Nguyễn Văn An",
        "DienTich_m2": 250.0,
    },
    {
        "MaCH": "CH002",
        "TenCH": "TechStore Đà Nẵng",
        "LoaiHinh": "Chi nhánh",
        "DiaChi": "45 Lê Duẩn, Hải Châu",
        "QuanHuyen": "Hải Châu",
        "ThanhPho": "Đà Nẵng",
        "NgayKhaiTruong": "2021-06-01",
        "QuanLy": "Trần Thị Bình",
        "DienTich_m2": 180.0,
    },
    {
        "MaCH": "CH003",
        "TenCH": "TechStore TP.HCM",
        "LoaiHinh": "Flagship",
        "DiaChi": "78 Nguyễn Trãi, Quận 1",
        "QuanHuyen": "Quận 1",
        "ThanhPho": "TP.HCM",
        "NgayKhaiTruong": "2019-01-10",
        "QuanLy": "Lê Minh Cường",
        "DienTich_m2": 320.0,
    },
    {
        "MaCH": "CH004",
        "TenCH": "TechStore Cần Thơ",
        "LoaiHinh": "Chi nhánh",
        "DiaChi": "12 Mậu Thân, Ninh Kiều",
        "QuanHuyen": "Ninh Kiều",
        "ThanhPho": "Cần Thơ",
        "NgayKhaiTruong": "2022-04-20",
        "QuanLy": "Phạm Thị Dung",
        "DienTich_m2": 150.0,
    },
    {
        "MaCH": "CH005",
        "TenCH": "TechStore Hải Phòng",
        "LoaiHinh": "Chi nhánh",
        "DiaChi": "34 Lê Lợi, Lê Chân",
        "QuanHuyen": "Lê Chân",
        "ThanhPho": "Hải Phòng",
        "NgayKhaiTruong": "2023-01-15",
        "QuanLy": "Hoàng Văn Đức",
        "DienTich_m2": 140.0,
    },
]

PRODUCTS = [
    # Điện thoại
    ("SP001", "iPhone 15 Pro Max 256GB", 31000000),
    ("SP002", "iPhone 15 128GB", 20500000),
    ("SP003", "Samsung Galaxy S24 Ultra", 28000000),
    ("SP004", "Samsung Galaxy A55", 10500000),
    ("SP005", "Xiaomi 14", 17000000),
    ("SP006", "OPPO Reno11", 12000000),
    # Laptop
    ("SP007", "MacBook Air M3", 31500000),
    ("SP008", "MacBook Pro 14 M3", 45000000),
    ("SP009", "Dell XPS 15", 42000000),
    ("SP010", "ASUS ROG Zephyrus G14", 36000000),
    ("SP011", "Lenovo ThinkPad X1", 38500000),
    ("SP012", "HP EliteBook 840", 29500000),
    # Tablet
    ("SP013", "iPad Pro 11", 25500000),
    ("SP014", "iPad Air", 17500000),
    ("SP015", "Galaxy Tab S9", 18500000),
    # Phụ kiện/tai nghe
    ("SP016", "AirPods Pro 2", 5900000),
    ("SP017", "Sony WH-1000XM5", 7800000),
    ("SP018", "JBL Tune 770NC", 2200000),
    ("SP019", "Anker 65W GaN Charger", 950000),
    ("SP020", "Baseus 20000mAh", 1200000),
]

PAYMENT_METHODS = ["Tiền mặt", "Chuyển khoản", "Quẹt thẻ", "Ví điện tử", "Momo", "VNPay"]
PAYMENT_WEIGHTS = [0.28, 0.21, 0.19, 0.12, 0.11, 0.09]
SALES_CHANNELS = ["InStore", "Online"]
CHANNEL_WEIGHTS = [0.82, 0.18]
CUSTOMER_TYPES = ["Lẻ", "Doanh nghiệp", "VIP"]
CUSTOMER_TYPE_WEIGHTS = [0.72, 0.18, 0.10]

FIRST_NAMES = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Võ", "Đỗ", "Bùi"]
MIDDLE_NAMES = ["Văn", "Thị", "Minh", "Thanh", "Hữu", "Anh", "Gia", "Hoàng"]
LAST_NAMES = ["An", "Bình", "Cường", "Dung", "Hà", "Khanh", "Linh", "Nam", "Phương", "Quang", "Sơn", "Trang"]
DEPARTMENTS = ["Kinh doanh", "Kỹ thuật", "Kho", "Kế toán"]
POSITIONS = ["Nhân viên", "Trưởng ca", "Tư vấn", "Kỹ thuật viên"]


# ============================================================
# Helpers để tạo lỗi bẩn có kiểm soát
# ============================================================
def maybe_spaces(s: str, p: float = 0.15) -> str:
    if random.random() < p:
        return f"  {s}  "
    return s


def maybe_case_mix(s: str, p: float = 0.08) -> str:
    if random.random() < p:
        return s.lower() if random.random() < 0.5 else s.upper()
    return s


def maybe_none(value, p: float):
    return None if random.random() < p else value


def format_date_dirty(dt: date) -> str:
    r = random.random()
    if r < 0.60:
        return dt.strftime("%Y-%m-%d")
    if r < 0.82:
        return dt.strftime("%d/%m/%Y")
    if r < 0.94:
        return dt.strftime("%d-%m-%Y")
    # intentionally odd values for parser robustness
    return random.choice(["N/A", "", "0000-00-00", dt.strftime("%Y/%m/%d")])


def add_duplicates(df: pd.DataFrame, frac: float) -> pd.DataFrame:
    if len(df) == 0 or frac <= 0:
        return df
    n = max(1, int(len(df) * frac))
    dup = df.sample(n=n, replace=True, random_state=seed)
    out = pd.concat([df, dup], ignore_index=True)
    out = out.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return out


# ============================================================
# DIRTY DATA GENERATORS
# ============================================================
def generate_dirty_customers(num_customers: int = 120) -> pd.DataFrame:
    rows = []
    for i in range(1, num_customers + 1):
        full_name = f"{random.choice(FIRST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(LAST_NAMES)}"
        birth = date(random.randint(1972, 2006), random.randint(1, 12), random.randint(1, 28))
        joined = date(random.randint(2020, YEAR), random.randint(1, 12), random.randint(1, 28))
        cust_type = random.choices(CUSTOMER_TYPES, CUSTOMER_TYPE_WEIGHTS, k=1)[0]

        rows.append({
            "MaKH": maybe_case_mix(f"KH{i:03d}", 0.05),
            "HoTen": maybe_spaces(full_name, 0.22),
            "GioiTinh": random.choice(["M", "F", "U", "Nam", "Nữ"]),
            "NgaySinh": maybe_none(format_date_dirty(birth), 0.12),
            "DienThoai": maybe_none(f"09{random.randint(10000000, 99999999)}", 0.10),
            "Email": maybe_none(f"kh{i}@email.com", 0.15),
            "ThanhPho": random.choice(["Hà Nội", "TP.HCM", "Đà Nẵng", "Cần Thơ", "Hải Phòng", "Bình Dương"]),
            "LoaiKH": cust_type,
            "DiemTichLuy": maybe_none(random.randint(0, 8000000 if cust_type == "VIP" else 3000000), 0.08),
            "NgayDangKy": format_date_dirty(joined),
        })

    df = pd.DataFrame(rows)
    df = add_duplicates(df, frac=0.06)

    # thêm vài dòng lỗi đặc biệt
    special = pd.DataFrame([
        {"MaKH": "KH999", "HoTen": "", "GioiTinh": "?", "NgaySinh": "31/02/2025", "DienThoai": "abc", "Email": "not-an-email", "ThanhPho": "", "LoaiKH": "Lẻ", "DiemTichLuy": -100, "NgayDangKy": "N/A"},
        {"MaKH": " kh001 ", "HoTen": "  Trùng mã khách hàng  ", "GioiTinh": "F", "NgaySinh": "1999-01-01", "DienThoai": None, "Email": None, "ThanhPho": "Hà Nội", "LoaiKH": "VIP", "DiemTichLuy": 9999999, "NgayDangKy": "2025/01/01"},
    ])

    return pd.concat([df, special], ignore_index=True)


def generate_dirty_employees(num_employees: int = 55) -> pd.DataFrame:
    rows = []
    store_codes = [s["MaCH"] for s in STORES]

    for i in range(1, num_employees + 1):
        hire_date = date(random.randint(2018, YEAR), random.randint(1, 12), random.randint(1, 28))
        rows.append({
            "MaNV": maybe_spaces(f"NV{i:03d}", 0.18),
            "HoTen": maybe_spaces(f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}", 0.12),
            "PhongBan": maybe_none(random.choice(DEPARTMENTS), 0.08),
            "ChucVu": random.choice(POSITIONS),
            "MaCH": maybe_case_mix(random.choice(store_codes), 0.10),
            "NgayVaoLam": format_date_dirty(hire_date),
        })

    df = pd.DataFrame(rows)
    df = add_duplicates(df, frac=0.05)

    # thêm mã cửa hàng không tồn tại
    df.loc[df.sample(frac=0.03, random_state=seed).index, "MaCH"] = "CH999"
    return df


def generate_dirty_stores() -> pd.DataFrame:
    base = pd.DataFrame(STORES)

    # inject dirty fields
    base.loc[0, "MaCH"] = "  CH001  "
    base.loc[0, "TenCH"] = "TechStore Hà Nội  "
    base.loc[2, "MaCH"] = "CH001"  # duplicate code
    base.loc[2, "TenCH"] = "TechStore Hà Nội"
    base.loc[3, "TenCH"] = ""  # empty name
    base.loc[4, "DiaChi"] = ""  # empty address

    # append extra mixed-case store
    extra = pd.DataFrame([
        {
            "MaCH": "ch006",
            "TenCH": "TechStore Bình Dương",
            "LoaiHinh": "Chi nhánh",
            "DiaChi": "55 Đại lộ Bình Dương",
            "QuanHuyen": "Thủ Dầu Một",
            "ThanhPho": "Bình Dương",
            "NgayKhaiTruong": "2023-06-15",
            "QuanLy": "Võ Thị Lan",
            "DienTich_m2": 120.0,
        }
    ])

    out = pd.concat([base, extra], ignore_index=True)
    out.loc[out.sample(frac=0.10, random_state=seed).index, "NgayKhaiTruong"] = "N/A"
    out.loc[out.sample(frac=0.08, random_state=seed).index, "DienTich_m2"] = None
    return out


def generate_dirty_sales(num_days: int = 120) -> pd.DataFrame:
    rows = []
    store_codes = [s["MaCH"] for s in STORES]
    product_codes = [p[0] for p in PRODUCTS]
    product_price = {p[0]: p[2] for p in PRODUCTS}

    for day_idx in range(num_days):
        current_date = START_DATE + timedelta(days=day_idx)

        # seasonality: cuối năm và cuối tuần bán mạnh hơn
        month_factor = 1.3 if current_date.month in (11, 12) else 1.0
        weekend_factor = 1.2 if current_date.weekday() >= 5 else 1.0
        base_invoices = int(random.randint(25, 55) * month_factor * weekend_factor)

        for inv_no in range(1, base_invoices + 1):
            invoice_id = f"HD{current_date.strftime('%Y%m%d')}{inv_no:04d}"
            num_items = random.choices([1, 2, 3, 4], weights=[0.55, 0.30, 0.12, 0.03], k=1)[0]

            for _ in range(num_items):
                sp = random.choice(product_codes)
                listed_price = product_price[sp]
                qty = random.choices([1, 2, 3, 4, 5], weights=[0.62, 0.23, 0.09, 0.04, 0.02], k=1)[0]

                # giá dao động quanh niêm yết theo campaign
                promo = random.choices([0.00, 0.03, 0.05, 0.10, 0.15], weights=[0.42, 0.22, 0.18, 0.12, 0.06], k=1)[0]
                unit_price = int(round(listed_price * (1 - random.uniform(0, promo)), -3))
                discount_amt = int(round(unit_price * qty * random.uniform(0.0, promo), -3))

                store = random.choice(store_codes)
                # inject missing FK refs
                if random.random() < 0.03:
                    store = f"CH{random.randint(100, 999)}"
                if random.random() < 0.03:
                    sp = f"SP{random.randint(100, 999)}"

                row = {
                    "MaHoaDon": maybe_spaces(invoice_id, 0.04),
                    "MaSP": maybe_case_mix(sp, 0.08),
                    "MaKH": maybe_case_mix(f"KH{random.randint(1, 120):03d}", 0.05),
                    "MaCH": maybe_case_mix(store, 0.08),
                    "MaNV": maybe_case_mix(f"NV{random.randint(1, 55):03d}", 0.06),
                    "NgayBan": format_date_dirty(current_date),
                    "SoLuong": maybe_none(qty, 0.03),
                    "DonGiaBan": maybe_none(unit_price, 0.02),
                    "ChietKhau": maybe_none(discount_amt, 0.05),
                    "ThueSuat": random.choice([0.10, 0.08, 0.05, None]),
                    "PhuongThucTT": maybe_none(random.choices(PAYMENT_METHODS, PAYMENT_WEIGHTS, k=1)[0], 0.07),
                    "KenhBan": random.choices(SALES_CHANNELS, CHANNEL_WEIGHTS, k=1)[0],
                    "IsHoanTra": 1 if random.random() < 0.04 else 0,
                }

                # inject outlier + text noise
                if random.random() < 0.01:
                    row["DonGiaBan"] = random.choice([999, 999999999])
                if random.random() < 0.01:
                    row["SoLuong"] = random.choice([0, -1, 99])

                rows.append(row)

    df = pd.DataFrame(rows)
    df = add_duplicates(df, frac=0.025)
    return df


# ============================================================
# SAVE
# ============================================================
def save_dirty_csv(df: pd.DataFrame, filename: str):
    filepath = OUTPUT_DIR / filename
    df.to_csv(filepath, index=False, encoding="utf-8-sig")
    logger.info(f"Saved DIRTY: {filename} ({len(df)} rows)")


# ============================================================
# MAIN
# ============================================================
def main():
    logger.info("=" * 60)
    logger.info("  DIRTY DATA GENERATION STARTED")
    logger.info("=" * 60)

    customers = generate_dirty_customers()
    sales = generate_dirty_sales()
    employees = generate_dirty_employees()
    stores = generate_dirty_stores()

    save_dirty_csv(customers, "DanhSachKhachHang_Dirty.csv")
    save_dirty_csv(sales, "BaoCaoDoanhThu_Dirty.csv")
    save_dirty_csv(employees, "DanhSachNhanVien_Dirty.csv")
    save_dirty_csv(stores, "DanhSachCuaHang_Dirty.csv")

    logger.info("")
    logger.info("=" * 60)
    logger.info("  DIRTY DATA ISSUES (đã inject):")
    logger.info("  - Leading/trailing spaces (code, tên, hóa đơn)")
    logger.info("  - Duplicate rows (2.5% - 6%)")
    logger.info("  - NULL values (phone, email, qty, price, payment)")
    logger.info("  - Inconsistent date formats + invalid date tokens")
    logger.info("  - Missing FK refs (MaCH/ MaSP không tồn tại)")
    logger.info("  - Case mixing (ch001, sp003, nv010)")
    logger.info("  - Outlier values (giá/ số lượng bất thường)")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
