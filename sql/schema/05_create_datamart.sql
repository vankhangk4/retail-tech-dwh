-- ============================================================
-- FILE: sql/schema/05_create_datamart.sql
-- Mô tả: Tạo Data Mart Layer (Aggregate Tables/Views)
-- ============================================================

-- 4.6. DM_SalesSummary — Aggregate Table phục vụ Dashboard Doanh thu
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_SalesSummary')
BEGIN
    CREATE TABLE DM_SalesSummary (
        SummaryKey    BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID     VARCHAR(20)   NOT NULL,
        DateKey      INT           NOT NULL,
        StoreKey     INT           NOT NULL,
        CategoryName NVARCHAR(100) NOT NULL,
        TotalRevenue DECIMAL(18,2) NOT NULL DEFAULT 0,
        TotalProfit  DECIMAL(18,2) NOT NULL DEFAULT 0,
        TotalOrders  INT          NOT NULL DEFAULT 0,
        TotalQty     INT          NOT NULL DEFAULT 0,
        LastRefreshed DATETIME2  NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: DM_SalesSummary';
END

-- 4.6. DM_ProductPerformance — Aggregate View phục vụ Dashboard Sản phẩm
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'DM_ProductPerformance')
BEGIN
    EXEC('
    CREATE VIEW DM_ProductPerformance AS
    SELECT
        f.TenantID,
        f.ProductKey,
        p.ProductCode,
        p.ProductName,
        p.CategoryName,
        p.Brand,
        SUM(f.Quantity)           AS TotalQtySold,
        SUM(f.NetSalesAmount)     AS TotalRevenue,
        SUM(f.GrossProfitAmount)  AS TotalProfit,
        SUM(f.GrossSalesAmount)   AS TotalGrossSales,
        AVG(f.UnitPrice)          AS AvgSellingPrice,
        SUM(f.DiscountAmount)     AS TotalDiscount,
        COUNT(DISTINCT f.InvoiceNumber) AS TotalTransactions,
        SUM(CAST(f.ReturnFlag AS INT)) AS TotalReturns,
        CASE WHEN SUM(f.GrossSalesAmount) > 0
             THEN SUM(f.DiscountAmount) / SUM(f.GrossSalesAmount) * 100
             ELSE 0 END           AS DiscountRatePct,
        CASE WHEN SUM(f.Quantity) > 0
             THEN SUM(f.GrossProfitAmount) / SUM(f.Quantity)
             ELSE 0 END           AS ProfitPerUnit
    FROM FactSales f
    INNER JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.IsCurrent = 1
    WHERE f.ReturnFlag = 0
    GROUP BY f.TenantID, f.ProductKey, p.ProductCode, p.ProductName,
             p.CategoryName, p.Brand
    ');
    PRINT 'Created: DM_ProductPerformance (View)';
END

-- 4.6. DM_InventoryAlert — Aggregate View phục vụ Dashboard Tồn kho
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'DM_InventoryAlert')
BEGIN
    EXEC('
    CREATE VIEW DM_InventoryAlert AS
    SELECT
        i.TenantID,
        i.StoreKey,
        i.ProductID,
        ISNULL(p.ProductName, i.ProductID)                           AS ProductName,
        p.Category                                                    AS CategoryName,
        i.CheckDate,
        i.QuantityOnHand                                              AS ClosingStock,
        i.ReorderLevel                                                AS ReorderPoint,
        ISNULL(s.StoreName, CAST(i.StoreKey AS NVARCHAR))            AS StoreName,
        CASE
            WHEN i.QuantityOnHand <= ISNULL(i.ReorderLevel, 0)       THEN N''Cảnh báo''
            WHEN i.QuantityOnHand <= ISNULL(i.ReorderLevel, 0) * 1.5 THEN N''Sắp hết''
            ELSE N''Bình thường''
        END AS AlertLevel,
        CASE
            WHEN i.QuantityOnHand <= ISNULL(i.ReorderLevel, 0)
            THEN ISNULL(i.ReorderLevel, 0) - i.QuantityOnHand
            ELSE 0
        END AS StockShortage
    FROM FactInventory i
    LEFT JOIN DimProduct p ON p.ProductID = i.ProductID
    LEFT JOIN DimStore   s ON s.StoreKey  = i.StoreKey
    ');
    PRINT 'Created: DM_InventoryAlert (View)';
END

-- 4.6. DM_CustomerRFM — Aggregate Table phục vụ Dashboard Khách hàng (RFM Analysis)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_CustomerRFM')
BEGIN
    CREATE TABLE DM_CustomerRFM (
        RFMKey       BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID    VARCHAR(20)   NOT NULL,
        CustomerKey INT          NOT NULL,
        CustomerCode VARCHAR(50)  NOT NULL,
        FullName    NVARCHAR(150) NOT NULL,
        Recency     INT          NOT NULL,   -- Số ngày từ lần mua cuối đến hôm nay
        Frequency   INT          NOT NULL,   -- Tổng số giao dịch
        Monetary    DECIMAL(18,2) NOT NULL,   -- Tổng doanh thu
        R_Score     TINYINT      NOT NULL,   -- Điểm Recency (1-5)
        F_Score     TINYINT      NOT NULL,   -- Điểm Frequency (1-5)
        M_Score     TINYINT      NOT NULL,   -- Điểm Monetary (1-5)
        RFM_Score   INT          NOT NULL,   -- Tổng điểm R+F+M
        Segment     NVARCHAR(50)  NOT NULL,   -- Phân khúc: Champions, Loyal, At_Risk, etc.
        LastRefreshed DATETIME2  NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: DM_CustomerRFM';
END

-- 4.6. DM_EmployeePerformance — Aggregate View phục vụ Dashboard Nhân viên
IF NOT EXISTS (SELECT * FROM sys.views WHERE name = 'DM_EmployeePerformance')
BEGIN
    EXEC('
    CREATE VIEW DM_EmployeePerformance AS
    SELECT
        f.TenantID,
        f.EmployeeKey,
        e.FullName,
        e.Position,
        e.StoreKey,
        s.StoreName,
        COUNT(DISTINCT f.InvoiceNumber) AS TotalTransactions,
        SUM(f.Quantity)           AS TotalQtySold,
        SUM(f.NetSalesAmount)     AS TotalRevenue,
        SUM(f.GrossProfitAmount)  AS TotalProfit,
        AVG(f.UnitPrice)          AS AvgSellingPrice,
        SUM(CAST(f.ReturnFlag AS INT)) AS TotalReturns,
        CASE WHEN COUNT(DISTINCT f.InvoiceNumber) > 0
             THEN SUM(f.Quantity) * 1.0 / COUNT(DISTINCT f.InvoiceNumber)
             ELSE 0 END           AS AvgItemsPerTransaction,
        CASE WHEN SUM(f.NetSalesAmount) > 0
             THEN SUM(f.GrossProfitAmount) / SUM(f.NetSalesAmount) * 100
             ELSE 0 END           AS ProfitMarginPct
    FROM FactSales f
    INNER JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
    INNER JOIN DimStore s ON s.StoreKey = f.StoreKey
    GROUP BY f.TenantID, f.EmployeeKey, e.FullName, e.Position,
             e.StoreKey, s.StoreName
    ');
    PRINT 'Created: DM_EmployeePerformance (View)';
END

-- Bổ sung Index cho DM layer (Dashboard query theo TenantID + DateKey)
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_SalesSummary')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_Sales_Tenant_Date')
        CREATE INDEX IX_DM_Sales_Tenant_Date ON DM_SalesSummary(TenantID, DateKey);
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_Sales_Store')
        CREATE INDEX IX_DM_Sales_Store ON DM_SalesSummary(TenantID, StoreKey, DateKey);
END

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_CustomerRFM')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_CustRFM_Tenant')
        CREATE INDEX IX_DM_CustRFM_Tenant ON DM_CustomerRFM(TenantID, Segment);
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_CustRFM_Customer')
        CREATE INDEX IX_DM_CustRFM_Customer ON DM_CustomerRFM(TenantID, CustomerKey);
END

-- 4.2B.1. Unique Index SCD2 cho DimProduct và DimCustomer
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'DimProduct')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_DimProduct_Current')
        CREATE UNIQUE INDEX UQ_DimProduct_Current ON DimProduct(ProductCode) WHERE IsCurrent = 1;
END

IF EXISTS (SELECT * FROM sys.tables WHERE name = 'DimCustomer')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_DimCustomer_Current')
        CREATE UNIQUE INDEX UQ_DimCustomer_Current ON DimCustomer(TenantID, CustomerCode) WHERE IsCurrent = 1;
END

PRINT 'Done: 05_create_datamart.sql';
