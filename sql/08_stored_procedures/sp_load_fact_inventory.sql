-- ============================================================
-- Script: 08_stored_procedures/sp_load_fact_inventory.sql
-- Mục đích: Load FactInventory
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_FactInventory', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_FactInventory;
GO
CREATE PROCEDURE dbo.sp_Load_FactInventory
    @BatchDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @BatchDate IS NULL SET @BatchDate = CAST(GETDATE() AS DATE);
    DECLARE @ProcessDate DATE = @BatchDate;
    DECLARE @RowsLoaded INT = 0;

    BEGIN TRY
        INSERT INTO dbo.FactInventory (
            DateKey, ProductKey, StoreKey, SupplierKey,
            OpeningStock, ClosingStock, StockReceived, StockSold, StockAdjusted,
            ReorderPoint, UnitCost, TotalInventoryValue
        )
        SELECT
            CONVERT(INT, FORMAT(s.NgayChot, 'yyyyMMdd'))         AS DateKey,
            ISNULL(p.ProductKey, -1)                             AS ProductKey,
            st.StoreKey,
            ISNULL(sup.SupplierKey, -1)                          AS SupplierKey,
            s.TonDauNgay,
            s.TonCuoiNgay,
            s.NhapTrongNgay,
            s.XuatTrongNgay,
            0,
            NULL,
            ISNULL(p.UnitCostPrice, 0),
            s.TonCuoiNgay * ISNULL(p.UnitCostPrice, 0)         AS TotalInventoryValue
        FROM dbo.STG_InventoryRaw s
        INNER JOIN dbo.DimStore st ON st.StoreCode = s.MaCH
        LEFT  JOIN dbo.DimProduct p ON p.ProductCode = s.MaSP AND p.IsCurrent = 1
        LEFT  JOIN dbo.DimSupplier sup ON sup.SupplierCode = s.MaNCC
        WHERE CAST(s.NgayChot AS DATE) = @ProcessDate
          AND NOT EXISTS (
              SELECT 1 FROM dbo.FactInventory fi
              WHERE fi.DateKey = CONVERT(INT, FORMAT(s.NgayChot, 'yyyyMMdd'))
                AND fi.ProductKey = ISNULL(p.ProductKey, -1)
                AND fi.StoreKey = st.StoreKey
          );

        SET @RowsLoaded = @@ROWCOUNT;

        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, RowsProcessed, RowsInserted, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_FactInventory', 'SUCCESS',
                @RowsLoaded, @RowsLoaded, GETDATE());

        PRINT 'sp_Load_FactInventory: ' + CAST(@RowsLoaded AS VARCHAR) + ' rows loaded.';

    END TRY
    BEGIN CATCH
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, ErrorMessage, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_FactInventory', 'FAILED', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_FactInventory created.';
GO
