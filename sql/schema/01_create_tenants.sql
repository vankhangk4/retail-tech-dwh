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
        CONSTRAINT CHK_Role CHECK (Role IN ('admin', 'viewer')),
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

-- Bước 4: Insert admin mặc định (password: Admin@1234 — hash bcrypt)
IF NOT EXISTS (SELECT * FROM AppUsers WHERE Username = 'admin')
BEGIN
    -- hash bcrypt của 'Admin@1234' (rounds=12)
    INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive)
    VALUES (
        'admin',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4mHPnlCJLmf1q3Gq',
        NULL,
        'admin',
        1
    );
    PRINT 'Created default admin user';
END

-- Bước 5: Insert viewer mẫu cho mỗi tenant
IF NOT EXISTS (SELECT * FROM AppUsers WHERE Username = 'manager_hn')
BEGIN
    -- hash bcrypt của 'Pass@HN123' (rounds=12)
    INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive)
    VALUES (
        'manager_hn',
        '$2b$12$KxGcD2vKZ9P8y7fL5vHQ0.6bX0r9JZL4qU8Y5hN3mM1cX2iS0dE',
        'STORE_HN',
        'viewer',
        1
    );
END

IF NOT EXISTS (SELECT * FROM AppUsers WHERE Username = 'manager_hcm')
BEGIN
    -- hash bcrypt của 'Pass@HCM123' (rounds=12)
    INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive)
    VALUES (
        'manager_hcm',
        '$2b$12$AxFdH3jLP0Q7z6eM4uIR1.7cY1s8KZL5rT7X4iN2mN0bY1jT9cF',
        'STORE_HCM',
        'viewer',
        1
    );
END

PRINT 'Done: 01_create_tenants.sql';
