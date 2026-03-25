-- ============================================================
-- Script: 08_stored_procedures/sp_load_fact_purchase.sql
-- Mục đích: Load FactPurchase (sẽ được populate từ mock data)
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_FactPurchase', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_FactPurchase;
GO
CREATE PROCEDURE dbo.sp_Load_FactPurchase
    @BatchDate DATE = NULL,
    @TenantId  VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    IF @BatchDate IS NULL SET @BatchDate = CAST(GETDATE() AS DATE);
    DECLARE @ProcessDate DATE = @BatchDate;
    DECLARE @RowsLoaded INT = 0;

    BEGIN TRY
        -- FactPurchase is loaded from STG_InventoryRaw via a purchase reference
        -- For now, this SP handles a dedicated purchase staging if available
        -- The actual purchase data comes from mock data generation

        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, RowsProcessed, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_FactPurchase', 'SUCCESS', 0, GETDATE());

        PRINT 'sp_Load_FactPurchase: Completed (0 rows - use dedicated import for purchase data).';

    END TRY
    BEGIN CATCH
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, ErrorMessage, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_FactPurchase', 'FAILED', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_FactPurchase created.';
GO
