-- ============================================================
-- FILE: sql/00_init.sql
-- MSSQL Docker init: tạo DB + schema + SPs + views + data
-- ============================================================

SET QUOTED_IDENTIFIER ON;
GO

-- Bước 1: Tạo database (chạy trên master)
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'DWH_MultiTenant')
BEGIN
    CREATE DATABASE DWH_MultiTenant;
    PRINT 'Created database: DWH_MultiTenant';
END
GO

-- Bước 2: Chuyển sang DWH_MultiTenant và tạo schema
USE DWH_MultiTenant;
GO

-- ============================================================
-- SCHEMA: 01_create_tenants.sql
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Tenants')
BEGIN
    CREATE TABLE Tenants (
        TenantID      VARCHAR(20)  PRIMARY KEY,
        TenantName    NVARCHAR(200) NOT NULL,
        FilePath      NVARCHAR(500) NULL,
        IsActive      BIT          NOT NULL DEFAULT 1,
        ExpiresAt     DATETIME2    NULL,
        CreatedAt     DATETIME2    NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: Tenants';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AppUsers')
BEGIN
    CREATE TABLE AppUsers (
        UserID        INT IDENTITY(1,1) PRIMARY KEY,
        Username      VARCHAR(100) NOT NULL UNIQUE,
        PasswordHash  VARCHAR(255) NOT NULL,
        TenantID      VARCHAR(20) NULL,
        Role          VARCHAR(20) NOT NULL DEFAULT 'viewer',
        IsActive      BIT          NOT NULL DEFAULT 1,
        CreatedAt     DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT CHK_AppUsers_Role CHECK (Role IN ('admin', 'viewer', 'superadmin'))
    );
    PRINT 'Created: AppUsers';
END

-- ============================================================
-- TENANTS: STORE_HN, STORE_HCM
-- ============================================================
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
PRINT 'Created: default tenants';

-- ============================================================
-- USER: Default superadmin được tạo bởi Python bootstrap_users()
-- khi API start, đọc từ env: DEFAULT_ADMIN_USER, DEFAULT_ADMIN_PASS, DEFAULT_ADMIN_ROLE
-- Script này không insert gì.
-- ============================================================

-- ============================================================
-- SCHEMA: 02_create_dimensions.sql
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimDate')
BEGIN
    CREATE TABLE DimDate (
        DateKey       INT           PRIMARY KEY,
        FullDate      DATE          NOT NULL,
        Day           TINYINT       NOT NULL,
        Month         TINYINT       NOT NULL,
        Quarter       TINYINT       NOT NULL,
        Year          SMALLINT      NOT NULL,
        MonthName     NVARCHAR(20)  NOT NULL,
        DayOfWeek     TINYINT       NOT NULL,
        WeekOfYear    TINYINT       NOT NULL
    );
    PRINT 'Created: DimDate';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimProduct')
BEGIN
    CREATE TABLE DimProduct (
        ProductKey    INT IDENTITY(1,1) PRIMARY KEY,
        ProductID     VARCHAR(20)   NOT NULL UNIQUE,
        ProductName   NVARCHAR(200) NOT NULL,
        Category      NVARCHAR(100) NULL,
        SubCategory   NVARCHAR(100) NULL,
        UnitPrice     DECIMAL(18,2) NOT NULL,
        SupplierID    VARCHAR(20)   NULL,
        IsActive      BIT           NOT NULL DEFAULT 1,
        TenantID      VARCHAR(20)   NULL
    );
    PRINT 'Created: DimProduct';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimCustomer')
BEGIN
    CREATE TABLE DimCustomer (
        CustomerKey   INT IDENTITY(1,1) PRIMARY KEY,
        CustomerID    VARCHAR(20)   NOT NULL UNIQUE,
        CustomerName  NVARCHAR(200) NOT NULL,
        Phone         VARCHAR(20)   NULL,
        Email         VARCHAR(100)  NULL,
        City          NVARCHAR(100) NULL,
        Region        NVARCHAR(100) NULL,
        CustomerType  VARCHAR(20)   NOT NULL DEFAULT 'Individual',
        TenantID      VARCHAR(20)   NULL,
        CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: DimCustomer';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimStore')
BEGIN
    CREATE TABLE DimStore (
        StoreKey      INT IDENTITY(1,1) PRIMARY KEY,
        TenantID      VARCHAR(20)   NOT NULL,
        StoreName     NVARCHAR(200) NOT NULL,
        Address       NVARCHAR(500) NULL,
        City          NVARCHAR(100) NOT NULL,
        Region        NVARCHAR(100) NOT NULL,
        ManagerName   NVARCHAR(100) NULL,
        OpenDate      DATE          NULL,
        IsActive      BIT           NOT NULL DEFAULT 1,
        CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: DimStore';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimEmployee')
BEGIN
    CREATE TABLE DimEmployee (
        EmployeeKey   INT IDENTITY(1,1) PRIMARY KEY,
        EmployeeID    VARCHAR(20)   NOT NULL UNIQUE,
        EmployeeName  NVARCHAR(200) NOT NULL,
        Position      NVARCHAR(100) NOT NULL,
        Department    NVARCHAR(100) NOT NULL,
        HireDate      DATE          NOT NULL,
        Salary        DECIMAL(18,2) NOT NULL,
        TenantID      VARCHAR(20)   NULL,
        ManagerID     VARCHAR(20)   NULL,
        IsActive      BIT           NOT NULL DEFAULT 1,
        CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: DimEmployee';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimSupplier')
BEGIN
    CREATE TABLE DimSupplier (
        SupplierKey   INT IDENTITY(1,1) PRIMARY KEY,
        SupplierID    VARCHAR(20)   NOT NULL UNIQUE,
        SupplierName  NVARCHAR(200) NOT NULL,
        ContactName   NVARCHAR(100) NULL,
        Phone         VARCHAR(20)   NULL,
        Email         VARCHAR(100)  NULL,
        City          NVARCHAR(100) NULL,
        IsActive      BIT           NOT NULL DEFAULT 1,
        CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: DimSupplier';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DimPaymentMethod')
BEGIN
    CREATE TABLE DimPaymentMethod (
        PaymentMethodKey INT IDENTITY(1,1) PRIMARY KEY,
        PaymentMethodID   VARCHAR(20)   NOT NULL UNIQUE,
        PaymentMethodName NVARCHAR(100) NOT NULL,
        IsActive          BIT           NOT NULL DEFAULT 1
    );
    INSERT INTO DimPaymentMethod (PaymentMethodID, PaymentMethodName) VALUES
        ('CASH',     'Cash'),
        ('CARD',     'Credit/Debit Card'),
        ('TRANSFER', 'Bank Transfer'),
        ('EWALLET',  'E-Wallet');
    PRINT 'Created: DimPaymentMethod';
END

-- ============================================================
-- SCHEMA: 03_create_facts.sql
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactSales')
BEGIN
    CREATE TABLE FactSales (
        SalesKey      BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID      VARCHAR(20)   NOT NULL,
        SaleDate      DATE          NOT NULL,
        ProductID     VARCHAR(20)   NOT NULL,
        CustomerID    VARCHAR(20)   NULL,
        StoreKey      INT           NULL,
        EmployeeID    VARCHAR(20)   NULL,
        PaymentMethod VARCHAR(20)   NOT NULL DEFAULT 'CASH',
        Quantity      INT           NOT NULL,
        UnitPrice     DECIMAL(18,2) NOT NULL,
        Discount      DECIMAL(18,2) NOT NULL DEFAULT 0,
        Revenue       DECIMAL(18,2) NOT NULL,
        Cost          DECIMAL(18,2) NOT NULL DEFAULT 0,
        Profit        AS (Revenue - Cost - Discount) PERSISTED,
        CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: FactSales';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactInventory')
BEGIN
    CREATE TABLE FactInventory (
        InventoryKey BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID      VARCHAR(20)   NOT NULL,
        CheckDate     DATE          NOT NULL,
        ProductID     VARCHAR(20)   NOT NULL,
        StoreKey      INT           NULL,
        QuantityOnHand INT          NOT NULL DEFAULT 0,
        ReorderLevel  INT           NOT NULL DEFAULT 10,
        LastRestocked DATE          NULL,
        CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: FactInventory';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'FactPurchase')
BEGIN
    CREATE TABLE FactPurchase (
        PurchaseKey  BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID     VARCHAR(20)   NOT NULL,
        PurchaseDate DATE          NOT NULL,
        ProductID    VARCHAR(20)   NOT NULL,
        SupplierID   VARCHAR(20)   NOT NULL,
        Quantity     INT           NOT NULL,
        UnitCost     DECIMAL(18,2) NOT NULL,
        TotalCost    DECIMAL(18,2) NOT NULL,
        IsPaid       BIT           NOT NULL DEFAULT 0,
        CreatedAt    DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: FactPurchase';
END

-- ============================================================
-- SCHEMA: 04_create_staging.sql
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_SalesRaw')
BEGIN
    CREATE TABLE STG_SalesRaw (
        ID             INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        SaleDate       NVARCHAR(50)  NULL,
        ProductID      NVARCHAR(50)  NULL,
        CustomerName   NVARCHAR(200) NULL,
        StoreName     NVARCHAR(200) NULL,
        EmployeeName  NVARCHAR(200) NULL,
        PaymentMethod  NVARCHAR(50)  NULL,
        Quantity       NVARCHAR(50)  NULL,
        UnitPrice      NVARCHAR(50)  NULL,
        Discount       NVARCHAR(50)  NULL,
        Revenue        NVARCHAR(50)  NULL,
        LoadStatus     NVARCHAR(20)  NOT NULL DEFAULT 'PENDING',
        ErrorMessage   NVARCHAR(500) NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_SalesRaw';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_ProductRaw')
BEGIN
    CREATE TABLE STG_ProductRaw (
        ID             INT IDENTITY(1,1) PRIMARY KEY,
        ProductID      NVARCHAR(50)  NULL,
        ProductName    NVARCHAR(200) NULL,
        Category       NVARCHAR(100) NULL,
        SubCategory    NVARCHAR(100) NULL,
        UnitPrice      NVARCHAR(50)  NULL,
        SupplierID     NVARCHAR(50)  NULL,
        LoadStatus     NVARCHAR(20)  NOT NULL DEFAULT 'PENDING',
        ErrorMessage   NVARCHAR(500) NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_ProductRaw';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_CustomerRaw')
BEGIN
    CREATE TABLE STG_CustomerRaw (
        ID             INT IDENTITY(1,1) PRIMARY KEY,
        CustomerID     NVARCHAR(50)  NULL,
        CustomerName   NVARCHAR(200) NULL,
        Phone          NVARCHAR(50)  NULL,
        Email          NVARCHAR(100) NULL,
        City           NVARCHAR(100) NULL,
        Region         NVARCHAR(100) NULL,
        CustomerType   NVARCHAR(50)  NULL,
        LoadStatus     NVARCHAR(20)  NOT NULL DEFAULT 'PENDING',
        ErrorMessage   NVARCHAR(500) NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_CustomerRaw';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_InventoryRaw')
BEGIN
    CREATE TABLE STG_InventoryRaw (
        ID             INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        CheckDate      NVARCHAR(50)  NULL,
        ProductID      NVARCHAR(50)  NULL,
        StoreName     NVARCHAR(200) NULL,
        QuantityOnHand NVARCHAR(50)  NULL,
        LoadStatus     NVARCHAR(20)  NOT NULL DEFAULT 'PENDING',
        ErrorMessage   NVARCHAR(500) NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_InventoryRaw';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_PurchaseRaw')
BEGIN
    CREATE TABLE STG_PurchaseRaw (
        ID             INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        PurchaseDate   NVARCHAR(50)  NULL,
        ProductID      NVARCHAR(50)  NULL,
        SupplierID     NVARCHAR(50)  NULL,
        Quantity       NVARCHAR(50)  NULL,
        UnitCost       NVARCHAR(50)  NULL,
        TotalCost      NVARCHAR(50)  NULL,
        IsPaid         NVARCHAR(50)  NULL,
        LoadStatus     NVARCHAR(20)  NOT NULL DEFAULT 'PENDING',
        ErrorMessage   NVARCHAR(500) NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_PurchaseRaw';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_ErrorLog')
BEGIN
    CREATE TABLE STG_ErrorLog (
        ErrorID        INT IDENTITY(1,1) PRIMARY KEY,
        TableName      NVARCHAR(100) NOT NULL,
        ErrorCode      INT           NULL,
        ErrorMessage   NVARCHAR(500) NULL,
        SourceRow      NVARCHAR(MAX) NULL,
        LoadBatch      NVARCHAR(50)  NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_ErrorLog';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ETLLogs')
BEGIN
    CREATE TABLE ETLLogs (
        LogID          INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NULL,
        TableName      NVARCHAR(100) NOT NULL,
        StepName       NVARCHAR(100) NOT NULL,
        RowsProcessed  INT           NOT NULL DEFAULT 0,
        RowsInserted   INT           NOT NULL DEFAULT 0,
        RowsUpdated    INT           NOT NULL DEFAULT 0,
        RowsRejected   INT           NOT NULL DEFAULT 0,
        DurationSec    INT           NULL,
        Status         NVARCHAR(20)  NOT NULL,
        ErrorMessage   NVARCHAR(500) NULL,
        CreatedAt      DATETIME2     NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: ETLLogs';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ETL_Watermark')
BEGIN
    CREATE TABLE ETL_Watermark (
        WatermarkID    INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        TableName      VARCHAR(100)  NOT NULL,
        LastValue      NVARCHAR(100) NULL,
        LastProcessedAt DATETIME2   NOT NULL DEFAULT GETDATE(),
        UNIQUE (TenantID, TableName)
    );
    PRINT 'Created: ETL_Watermark';
END

-- ============================================================
-- SCHEMA: 05_create_datamart.sql
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_SalesSummary')
BEGIN
    CREATE TABLE DM_SalesSummary (
        SummaryKey   BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID     VARCHAR(20)   NOT NULL,
        Year         SMALLINT      NOT NULL,
        Quarter      TINYINT       NOT NULL,
        Month        TINYINT       NOT NULL,
        ProductID    VARCHAR(20)   NULL,
        Category     NVARCHAR(100) NULL,
        TotalRevenue DECIMAL(18,2) NOT NULL DEFAULT 0,
        TotalCost    DECIMAL(18,2) NOT NULL DEFAULT 0,
        TotalProfit  DECIMAL(18,2) NOT NULL DEFAULT 0,
        OrderCount   INT           NOT NULL DEFAULT 0,
        AvgOrderVal  DECIMAL(18,2) NOT NULL DEFAULT 0,
        UpdatedAt    DATETIME2     NOT NULL DEFAULT GETDATE(),
        UNIQUE (TenantID, Year, Quarter, Month, ProductID)
    );
    PRINT 'Created: DM_SalesSummary';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_CustomerRFM')
BEGIN
    CREATE TABLE DM_CustomerRFM (
        RFMKey       INT IDENTITY(1,1) PRIMARY KEY,
        TenantID     VARCHAR(20)   NOT NULL,
        CustomerID   VARCHAR(20)   NOT NULL,
        Recency      INT           NOT NULL,
        Frequency    INT           NOT NULL,
        Monetary     DECIMAL(18,2) NOT NULL,
        RFMScore     VARCHAR(10)    NOT NULL,
        Segment      NVARCHAR(50)  NOT NULL,
        UpdatedAt    DATETIME2     NOT NULL DEFAULT GETDATE(),
        UNIQUE (TenantID, CustomerID)
    );
    PRINT 'Created: DM_CustomerRFM';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_ProductPerformance')
BEGIN
    CREATE TABLE DM_ProductPerformance (
        PerfKey     BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID    VARCHAR(20)   NOT NULL,
        ProductID   VARCHAR(20)   NOT NULL,
        Year        SMALLINT      NOT NULL,
        Month       TINYINT       NOT NULL,
        UnitsSold   INT           NOT NULL DEFAULT 0,
        Revenue     DECIMAL(18,2) NOT NULL DEFAULT 0,
        Profit      DECIMAL(18,2) NOT NULL DEFAULT 0,
        ReturnRate  DECIMAL(5,2)  NOT NULL DEFAULT 0,
        UNIQUE (TenantID, ProductID, Year, Month)
    );
    PRINT 'Created: DM_ProductPerformance';
END

IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'DM_InventoryAlert')
BEGIN
    EXEC('
    CREATE VIEW DM_InventoryAlert AS
    SELECT
        i.TenantID,
        i.StoreKey,
        i.ProductID,
        ISNULL(p.ProductName, i.ProductID) AS ProductName,
        p.Category                          AS CategoryName,
        i.CheckDate,
        i.QuantityOnHand                    AS ClosingStock,
        i.ReorderLevel                      AS ReorderPoint,
        ISNULL(s.StoreName, CAST(i.StoreKey AS NVARCHAR)) AS StoreName,
        CASE
            WHEN i.QuantityOnHand <= ISNULL(i.ReorderLevel, 0)       THEN N''Cảnh báo''
            WHEN i.QuantityOnHand <= ISNULL(i.ReorderLevel, 0) * 1.5 THEN N''Sắp hết''
            ELSE N''Bình thường''
        END AS AlertLevel
    FROM FactInventory i
    LEFT JOIN DimProduct p ON p.ProductID = i.ProductID
    LEFT JOIN DimStore   s ON s.StoreKey  = i.StoreKey
    ');
    PRINT 'Created: DM_InventoryAlert (View)';
END

-- V_SalesEnriched — Sales fact joined với dimensions, dùng cho dashboards
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'V_SalesEnriched')
BEGIN
    EXEC('
    CREATE VIEW V_SalesEnriched AS
    SELECT
        f.SalesKey,
        f.TenantID,
        f.SaleDate,
        YEAR(f.SaleDate)                                        AS Year,
        MONTH(f.SaleDate)                                       AS Month,
        DATEPART(quarter, f.SaleDate)                           AS Quarter,
        DATENAME(month, f.SaleDate)                             AS MonthName,
        f.ProductID,
        ISNULL(p.ProductName, f.ProductID)                      AS ProductName,
        p.Category                                              AS CategoryName,
        p.SubCategory,
        f.CustomerID,
        f.StoreKey,
        ISNULL(s.StoreName, CAST(f.StoreKey AS NVARCHAR))       AS StoreName,
        f.EmployeeID,
        ISNULL(e.EmployeeName, f.EmployeeID)                    AS EmployeeName,
        f.PaymentMethod,
        f.Quantity,
        f.UnitPrice,
        f.Discount,
        f.Revenue,
        f.Cost,
        f.Profit
    FROM FactSales f
    LEFT JOIN DimProduct  p ON p.ProductID  = f.ProductID
    LEFT JOIN DimStore    s ON s.StoreKey   = f.StoreKey
    LEFT JOIN DimEmployee e ON e.EmployeeID = f.EmployeeID
    ');
    PRINT 'Created: V_SalesEnriched (View)';
END

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_EmployeePerformance')
BEGIN
    CREATE TABLE DM_EmployeePerformance (
        PerfKey       BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID      VARCHAR(20)   NOT NULL,
        EmployeeID    VARCHAR(20)   NOT NULL,
        Year          SMALLINT      NOT NULL,
        Month         TINYINT       NOT NULL,
        TotalSales    DECIMAL(18,2) NOT NULL DEFAULT 0,
        OrderCount    INT           NOT NULL DEFAULT 0,
        AvgOrderValue DECIMAL(18,2) NOT NULL DEFAULT 0,
        UNIQUE (TenantID, EmployeeID, Year, Month)
    );
    PRINT 'Created: DM_EmployeePerformance';
END

-- ============================================================
-- SCHEMA: 06_create_indexes.sql
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_FactSales_TenantDate' AND object_id = OBJECT_ID('FactSales'))
    CREATE INDEX IX_FactSales_TenantDate ON FactSales(TenantID, SaleDate);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_FactSales_ProductID' AND object_id = OBJECT_ID('FactSales'))
    CREATE INDEX IX_FactSales_ProductID ON FactSales(ProductID);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_FactInventory_TenantDate' AND object_id = OBJECT_ID('FactInventory'))
    CREATE INDEX IX_FactInventory_TenantDate ON FactInventory(TenantID, CheckDate);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_FactPurchase_TenantDate' AND object_id = OBJECT_ID('FactPurchase'))
    CREATE INDEX IX_FactPurchase_TenantDate ON FactPurchase(TenantID, PurchaseDate);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_DimProduct_TenantID' AND object_id = OBJECT_ID('DimProduct'))
    CREATE INDEX IX_DimProduct_TenantID ON DimProduct(TenantID);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_DimCustomer_TenantID' AND object_id = OBJECT_ID('DimCustomer'))
    CREATE INDEX IX_DimCustomer_TenantID ON DimCustomer(TenantID);
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_STG_SalesRaw_TenantLoad' AND object_id = OBJECT_ID('STG_SalesRaw'))
    CREATE INDEX IX_STG_SalesRaw_TenantLoad ON STG_SalesRaw(TenantID, LoadStatus);
PRINT 'Created: Indexes';

-- ============================================================
-- FIX: Add missing columns to STG tables (idempotent)
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_SalesRaw' AND COLUMN_NAME='ProductName')
    ALTER TABLE STG_SalesRaw ADD ProductName NVARCHAR(200) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_SalesRaw' AND COLUMN_NAME='Category')
    ALTER TABLE STG_SalesRaw ADD Category NVARCHAR(100) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_SalesRaw' AND COLUMN_NAME='SubCategory')
    ALTER TABLE STG_SalesRaw ADD SubCategory NVARCHAR(100) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_SalesRaw' AND COLUMN_NAME='SupplierID')
    ALTER TABLE STG_SalesRaw ADD SupplierID NVARCHAR(50) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_SalesRaw' AND COLUMN_NAME='TenantID')
    ALTER TABLE STG_SalesRaw ADD TenantID VARCHAR(20) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_SalesRaw' AND COLUMN_NAME='City')
    ALTER TABLE STG_SalesRaw ADD City NVARCHAR(100) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_ProductRaw' AND COLUMN_NAME='TenantID')
    ALTER TABLE STG_ProductRaw ADD TenantID VARCHAR(20) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_CustomerRaw' AND COLUMN_NAME='Region')
    ALTER TABLE STG_CustomerRaw ADD Region NVARCHAR(100) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_CustomerRaw' AND COLUMN_NAME='CustomerType')
    ALTER TABLE STG_CustomerRaw ADD CustomerType NVARCHAR(50) NULL;
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='STG_CustomerRaw' AND COLUMN_NAME='TenantID')
    ALTER TABLE STG_CustomerRaw ADD TenantID VARCHAR(20) NULL;
PRINT 'Fixed: STG columns added';

-- ============================================================
-- STORED PROCEDURES
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimDate')
EXEC('
CREATE PROCEDURE usp_Load_DimDate
    @StartDate DATE,
    @EndDate   DATE
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @current DATE = @StartDate;
    WHILE @current <= @EndDate
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM DimDate WHERE DateKey = CAST(FORMAT(@current, ''yyyyMMdd'') AS INT))
        BEGIN
            INSERT INTO DimDate (DateKey, FullDate, Day, Month, Quarter, Year, MonthName, DayOfWeek, WeekOfYear)
            VALUES (
                CAST(FORMAT(@current, ''yyyyMMdd'') AS INT),
                @current,
                DAY(@current),
                MONTH(@current),
                DATEPART(QUARTER, @current),
                YEAR(@current),
                DATENAME(MONTH, @current),
                DATEPART(WEEKDAY, @current),
                DATEPART(ISO_WEEK, @current)
            );
        END
        SET @current = DATEADD(DAY, 1, @current);
    END
    PRINT ''DimDate populated from '' + CAST(@StartDate AS VARCHAR(10)) + '' to '' + CAST(@EndDate AS VARCHAR(10));
END
');
PRINT 'Created: usp_Load_DimDate';

-- usp_Load_DimProduct
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimProduct')
EXEC('
CREATE PROCEDURE usp_Load_DimProduct
AS
BEGIN
    SET NOCOUNT ON;
    MERGE INTO DimProduct AS target
    USING (
        SELECT DISTINCT ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, TenantID
        FROM (
            SELECT ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, TenantID FROM STG_ProductRaw WHERE LoadStatus = ''PENDING''
            UNION ALL
            SELECT ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, TenantID FROM STG_SalesRaw WHERE LoadStatus = ''PENDING''
        ) AS combined
        WHERE ProductID IS NOT NULL AND LEN(RTRIM(ProductID)) > 0
    ) AS source
    ON target.ProductID = source.ProductID
    WHEN NOT MATCHED THEN
        INSERT (ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, TenantID)
        VALUES (source.ProductID, source.ProductName, source.Category, source.SubCategory, source.UnitPrice, source.SupplierID, source.TenantID)
    WHEN MATCHED AND source.UnitPrice <> target.UnitPrice THEN
        UPDATE SET ProductName = source.ProductName, UnitPrice = source.UnitPrice;
END
');
PRINT 'Created: usp_Load_DimProduct';

-- usp_Load_DimCustomer
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimCustomer')
EXEC('
CREATE PROCEDURE usp_Load_DimCustomer
AS
BEGIN
    SET NOCOUNT ON;
    MERGE INTO DimCustomer AS target
    USING (
        SELECT DISTINCT CustomerID, CustomerName, Phone, Email, City,
               ISNULL(Region, ''Unknown'') AS Region,
               ISNULL(CustomerType, ''Individual'') AS CustomerType,
               TenantID
        FROM STG_CustomerRaw WHERE LoadStatus = ''PENDING'' AND CustomerID IS NOT NULL
    ) AS source
    ON target.CustomerID = source.CustomerID
    WHEN NOT MATCHED THEN
        INSERT (CustomerID, CustomerName, Phone, Email, City, Region, CustomerType, TenantID)
        VALUES (source.CustomerID, source.CustomerName, source.Phone, source.Email, source.City, source.Region, source.CustomerType, source.TenantID)
    WHEN MATCHED THEN
        UPDATE SET CustomerName = source.CustomerName, Phone = source.Phone;
END
');
PRINT 'Created: usp_Load_DimCustomer';

-- usp_Transform_FactSales
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Transform_FactSales')
EXEC('
CREATE PROCEDURE usp_Transform_FactSales
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @rows INT;
    SELECT @rows = COUNT(*) FROM STG_SalesRaw WHERE LoadStatus = ''PENDING'';
    INSERT INTO FactSales (TenantID, SaleDate, ProductID, CustomerID, PaymentMethod, Quantity, UnitPrice, Discount, Revenue)
    SELECT
        TenantID,
        TRY_CAST(SaleDate AS DATE),
        LTRIM(RTRIM(ProductID)),
        (SELECT TOP 1 CustomerKey FROM DimCustomer WHERE CustomerName = LTRIM(RTRIM(STG_SalesRaw.CustomerName))),
        ISNULL((SELECT PaymentMethodKey FROM DimPaymentMethod WHERE PaymentMethodName = STG_SalesRaw.PaymentMethod), 1),
        TRY_CAST(Quantity AS INT),
        TRY_CAST(UnitPrice AS DECIMAL(18,2)),
        ISNULL(TRY_CAST(Discount AS DECIMAL(18,2)), 0),
        ISNULL(TRY_CAST(Revenue AS DECIMAL(18,2)), 0)
    FROM STG_SalesRaw
    WHERE LoadStatus = ''PENDING'';
    UPDATE STG_SalesRaw SET LoadStatus = ''LOADED'' WHERE LoadStatus = ''PENDING'';
    PRINT ''Loaded '' + CAST(@rows AS VARCHAR) + '' sales rows into FactSales'';
END
');
PRINT 'Created: usp_Transform_FactSales';

-- usp_Transform_FactInventory
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Transform_FactInventory')
EXEC('
CREATE PROCEDURE usp_Transform_FactInventory
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @rows INT;
    SELECT @rows = COUNT(*) FROM STG_InventoryRaw WHERE LoadStatus = ''PENDING'';
    INSERT INTO FactInventory (TenantID, CheckDate, ProductID, QuantityOnHand, ReorderLevel)
    SELECT
        TenantID,
        TRY_CAST(CheckDate AS DATE),
        LTRIM(RTRIM(ProductID)),
        ISNULL(TRY_CAST(QuantityOnHand AS INT), 0),
        10
    FROM STG_InventoryRaw
    WHERE LoadStatus = ''PENDING'';
    UPDATE STG_InventoryRaw SET LoadStatus = ''LOADED'' WHERE LoadStatus = ''PENDING'';
    PRINT ''Loaded '' + CAST(@rows AS VARCHAR) + '' inventory rows into FactInventory'';
END
');
PRINT 'Created: usp_Transform_FactInventory';

-- usp_Transform_FactPurchase
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Transform_FactPurchase')
EXEC('
CREATE PROCEDURE usp_Transform_FactPurchase
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @rows INT;
    SELECT @rows = COUNT(*) FROM STG_PurchaseRaw WHERE LoadStatus = ''PENDING'';
    INSERT INTO FactPurchase (TenantID, PurchaseDate, ProductID, SupplierID, Quantity, UnitCost, TotalCost, IsPaid)
    SELECT
        TenantID,
        TRY_CAST(PurchaseDate AS DATE),
        LTRIM(RTRIM(ProductID)),
        LTRIM(RTRIM(SupplierID)),
        ISNULL(TRY_CAST(Quantity AS INT), 0),
        ISNULL(TRY_CAST(UnitCost AS DECIMAL(18,2)), 0),
        ISNULL(TRY_CAST(TotalCost AS DECIMAL(18,2)), 0),
        CASE WHEN LOWER(IsPaid) IN (''1'',''yes'',''true'',''paid'') THEN 1 ELSE 0 END
    FROM STG_PurchaseRaw
    WHERE LoadStatus = ''PENDING'';
    UPDATE STG_PurchaseRaw SET LoadStatus = ''LOADED'' WHERE LoadStatus = ''PENDING'';
    PRINT ''Loaded '' + CAST(@rows AS VARCHAR) + '' purchase rows into FactPurchase'';
END
');
PRINT 'Created: usp_Transform_FactPurchase';

-- usp_Load_DimStore
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimStore')
EXEC('
CREATE PROCEDURE usp_Load_DimStore
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO DimStore (TenantID, StoreName, City, Region)
    SELECT DISTINCT
        TenantID,
        StoreName,
        ISNULL(City, CASE WHEN TenantID = ''STORE_HN'' THEN ''Ha Noi'' ELSE ''Ho Chi Minh'' END),
        CASE WHEN TenantID = ''STORE_HN'' THEN ''North'' ELSE ''South'' END
    FROM STG_SalesRaw
    WHERE LoadStatus = ''LOADED''
      AND StoreName IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM DimStore WHERE StoreName = STG_SalesRaw.StoreName);
END
');
PRINT 'Created: usp_Load_DimStore';

-- usp_Load_DimEmployee
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimEmployee')
EXEC('
CREATE PROCEDURE usp_Load_DimEmployee
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO DimEmployee (EmployeeID, EmployeeName, Position, Department, HireDate, TenantID)
    SELECT DISTINCT
        ''EMP_'' + CAST(ROW_NUMBER() OVER(ORDER BY EmployeeName) AS VARCHAR(10)),
        EmployeeName,
        ''Sales Staff'',
        ''Sales'',
        GETDATE(),
        TenantID
    FROM STG_SalesRaw
    WHERE LoadStatus = ''LOADED''
      AND EmployeeName IS NOT NULL
      AND NOT EXISTS (SELECT 1 FROM DimEmployee WHERE EmployeeName = STG_SalesRaw.EmployeeName);
END
');
PRINT 'Created: usp_Load_DimEmployee';

-- usp_Update_Watermark
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Update_Watermark')
EXEC('
CREATE PROCEDURE usp_Update_Watermark
    @TenantID VARCHAR(20),
    @TableName VARCHAR(100),
    @LastValue NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    MERGE INTO ETL_Watermark AS target
    USING (SELECT @TenantID AS TenantID, @TableName AS TableName) AS source
    ON target.TenantID = source.TenantID AND target.TableName = source.TableName
    WHEN MATCHED THEN
        UPDATE SET LastValue = @LastValue, LastProcessedAt = GETDATE()
    WHEN NOT MATCHED THEN
        INSERT (TenantID, TableName, LastValue) VALUES (@TenantID, @TableName, @LastValue);
END
');
PRINT 'Created: usp_Update_Watermark';

-- usp_Refresh_DM_SalesSummary
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Refresh_DM_SalesSummary')
EXEC('
CREATE PROCEDURE usp_Refresh_DM_SalesSummary
AS
BEGIN
    SET NOCOUNT ON;
    MERGE INTO DM_SalesSummary AS target
    USING (
        SELECT
            fs.TenantID,
            YEAR(fs.SaleDate) AS Year,
            MONTH(fs.SaleDate) AS Month,
            DATEPART(QUARTER, fs.SaleDate) AS Quarter,
            fs.ProductID,
            dp.Category,
            SUM(fs.Revenue) AS TotalRevenue,
            SUM(fs.Revenue) * 0.7 AS TotalCost,
            SUM(fs.Revenue) * 0.25 AS TotalProfit,
            COUNT(*) AS OrderCount,
            CASE WHEN COUNT(*) > 0 THEN SUM(fs.Revenue) / COUNT(*) ELSE 0 END AS AvgOrderVal
        FROM FactSales fs
        LEFT JOIN DimProduct dp ON fs.ProductID = dp.ProductID
        GROUP BY fs.TenantID, YEAR(fs.SaleDate), MONTH(fs.SaleDate), DATEPART(QUARTER, fs.SaleDate), fs.ProductID, dp.Category
    ) AS source
    ON target.TenantID = source.TenantID AND target.Year = source.Year
        AND target.Month = source.Month AND target.ProductID = source.ProductID
    WHEN MATCHED THEN UPDATE SET
        TotalRevenue = source.TotalRevenue, TotalCost = source.TotalCost,
        TotalProfit = source.TotalProfit, OrderCount = source.OrderCount,
        AvgOrderVal = source.AvgOrderVal, UpdatedAt = GETDATE()
    WHEN NOT MATCHED THEN INSERT
        (TenantID, Year, Quarter, Month, ProductID, Category, TotalRevenue, TotalCost, TotalProfit, OrderCount, AvgOrderVal)
        VALUES (source.TenantID, source.Year, source.Quarter, source.Month, source.ProductID,
                source.Category, source.TotalRevenue, source.TotalCost, source.TotalProfit,
                source.OrderCount, source.AvgOrderVal);
    PRINT ''DM_SalesSummary refreshed'';
END
');
PRINT 'Created: usp_Refresh_DM_SalesSummary';

-- usp_Refresh_DM_CustomerRFM
IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Refresh_DM_CustomerRFM')
EXEC('
CREATE PROCEDURE usp_Refresh_DM_CustomerRFM
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @maxDate DATE = (SELECT ISNULL(MAX(SaleDate), GETDATE()) FROM FactSales);
    MERGE INTO DM_CustomerRFM AS target
    USING (
        SELECT
            fs.TenantID,
            fs.CustomerID,
            DATEDIFF(DAY, MAX(fs.SaleDate), @maxDate) AS Recency,
            COUNT(*) AS Frequency,
            SUM(fs.Revenue) AS Monetary
        FROM FactSales fs
        WHERE fs.CustomerID IS NOT NULL
        GROUP BY fs.TenantID, fs.CustomerID
    ) AS source
    ON target.TenantID = source.TenantID AND target.CustomerID = source.CustomerID
    WHEN MATCHED THEN UPDATE SET Recency = source.Recency, Frequency = source.Frequency, Monetary = source.Monetary, UpdatedAt = GETDATE()
    WHEN NOT MATCHED THEN INSERT (TenantID, CustomerID, Recency, Frequency, Monetary, RFMScore, Segment)
        VALUES (source.TenantID, source.CustomerID, source.Recency, source.Frequency, source.Monetary, ''000'', ''New'');
    UPDATE DM_CustomerRFM SET
        RFMScore = CAST(
            CASE WHEN Recency <= 30  THEN 3 WHEN Recency <= 60  THEN 2 ELSE 1 END AS VARCHAR) +
            CAST(
            CASE WHEN Frequency >= 10 THEN 3 WHEN Frequency >= 5  THEN 2 ELSE 1 END AS VARCHAR) +
            CAST(
            CASE WHEN Monetary >= 10000000 THEN 3 WHEN Monetary >= 5000000 THEN 2 ELSE 1 END AS VARCHAR),
        Segment = CASE
            WHEN RFMScore LIKE ''3[12][12]'' THEN ''Champions''
            WHEN RFMScore LIKE ''[12]3[12]'' THEN ''Loyal''
            WHEN RFMScore LIKE ''[12][12]3'' THEN ''Big Spender''
            WHEN RFMScore LIKE ''[12][12][12]'' THEN ''At Risk''
            ELSE ''New'' END;
    PRINT ''DM_CustomerRFM refreshed'';
END
');
PRINT 'Created: usp_Refresh_DM_CustomerRFM';

-- ============================================================
-- VIEWS
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'v_FactSales_ByTenant')
EXEC('
CREATE VIEW v_FactSales_ByTenant AS
SELECT
    fs.SalesKey, fs.TenantID, fs.SaleDate,
    dp.ProductName, dp.Category,
    dc.CustomerName, dc.City,
    ds.StoreName, ds.City AS StoreCity,
    fs.Quantity, fs.UnitPrice, fs.Discount, fs.Revenue, fs.Profit,
    fs.CreatedAt
FROM FactSales fs
LEFT JOIN DimProduct dp ON fs.ProductID = dp.ProductID
LEFT JOIN DimCustomer dc ON fs.CustomerID = dc.CustomerID
LEFT JOIN DimStore ds ON fs.StoreKey = ds.StoreKey
');
PRINT 'Created: v_FactSales_ByTenant';

IF NOT EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_SetTenantContext')
EXEC('
CREATE PROCEDURE usp_SetTenantContext @TenantID VARCHAR(20) AS BEGIN
    SELECT ''Current tenant: '' + @TenantID;
END
');
PRINT 'Created: usp_SetTenantContext';

IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'v_DM_SalesSummary_ByTenant')
EXEC('
CREATE VIEW v_DM_SalesSummary_ByTenant AS
SELECT
    TenantID, Year, Quarter, Month,
    SUM(TotalRevenue) AS TotalRevenue,
    SUM(TotalProfit) AS TotalProfit,
    SUM(OrderCount) AS TotalOrders
FROM DM_SalesSummary
GROUP BY TenantID, Year, Quarter, Month
');
PRINT 'Created: v_DM_SalesSummary_ByTenant';

-- ============================================================
-- POPULATE DATES
-- ============================================================
EXEC usp_Load_DimDate @StartDate = '2015-01-01', @EndDate = '2030-12-31';
PRINT 'DimDate populated (2015-2030)';

-- ============================================================
-- BOOTSTRAP: Create default admin user
-- NOTE: Hash = bcrypt(base64(SHA2_256(password))).
--       Password: admin / M1tjtnrx
--       Hash nay tuong thich voi passlib.verify(plain, hash) trong API.
--       Neu can doi: thay the gia tri PasswordHash ben duoi roi chay lai script.
-- ============================================================
IF NOT EXISTS (SELECT 1 FROM AppUsers WHERE Username = 'admin')
BEGIN
    DECLARE @AdminHash VARCHAR(255) = '$2b$12$OWPB.4o0QUxQchp2.qM1QOCumg5nZlJXpvO2Rerpqb74sNW2/Ovym';
    INSERT INTO AppUsers (Username, PasswordHash, TenantID, Role, IsActive)
    VALUES ('admin', @AdminHash, NULL, 'superadmin', 1);
    PRINT 'Bootstrap: Created admin user (superadmin)';
END
ELSE
BEGIN
    PRINT 'Bootstrap: admin user already exists — skipping';
END

PRINT '============================================================';
PRINT 'HOAN TAT TAO DATA WAREHOUSE - MULTI-TENANT';
PRINT '============================================================';
