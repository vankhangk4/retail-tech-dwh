-- ============================================================
-- Script: 02_staging/stg_tables.sql
-- Mục đích: Tạo 7 bảng Staging (STG_*) - phản chiếu nguồn
-- Thứ tự chạy: 2
-- ============================================================
USE DWH_RetailTech;
GO

-- ============================================================
-- STG_SalesRaw: Bán hàng (từ Excel POS)
-- ============================================================
IF OBJECT_ID('dbo.STG_SalesRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_SalesRaw;
CREATE TABLE dbo.STG_SalesRaw (
    STG_SalesID       BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaHoaDon          VARCHAR(50)     NOT NULL,
    MaSP              VARCHAR(50)     NOT NULL,
    MaKH              VARCHAR(50)     NULL,
    MaCH              VARCHAR(20)    NOT NULL,
    MaNV              VARCHAR(20)    NULL,
    NgayBan           DATE           NOT NULL,
    SoLuong           INT            NOT NULL,
    DonGiaBan         DECIMAL(18,2)  NOT NULL,
    ChietKhau         DECIMAL(18,2)  NULL DEFAULT 0,
    ThueSuat          DECIMAL(5,4)   NULL DEFAULT 0.10,
    PhuongThucTT      VARCHAR(30)    NULL,
    KenhBan           VARCHAR(20)    NULL DEFAULT 'InStore',
    IsHoanTra         BIT            NULL DEFAULT 0,
    LoadDatetime      DATETIME2      NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_SalesRaw_NgayBan ON dbo.STG_SalesRaw(NgayBan);
CREATE INDEX IX_STG_SalesRaw_MaHoaDon ON dbo.STG_SalesRaw(MaHoaDon);
GO

-- ============================================================
-- STG_InventoryRaw: Tồn kho (từ Excel Kho/Google Sheets)
-- ============================================================
IF OBJECT_ID('dbo.STG_InventoryRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_InventoryRaw;
CREATE TABLE dbo.STG_InventoryRaw (
    STG_InventoryID   BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaPhieu            VARCHAR(50)     NOT NULL,
    MaSP               VARCHAR(50)     NOT NULL,
    MaCH               VARCHAR(20)     NOT NULL,
    MaNCC              VARCHAR(50)    NULL,
    NgayChot           DATE           NOT NULL,
    TonDauNgay         INT            NOT NULL DEFAULT 0,
    TonCuoiNgay        INT            NOT NULL DEFAULT 0,
    NhapTrongNgay      INT            NOT NULL DEFAULT 0,
    XuatTrongNgay      INT            NOT NULL DEFAULT 0,
    LoadDatetime       DATETIME2      NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_InventoryRaw_NgayChot ON dbo.STG_InventoryRaw(NgayChot);
GO

-- ============================================================
-- STG_ProductRaw: Danh mục sản phẩm (từ CSV)
-- ============================================================
IF OBJECT_ID('dbo.STG_ProductRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_ProductRaw;
CREATE TABLE dbo.STG_ProductRaw (
    STG_ProductID      BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaSP               VARCHAR(50)     NOT NULL,
    TenSP              NVARCHAR(255)   NOT NULL,
    ThuongHieu         NVARCHAR(100)   NOT NULL,
    DanhMuc            NVARCHAR(100)   NOT NULL,
    DanhMucCon         NVARCHAR(100)   NULL,
    GiaVon             DECIMAL(18,2)   NOT NULL,
    GiaNiemYet         DECIMAL(18,2)   NOT NULL,
    DonViTinh          VARCHAR(20)     NOT NULL DEFAULT N'cái',
    BaoHanh_Thang      TINYINT         NULL,
    LoadDatetime       DATETIME2       NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_ProductRaw_MaSP ON dbo.STG_ProductRaw(MaSP);
GO

-- ============================================================
-- STG_CustomerRaw: Khách hàng (từ Excel/CSV)
-- ============================================================
IF OBJECT_ID('dbo.STG_CustomerRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_CustomerRaw;
CREATE TABLE dbo.STG_CustomerRaw (
    STG_CustomerID     BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaKH               VARCHAR(50)     NOT NULL,
    HoTen              NVARCHAR(150)   NOT NULL,
    GioiTinh           CHAR(1)         NULL,
    NgaySinh           DATE            NULL,
    DienThoai          VARCHAR(20)     NULL,
    Email              VARCHAR(150)    NULL,
    ThanhPho           NVARCHAR(100)   NULL,
    LoaiKH             VARCHAR(20)     NULL DEFAULT N'Lẻ',
    DiemTichLuy        INT             NULL DEFAULT 0,
    NgayDangKy         DATE            NULL,
    LoadDatetime       DATETIME2       NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_CustomerRaw_MaKH ON dbo.STG_CustomerRaw(MaKH);
GO

-- ============================================================
-- STG_StoreRaw: Cửa hàng (từ Excel/CSV)
-- ============================================================
IF OBJECT_ID('dbo.STG_StoreRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_StoreRaw;
CREATE TABLE dbo.STG_StoreRaw (
    STG_StoreID        BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaCH               VARCHAR(20)      NOT NULL,
    TenCH              NVARCHAR(150)    NOT NULL,
    LoaiHinh           VARCHAR(50)      NOT NULL,
    DiaChi             NVARCHAR(255)    NOT NULL,
    QuanHuyen          NVARCHAR(100)    NULL,
    ThanhPho           NVARCHAR(100)    NOT NULL,
    NgayKhaiTruong     DATE            NOT NULL,
    QuanLy             NVARCHAR(150)    NULL,
    DienTich_m2        DECIMAL(8,2)     NULL,
    LoadDatetime       DATETIME2        NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_StoreRaw_MaCH ON dbo.STG_StoreRaw(MaCH);
GO

-- ============================================================
-- STG_EmployeeRaw: Nhân viên (từ Excel/CSV)
-- ============================================================
IF OBJECT_ID('dbo.STG_EmployeeRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_EmployeeRaw;
CREATE TABLE dbo.STG_EmployeeRaw (
    STG_EmployeeID     BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaNV               VARCHAR(20)     NOT NULL,
    HoTen              NVARCHAR(150)   NOT NULL,
    PhongBan           NVARCHAR(100)   NOT NULL,
    ChucVu             NVARCHAR(100)   NOT NULL,
    MaCH               VARCHAR(20)    NOT NULL,
    NgayVaoLam         DATE           NOT NULL,
    LoadDatetime       DATETIME2      NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_EmployeeRaw_MaNV ON dbo.STG_EmployeeRaw(MaNV);
GO

-- ============================================================
-- STG_SupplierRaw: Nhà cung cấp (từ Excel/CSV)
-- ============================================================
IF OBJECT_ID('dbo.STG_SupplierRaw', 'U') IS NOT NULL DROP TABLE dbo.STG_SupplierRaw;
CREATE TABLE dbo.STG_SupplierRaw (
    STG_SupplierID     BIGINT IDENTITY(1,1) PRIMARY KEY,
    MaNCC              VARCHAR(50)     NOT NULL,
    TenNCC             NVARCHAR(200)   NOT NULL,
    QuocGia            NVARCHAR(100)   NOT NULL,
    NguoiLienHe        NVARCHAR(150)   NULL,
    DienThoai          VARCHAR(30)     NULL,
    Email              VARCHAR(150)    NULL,
    DieuKhoanTT_Ngay   TINYINT         NULL,
    LoadDatetime       DATETIME2       NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_STG_SupplierRaw_MaNCC ON dbo.STG_SupplierRaw(MaNCC);
GO

PRINT 'All STG_* staging tables created successfully.';
GO
