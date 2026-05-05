-- ============================================================
-- FILE: sql/sp/usp_Refresh_DM_InventoryAlert.sql
-- Mô tả: Refresh Data Mart DM_InventoryAlert (dựa trên FactInventory)
-- Được gọi từ ETL Orchestrator sau mỗi lần nạp dữ liệu
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Refresh_DM_InventoryAlert')
BEGIN
    DROP PROCEDURE usp_Refresh_DM_InventoryAlert;
END
GO

CREATE PROCEDURE usp_Refresh_DM_InventoryAlert
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
    BEGIN TRANSACTION;

    -- Xóa dữ liệu cũ của tenant này
    DELETE FROM DM_InventoryAlert WHERE TenantID = @TenantID;

    -- Tính toán và insert dữ liệu alert mới
    -- Lấy bản ghi tồn kho mới nhất (có DateKey cao nhất) cho mỗi sản phẩm/cửa hàng
    INSERT INTO DM_InventoryAlert (
        TenantID,
        StoreKey,
        ProductKey,
        ProductCode,
        ProductName,
        CategoryName,
        LatestDateKey,
        ClosingStock,
        ReorderPoint,
        AlertLevel,
        StockShortage,
        LastRefreshed
    )
    SELECT
        inv.TenantID,
        inv.StoreKey,
        inv.ProductKey,
        p.ProductCode,
        p.ProductName,
        p.CategoryName,
        inv.DateKey,
        inv.ClosingStock,
        inv.ReorderPoint,
        -- Alert Level logic
        CASE
            WHEN inv.ClosingStock <= ISNULL(inv.ReorderPoint, 0) THEN N'Cảnh báo'
            WHEN inv.ClosingStock <= ISNULL(inv.ReorderPoint, 0) * 1.5 THEN N'Sắp hết'
            ELSE N'Bình thường'
        END AS AlertLevel,
        -- Stock Shortage (số lượng cần đặt hàng)
        CASE
            WHEN inv.ClosingStock <= ISNULL(inv.ReorderPoint, 0)
            THEN ISNULL(inv.ReorderPoint, 0) - inv.ClosingStock
            ELSE 0
        END AS StockShortage,
        GETDATE()
    FROM (
        -- CTE: Lấy bản ghi tồn kho mới nhất cho mỗi product/store
        SELECT
            TenantID,
            StoreKey,
            ProductKey,
            DateKey,
            ClosingStock,
            ReorderPoint,
            ROW_NUMBER() OVER (
                PARTITION BY TenantID, StoreKey, ProductKey
                ORDER BY DateKey DESC
            ) AS rn
        FROM FactInventory
        WHERE TenantID = @TenantID
    ) inv
    INNER JOIN DimProduct p ON p.ProductKey = inv.ProductKey AND p.IsCurrent = 1
    WHERE inv.rn = 1;  -- Chỉ lấy bản ghi mới nhất

    COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW;
    END CATCH;

END;
GO

PRINT 'Created: usp_Refresh_DM_InventoryAlert';
