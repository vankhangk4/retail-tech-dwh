-- ============================================================
-- FILE: sql/sp/usp_Transform_FactInventory.sql
-- Mô tả: Transform và Load FactInventory (có @TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Transform_FactInventory')
BEGIN
    DROP PROCEDURE usp_Transform_FactInventory;
END
GO

CREATE PROCEDURE usp_Transform_FactInventory
    @BatchDate DATE = NULL,
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        IF @BatchDate IS NULL
            SET @BatchDate = CAST(GETDATE() AS DATE);

        IF NOT EXISTS (SELECT 1 FROM Tenants WHERE TenantID = @TenantID AND IsActive = 1)
        BEGIN
            RAISERROR('Tenant khong hop le hoac khong hoat dong.', 16, 1);
            RETURN;
        END

        INSERT INTO FactInventory (
            TenantID, DateKey, ProductKey, StoreKey, SupplierKey,
            OpeningStock, ClosingStock, StockReceived, StockSold,
            StockAdjusted, ReorderPoint, UnitCost, TotalInventoryValue, LoadDatetime
        )
        SELECT
            @TenantID,
            CONVERT(INT, FORMAT(i.NgayChupAnh, 'yyyyMMdd')),
            p.ProductKey,
            st.StoreKey,
            NULL,
            ISNULL(i.TonDauNgay, 0),
            ISNULL(i.TonCuoiNgay, 0),
            ISNULL(i.NhapTrongNgay, 0),
            ISNULL(i.BanTrongNgay, 0),
            ISNULL(i.DieuChinh, 0),
            NULL,
            ISNULL(i.DonGiaVon, 0),
            ISNULL(i.TonCuoiNgay, 0) * ISNULL(i.DonGiaVon, 0),
            GETDATE()
        FROM STG_InventoryRaw i
        INNER JOIN DimProduct p ON p.ProductCode = i.MaSP AND p.IsCurrent = 1
        INNER JOIN DimStore st ON st.StoreCode = i.MaCH AND st.TenantID = @TenantID
        WHERE i.TenantID = @TenantID
          AND i.NgayChupAnh = @BatchDate
          AND NOT EXISTS (
              SELECT 1 FROM FactInventory f
              WHERE f.TenantID = @TenantID
                AND f.DateKey = CONVERT(INT, FORMAT(i.NgayChupAnh, 'yyyyMMdd'))
                AND f.ProductKey = p.ProductKey
                AND f.StoreKey = st.StoreKey
          );

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO

PRINT 'Created: usp_Transform_FactInventory';