-- ============================================================
-- Script: 08_stored_procedures/sp_main_etl.sql
-- Mục đích: ETL Orchestrator - điều phối toàn bộ pipeline
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Main_ETL', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Main_ETL;
GO
CREATE PROCEDURE dbo.sp_Main_ETL
    @BatchDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @BatchDate IS NULL
        SET @BatchDate = CAST(GETDATE() AS DATE);

    DECLARE @StartTime DATETIME2 = GETDATE();
    DECLARE @TotalRowsProcessed INT = 0;
    DECLARE @ErrorMessage NVARCHAR(MAX) = NULL;
    DECLARE @PipelineStatus VARCHAR(20) = 'SUCCESS';

    PRINT '============================================';
    PRINT '  sp_Main_ETL Started | BatchDate: ' + CAST(@BatchDate AS VARCHAR);
    PRINT '============================================';

    BEGIN TRY
        -- =============================================
        -- PHASE 1: Load Dimensions (order matters!)
        -- =============================================

        PRINT '';
        PRINT '>>> [1] Loading DimSupplier...';
        EXEC dbo.sp_Load_DimSupplier;

        PRINT '>>> [2] Loading DimProduct (SCD2)...';
        EXEC dbo.sp_Load_DimProduct;

        PRINT '>>> [3] Loading DimCustomer...';
        EXEC dbo.sp_Load_DimCustomer;

        PRINT '>>> [4] Loading DimStore...';
        EXEC dbo.sp_Load_DimStore;

        PRINT '>>> [5] Loading DimEmployee...';
        EXEC dbo.sp_Load_DimEmployee;

        -- =============================================
        -- PHASE 2: Load Facts
        -- =============================================

        PRINT '>>> [6] Loading FactSales...';
        EXEC dbo.sp_Load_FactSales @BatchDate = @BatchDate;

        PRINT '>>> [7] Loading FactInventory...';
        EXEC dbo.sp_Load_FactInventory @BatchDate = @BatchDate;

        PRINT '>>> [8] Loading FactPurchase...';
        EXEC dbo.sp_Load_FactPurchase @BatchDate = @BatchDate;

        -- =============================================
        -- PHASE 3: Refresh Data Marts
        -- =============================================

        PRINT '>>> [9] Refreshing DM_SalesDailySummary...';
        EXEC dbo.sp_Refresh_DM_SalesSummary @BatchDate = @BatchDate;

        PRINT '>>> [10] Refreshing DM_InventoryAlert...';
        EXEC dbo.sp_Refresh_DM_InventoryAlert;

        -- =============================================
        -- PHASE 4: Update Watermarks
        -- =============================================

        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_SalesRaw', @Status = 'SUCCESS';
        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_InventoryRaw', @Status = 'SUCCESS';
        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_ProductRaw', @Status = 'SUCCESS';
        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_CustomerRaw', @Status = 'SUCCESS';
        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_StoreRaw', @Status = 'SUCCESS';
        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_EmployeeRaw', @Status = 'SUCCESS';
        EXEC dbo.sp_Update_Watermark @SourceName = 'STG_SupplierRaw', @Status = 'SUCCESS';

    END TRY
    BEGIN CATCH
        SET @PipelineStatus = 'FAILED';
        SET @ErrorMessage = ERROR_MESSAGE();

        -- Update watermark to FAILED
        EXEC dbo.sp_Update_Watermark
            @SourceName = 'STG_SalesRaw',
            @Status = 'FAILED',
            @Notes = @ErrorMessage;

        PRINT '';
        PRINT '!!! ETL PIPELINE FAILED: ' + @ErrorMessage;
    END CATCH

    -- =============================================
    -- Log overall pipeline run
    -- =============================================
    DECLARE @DurationSeconds DECIMAL(10,2) = DATEDIFF(SECOND, @StartTime, GETDATE());

    INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, Duration_Seconds, ErrorMessage, LoadDatetime)
    VALUES (
        @BatchDate,
        'ETL_Main',
        'Orchestrator',
        @PipelineStatus,
        @DurationSeconds,
        @ErrorMessage,
        GETDATE()
    );

    PRINT '';
    PRINT '============================================';
    PRINT '  sp_Main_ETL Finished | Status: ' + @PipelineStatus;
    PRINT '  Duration: ' + CAST(@DurationSeconds AS VARCHAR) + ' seconds';
    PRINT '============================================';

    IF @PipelineStatus = 'FAILED'
        THROW 50000, @ErrorMessage, 1;
END;
GO

-- ============================================================
-- SP: sp_Refresh_DM_SalesSummary
-- ============================================================
IF OBJECT_ID('dbo.sp_Refresh_DM_SalesSummary', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Refresh_DM_SalesSummary;
GO
CREATE PROCEDURE dbo.sp_Refresh_DM_SalesSummary
    @BatchDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF @BatchDate IS NULL SET @BatchDate = CAST(GETDATE() AS DATE);

    BEGIN TRY
        -- Upsert daily summary
        MERGE dbo.DM_SalesDailySummary AS target
        USING (
            SELECT
                f.DateKey,
                f.StoreKey,
                f.ProductKey,
                p.CategoryName,
                SUM(f.GrossSalesAmount)  AS GrossSalesAmount,
                SUM(f.NetSalesAmount)    AS NetSalesAmount,
                SUM(f.CostAmount)        AS CostAmount,
                SUM(f.GrossProfitAmount) AS GrossProfitAmount,
                SUM(f.Quantity)          AS QuantitySold,
                COUNT(DISTINCT f.InvoiceNumber) AS TransactionCount,
                SUM(CASE WHEN f.ReturnFlag = 1 THEN 1 ELSE 0 END) AS ReturnCount
            FROM dbo.FactSales f
            LEFT JOIN dbo.DimProduct p ON p.ProductKey = f.ProductKey
            WHERE f.DateKey = CONVERT(INT, FORMAT(@BatchDate, 'yyyyMMdd'))
            GROUP BY f.DateKey, f.StoreKey, f.ProductKey, p.CategoryName
        ) AS source (
            DateKey, StoreKey, ProductKey, CategoryName,
            GrossSalesAmount, NetSalesAmount, CostAmount, GrossProfitAmount,
            QuantitySold, TransactionCount, ReturnCount
        )
        ON target.DateKey = source.DateKey
           AND ISNULL(target.StoreKey, -1) = ISNULL(source.StoreKey, -1)
           AND ISNULL(target.ProductKey, -1) = ISNULL(source.ProductKey, -1)
        WHEN MATCHED THEN UPDATE SET
            target.GrossSalesAmount  = source.GrossSalesAmount,
            target.NetSalesAmount    = source.NetSalesAmount,
            target.CostAmount        = source.CostAmount,
            target.GrossProfitAmount = source.GrossProfitAmount,
            target.QuantitySold      = source.QuantitySold,
            target.TransactionCount  = source.TransactionCount,
            target.ReturnCount       = source.ReturnCount,
            target.LoadDatetime      = GETDATE()
        WHEN NOT MATCHED THEN INSERT (
            DateKey, StoreKey, ProductKey, CategoryName,
            GrossSalesAmount, NetSalesAmount, CostAmount, GrossProfitAmount,
            QuantitySold, TransactionCount, ReturnCount, LoadDatetime
        ) VALUES (
            source.DateKey, source.StoreKey, source.ProductKey, source.CategoryName,
            source.GrossSalesAmount, source.NetSalesAmount, source.CostAmount, source.GrossProfitAmount,
            source.QuantitySold, source.TransactionCount, source.ReturnCount, GETDATE()
        );

        PRINT 'DM_SalesDailySummary refreshed for ' + CAST(@BatchDate AS VARCHAR);

    END TRY
    BEGIN CATCH
        PRINT 'sp_Refresh_DM_SalesSummary error: ' + ERROR_MESSAGE();
    END CATCH
END;
GO

-- ============================================================
-- SP: sp_Refresh_DM_InventoryAlert
-- ============================================================
IF OBJECT_ID('dbo.sp_Refresh_DM_InventoryAlert', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Refresh_DM_InventoryAlert;
GO
CREATE PROCEDURE dbo.sp_Refresh_DM_InventoryAlert
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @Today DATE = CAST(GETDATE() AS DATE);

    BEGIN TRY
        -- Detect low stock alerts
        MERGE dbo.DM_InventoryAlert AS target
        USING (
            SELECT
                @Today                          AS AlertDate,
                fi.ProductKey,
                fi.StoreKey,
                CASE
                    WHEN fi.ClosingStock = 0 THEN 'HIGH'
                    WHEN fi.ClosingStock <= 5 THEN 'HIGH'
                    WHEN fi.ClosingStock <= 10 THEN 'MEDIUM'
                    ELSE 'LOW'
                END                             AS AlertLevel,
                fi.ClosingStock                AS CurrentStock,
                fi.ReorderPoint,
                CASE
                    WHEN AVG(fi2.StockSold * 1.0 / NULLIF(DATEDIFF(DAY,
                        (SELECT MIN(DateKey) FROM dbo.DimDate WHERE DateKey > fi.DateKey - 30),
                        fi.DateKey), 0)) > 0
                    THEN CAST(fi.ClosingStock / NULLIF(AVG(fi2.StockSold * 1.0 /
                        NULLIF(DATEDIFF(DAY,
                        (SELECT MIN(DateKey) FROM dbo.DimDate WHERE DateKey > fi.DateKey - 30),
                        fi.DateKey), 0)) OVER (PARTITION BY fi.ProductKey, fi.StoreKey), 0) AS DECIMAL(10,1))
                    ELSE NULL
                END                             AS DaysOfSupply,
                CASE WHEN fi.ReorderPoint IS NOT NULL AND fi.ClosingStock < fi.ReorderPoint
                     THEN fi.ReorderPoint - fi.ClosingStock + 10
                     ELSE 10
                END                             AS SuggestedOrderQty,
                NULL                            AS AvgDailySales
            FROM dbo.FactInventory fi
            WHERE fi.DateKey = CONVERT(INT, FORMAT(@Today, 'yyyyMMdd'))
              AND fi.ClosingStock < 15
        ) AS source (
            AlertDate, ProductKey, StoreKey, AlertLevel, CurrentStock,
            ReorderPoint, DaysOfSupply, SuggestedOrderQty, AvgDailySales
        )
        ON target.AlertDate = source.AlertDate
           AND target.ProductKey = source.ProductKey
           AND target.StoreKey = source.StoreKey
        WHEN MATCHED THEN UPDATE SET
            target.AlertLevel      = source.AlertLevel,
            target.CurrentStock    = source.CurrentStock,
            target.DaysOfSupply    = source.DaysOfSupply,
            target.IsAcknowledged  = 0,
            target.LoadDatetime    = GETDATE()
        WHEN NOT MATCHED THEN INSERT (
            AlertDate, ProductKey, StoreKey, AlertLevel, CurrentStock,
            ReorderPoint, DaysOfSupply, SuggestedOrderQty, AvgDailySales, IsAcknowledged, LoadDatetime
        ) VALUES (
            source.AlertDate, source.ProductKey, source.StoreKey, source.AlertLevel, source.CurrentStock,
            source.ReorderPoint, source.DaysOfSupply, source.SuggestedOrderQty, source.AvgDailySales, 0, GETDATE()
        );

        PRINT 'DM_InventoryAlert refreshed.';

    END TRY
    BEGIN CATCH
        PRINT 'sp_Refresh_DM_InventoryAlert error: ' + ERROR_MESSAGE();
    END CATCH
END;
GO

PRINT 'sp_Main_ETL and Data Mart refresh SPs created.';
GO
