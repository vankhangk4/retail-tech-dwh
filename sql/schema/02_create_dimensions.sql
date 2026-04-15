-- ============================================================
-- FILE: sql/schema/02_create_dimensions.sql
-- Mô tả: Tạo các bảng Dimension (Star Schema)
-- ============================================================

-- 2.3.1. DimDate — Chiều Thời gian (Shared, pre-populated)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimDate')
BEGIN
    CREATE TABLE DimDate (
        DateKey        INT          PRIMARY KEY,   -- PK — dạng số YYYYMMDD
        FullDate       DATE         NOT NULL,
        DayOfWeek      TINYINT      NOT NULL,
        DayName        VARCHAR(15)  NOT NULL,
        DayOfMonth     TINYINT      NOT NULL,
        WeekOfYear     TINYINT      NOT NULL,
        MonthNumber    TINYINT      NOT NULL,
        MonthName      VARCHAR(15)  NOT NULL,
        Quarter        TINYINT      NOT NULL,
        QuarterName    CHAR(2)      NOT NULL,
        Year           SMALLINT     NOT NULL,
        IsWeekend      BIT          NOT NULL DEFAULT 0,
        IsHoliday      BIT          NOT NULL DEFAULT 0,
        HolidayName    NVARCHAR(100) NULL,
        FiscalYear     SMALLINT     NOT NULL,
        FiscalQuarter  TINYINT      NOT NULL
    );
    PRINT 'Created: DimDate';
END

-- 2.3.2. DimProduct — Chiều Sản phẩm (Shared, SCD Type 2)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimProduct')
BEGIN
    CREATE TABLE DimProduct (
        ProductKey       INT IDENTITY(1,1) PRIMARY KEY,
        ProductCode      VARCHAR(50)  NOT NULL,          -- Business Key
        ProductName      NVARCHAR(255) NOT NULL,
        Brand            NVARCHAR(100) NOT NULL,
        CategoryName     NVARCHAR(100) NOT NULL,
        SubCategory      NVARCHAR(100) NULL,
        UnitCostPrice    DECIMAL(18,2) NOT NULL,         -- Giá vốn
        UnitListPrice    DECIMAL(18,2) NOT NULL,         -- Giá niêm yết
        UnitOfMeasure    VARCHAR(20)   NOT NULL DEFAULT N'cái',
        Warranty_Months  TINYINT      NULL,
        IsActive         BIT          NOT NULL DEFAULT 1,
        EffectiveDate    DATE         NOT NULL,           -- SCD Type 2
        ExpirationDate   DATE         NULL,               -- NULL = bản ghi hiện tại
        IsCurrent        BIT          NOT NULL DEFAULT 1
    );
    PRINT 'Created: DimProduct';
END

-- 2.3.3. DimCustomer — Chiều Khách hàng (Có TenantID, SCD Type 2)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimCustomer')
BEGIN
    CREATE TABLE DimCustomer (
        CustomerKey     INT IDENTITY(1,1) PRIMARY KEY,
        CustomerCode   VARCHAR(50)   NOT NULL,           -- Business Key
        TenantID       VARCHAR(20)   NOT NULL,           -- FK → Tenants [MỚI]
        FullName       NVARCHAR(150) NOT NULL,
        Gender         CHAR(1)       NULL,
        DateOfBirth    DATE          NULL,
        AgeGroup       VARCHAR(20)  NULL,
        Phone          VARCHAR(20)   NULL,
        Email          VARCHAR(150)  NULL,
        City           NVARCHAR(100) NULL,
        Province       NVARCHAR(100) NULL,
        CustomerType   VARCHAR(20)  NOT NULL DEFAULT N'Lẻ',
        LoyaltyPoint   INT           NOT NULL DEFAULT 0,
        MemberSince    DATE          NOT NULL,
        EffectiveDate  DATE          NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        ExpirationDate DATE          NULL,
        IsCurrent      BIT          NOT NULL DEFAULT 1,
        IsActive       BIT          NOT NULL DEFAULT 1,
        CONSTRAINT FK_DimCustomer_Tenant FOREIGN KEY (TenantID)
            REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: DimCustomer';
END

-- 2.3.4. DimStore — Chiều Cửa hàng (Có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimStore')
BEGIN
    CREATE TABLE DimStore (
        StoreKey       INT IDENTITY(1,1) PRIMARY KEY,
        StoreCode      VARCHAR(20)   NOT NULL UNIQUE,    -- Business Key
        TenantID       VARCHAR(20)   NOT NULL,           -- FK → Tenants [MỚI]
        StoreName      NVARCHAR(150) NOT NULL,
        StoreType      VARCHAR(50)   NOT NULL,           -- Flagship, Chi nhánh, Online
        Address        NVARCHAR(255) NOT NULL,
        District       NVARCHAR(100) NOT NULL,
        City           NVARCHAR(100) NOT NULL,
        OpenDate       DATE          NOT NULL,
        ManagerName    NVARCHAR(150) NULL,
        StoreArea_m2   DECIMAL(8,2)  NULL,
        IsActive       BIT          NOT NULL DEFAULT 1,
        CONSTRAINT FK_DimStore_Tenant FOREIGN KEY (TenantID)
            REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: DimStore';
END

-- 2.3.5. DimEmployee — Chiều Nhân viên (Có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimEmployee')
BEGIN
    CREATE TABLE DimEmployee (
        EmployeeKey    INT IDENTITY(1,1) PRIMARY KEY,
        EmployeeCode   VARCHAR(20)   NOT NULL,           -- Business Key
        TenantID       VARCHAR(20)   NOT NULL,           -- FK → Tenants [MỚI]
        FullName       NVARCHAR(150) NOT NULL,
        Department     NVARCHAR(100) NOT NULL,
        Position       NVARCHAR(100) NOT NULL,
        StoreKey       INT           NOT NULL,           -- FK → DimStore
        HireDate       DATE          NOT NULL,
        IsActive       BIT          NOT NULL DEFAULT 1,
        CONSTRAINT FK_DimEmployee_Tenant FOREIGN KEY (TenantID)
            REFERENCES Tenants(TenantID),
        CONSTRAINT FK_DimEmployee_Store FOREIGN KEY (StoreKey)
            REFERENCES DimStore(StoreKey)
    );
    PRINT 'Created: DimEmployee';
END

-- 2.3.6. DimSupplier — Chiều Nhà cung cấp (Shared)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimSupplier')
BEGIN
    CREATE TABLE DimSupplier (
        SupplierKey       INT IDENTITY(1,1) PRIMARY KEY,
        SupplierCode      VARCHAR(50)  NOT NULL UNIQUE,  -- Business Key
        SupplierName      NVARCHAR(200) NOT NULL,
        Country           NVARCHAR(100) NOT NULL,
        ContactPerson     NVARCHAR(150) NULL,
        Phone             VARCHAR(30)   NULL,
        Email             VARCHAR(150)  NULL,
        PaymentTerm_Days  TINYINT       NULL,
        IsActive          BIT          NOT NULL DEFAULT 1
    );
    PRINT 'Created: DimSupplier';
END

-- 2.3.7. DimPaymentMethod — Chiều Phương thức thanh toán (Shared)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimPaymentMethod')
BEGIN
    CREATE TABLE DimPaymentMethod (
        PaymentMethodKey INT IDENTITY(1,1) PRIMARY KEY,
        PaymentMethodCode VARCHAR(30) NOT NULL UNIQUE,
        PaymentMethodName NVARCHAR(100) NOT NULL,
        IsActive          BIT NOT NULL DEFAULT 1
    );
    PRINT 'Created: DimPaymentMethod';

    -- Insert default payment methods
    INSERT INTO DimPaymentMethod (PaymentMethodCode, PaymentMethodName)
    VALUES
        ('CASH',      N'Tiền mặt'),
        ('TRANSFER',  N'Chuyển khoản'),
        ('CREDIT',    N'Tín dụng'),
        ('EWALLET',   N'Ví điện tử');
END

-- Insert sample store data
IF NOT EXISTS (SELECT * FROM DimStore WHERE StoreCode = 'STORE_HN')
BEGIN
    INSERT INTO DimStore (StoreCode, TenantID, StoreName, StoreType, Address, District, City, OpenDate, ManagerName)
    VALUES ('STORE_HN', 'STORE_HN', N'Cửa hàng Hà Nội', 'Flagship', N'123 Đường Láng, Đống Đa', N'Đống Đa', N'Hà Nội', '2020-01-15', N'Nguyễn Văn A');
END

IF NOT EXISTS (SELECT * FROM DimStore WHERE StoreCode = 'STORE_HCM')
BEGIN
    INSERT INTO DimStore (StoreCode, TenantID, StoreName, StoreType, Address, District, City, OpenDate, ManagerName)
    VALUES ('STORE_HCM', 'STORE_HCM', N'Cửa hàng Hồ Chí Minh', 'Chi nhánh', N'456 Đường CMT8, Q3', N'Quận 3', N'Hồ Chí Minh', '2021-06-01', N'Trần Thị B');
END

PRINT 'Done: 02_create_dimensions.sql';
