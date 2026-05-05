-- ============================================================
-- FILE: sql/schema/01_create_tenants.sql
-- Mô tả: Tạo bảng Tenants và AppUsers cho Multi-Tenant
-- ============================================================

-- Bước 1: Tạo bảng Tenants
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Tenants')
BEGIN
    CREATE TABLE Tenants (
        TenantID      VARCHAR(20)  PRIMARY KEY,           -- PK — Mã định danh cửa hàng
        TenantName    NVARCHAR(200) NOT NULL,              -- Tên cửa hàng/chi nhánh
        FilePath      NVARCHAR(500) NULL,                  -- Đường dẫn file Excel/CSV
        IsActive      BIT          NOT NULL DEFAULT 1,      -- Trạng thái hoạt động
        ExpiresAt     DATETIME2    NULL,                     -- Ngày hết hạn — NULL = không hết hạn
        CreatedAt     DATETIME2    NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: Tenants';
END

-- Bước 2: Tạo bảng AppUsers
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AppUsers')
BEGIN
    CREATE TABLE AppUsers (
        UserID        INT IDENTITY(1,1) PRIMARY KEY,       -- PK — Surrogate Key tự tăng
        Username      VARCHAR(100) NOT NULL UNIQUE,         -- Tên đăng nhập — UNIQUE
        PasswordHash  VARCHAR(255) NOT NULL,                -- Mật khẩu hash bcrypt (rounds=12)
        TenantID      VARCHAR(20) NULL,                     -- FK → Tenants — NULL nếu là admin
        Role          VARCHAR(20) NOT NULL DEFAULT 'viewer',
                                                       -- Vai trò: 'admin' hoặc 'viewer'
        IsActive      BIT          NOT NULL DEFAULT 1,      -- Trạng thái tài khoản
        CreatedAt     DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT CHK_Role CHECK (Role IN ('admin', 'viewer', 'superadmin')),
        CONSTRAINT FK_AppUsers_Tenant FOREIGN KEY (TenantID)
            REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: AppUsers';
END

-- Bước 3: Insert dữ liệu mẫu tenant
IF NOT EXISTS (SELECT * FROM Tenants WHERE TenantID = 'STORE_HN')
BEGIN
    INSERT INTO Tenants (TenantID, TenantName, FilePath, IsActive)
    VALUES ('STORE_HN', N'Cửa hàng Hà Nội', './data/STORE_HN/', 1);
END

IF NOT EXISTS (SELECT * FROM Tenants WHERE TenantID = 'STORE_HCM')
BEGIN
    INSERT INTO Tenants (TenantID, TenantName, FilePath, IsActive)
    VALUES ('STORE_HCM', N'Cửa hàng Hồ Chí Minh', './data/STORE_HCM/', 1);
END

-- Bước 4: User mặc định được tạo bởi Python bootstrap_users() khi API start.
-- Đọc từ env: DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS, DEFAULT_ADMIN_ROLE
-- Script này không insert gì — chỉ tạo bảng.
PRINT 'Done: 01_create_tenants.sql';
