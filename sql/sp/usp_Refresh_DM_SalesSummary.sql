-- ============================================================
-- FILE: sql/sp/usp_Refresh_DM_SalesSummary.sql
-- Mô tả: Refresh Data Mart DM_SalesSummary theo tenant
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Refresh_DM_SalesSummary')
BEGIN
    DROP PROCEDURE usp_Refresh_DM_SalesSummary;
END
GO

CREATE PROCEDURE usp_Refresh_DM_SalesSummary
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- Xóa data cũ của tenant
    DELETE FROM DM_SalesSummary WHERE TenantID = @TenantID;

    -- Tính toán và insert data mới
    INSERT INTO DM_SalesSummary (
        TenantID, DateKey, StoreKey, CategoryName,
        TotalRevenue, TotalProfit, TotalOrders, TotalQty, LastRefreshed
    )
    SELECT
        f.TenantID,
        f.DateKey,
        f.StoreKey,
        p.CategoryName,
        SUM(f.NetSalesAmount),
        SUM(f.GrossProfitAmount),
        COUNT(DISTINCT f.InvoiceNumber),
        SUM(f.Quantity),
        GETDATE()
    FROM FactSales f
    INNER JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.IsCurrent = 1
    WHERE f.TenantID = @TenantID
    GROUP BY f.TenantID, f.DateKey, f.StoreKey, p.CategoryName;
END;
GO

PRINT 'Created: usp_Refresh_DM_SalesSummary';