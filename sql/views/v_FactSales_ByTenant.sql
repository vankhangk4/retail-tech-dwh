-- ============================================================
-- FILE: sql/views/v_FactSales_ByTenant.sql
-- Mô tả: View tự động lọc theo SESSION_CONTEXT tenant_id
-- ============================================================

IF EXISTS (SELECT * FROM sys.views WHERE name = 'v_FactSales_ByTenant')
BEGIN
    DROP VIEW v_FactSales_ByTenant;
END
GO

CREATE VIEW v_FactSales_ByTenant AS
SELECT
    f.SalesKey,
    f.TenantID,
    f.DateKey,
    d.FullDate,
    f.ProductKey,
    p.ProductCode,
    p.ProductName,
    p.CategoryName,
    f.CustomerKey,
    f.StoreKey,
    s.StoreName,
    f.EmployeeKey,
    f.InvoiceNumber,
    f.Quantity,
    f.UnitPrice,
    f.DiscountAmount,
    f.GrossSalesAmount,
    f.NetSalesAmount,
    f.CostAmount,
    f.GrossProfitAmount,
    f.GrossProfitAmount / NULLIF(f.GrossSalesAmount, 0) * 100 AS GrossMarginPct,
    f.TaxAmount,
    f.SalesChannel,
    f.ReturnFlag,
    f.LoadDatetime
FROM FactSales f
INNER JOIN DimDate d ON d.DateKey = f.DateKey
INNER JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.IsCurrent = 1
INNER JOIN DimStore s ON s.StoreKey = f.StoreKey
WHERE f.TenantID = ISNULL(CAST(SESSION_CONTEXT(N'tenant_id') AS VARCHAR(20)), '##INVALID##');
GO

-- ============================================================
-- FILE: sql/views/usp_SetTenantContext.sql
-- Mô tả: Stored Procedure set context trước khi truy vấn qua View
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_SetTenantContext')
BEGIN
    DROP PROCEDURE usp_SetTenantContext;
END
GO

CREATE PROCEDURE usp_SetTenantContext
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Tenants WHERE TenantID = @TenantID AND IsActive = 1)
    BEGIN
        RAISERROR('Tenant khong hop le hoac khong hoat dong.', 16, 1);
        RETURN;
    END

    EXEC sp_set_session_context N'tenant_id', @TenantID, @read_only = 1;
END;
GO

-- Cách sử dụng:
-- EXEC usp_SetTenantContext 'STORE_HN';
-- SELECT * FROM v_FactSales_ByTenant WHERE DateKey = 20240115;
-- Lưu ý: SESSION_CONTEXT reset khi kết thúc connection

PRINT 'Created: v_FactSales_ByTenant and usp_SetTenantContext';

-- ============================================================
-- FILE: sql/views/v_DM_SalesSummary_ByTenant.sql
-- ============================================================

IF EXISTS (SELECT * FROM sys.views WHERE name = 'v_DM_SalesSummary_ByTenant')
BEGIN
    DROP VIEW v_DM_SalesSummary_ByTenant;
END
GO

CREATE VIEW v_DM_SalesSummary_ByTenant AS
SELECT
    dm.SummaryKey,
    dm.TenantID,
    dm.DateKey,
    d.FullDate,
    dm.StoreKey,
    s.StoreName,
    dm.CategoryName,
    dm.TotalRevenue,
    dm.TotalProfit,
    dm.TotalOrders,
    dm.TotalQty,
    dm.TotalProfit / NULLIF(dm.TotalRevenue, 0) * 100 AS ProfitMarginPct,
    dm.LastRefreshed
FROM DM_SalesSummary dm
INNER JOIN DimDate d ON d.DateKey = dm.DateKey
INNER JOIN DimStore s ON s.StoreKey = dm.StoreKey
WHERE dm.TenantID = ISNULL(CAST(SESSION_CONTEXT(N'tenant_id') AS VARCHAR(20)), '##INVALID##');
GO

PRINT 'Created: v_DM_SalesSummary_ByTenant';