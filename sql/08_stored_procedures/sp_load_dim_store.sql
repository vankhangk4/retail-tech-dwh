-- ============================================================
-- Script: 08_stored_procedures/sp_load_dim_store.sql
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_DimStore', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_DimStore;
GO
CREATE PROCEDURE dbo.sp_Load_DimStore
    @TenantId VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ProcessDate DATE = CAST(GETDATE() AS DATE);
    DECLARE @RowsInserted INT = 0;

    BEGIN TRY
        INSERT INTO dbo.DimStore (
            TenantId, StoreCode, StoreName, StoreType, Address, District, City,
            OpenDate, ManagerName, StoreArea_m2, IsActive
        )
        SELECT
            @TenantId,
            s.MaCH,
            s.TenCH,
            s.LoaiHinh,
            s.DiaChi,
            s.QuanHuyen,
            s.ThanhPho,
            s.NgayKhaiTruong,
            s.QuanLy,
            s.DienTich_m2,
            1
        FROM dbo.STG_StoreRaw s
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.DimStore ds WHERE ds.TenantId = @TenantId AND ds.StoreCode = s.MaCH
        );

        SET @RowsInserted = @@ROWCOUNT;

        UPDATE ds
        SET    ds.StoreName    = s.TenCH,
               ds.StoreType     = s.LoaiHinh,
               ds.Address       = s.DiaChi,
               ds.District      = s.QuanHuyen,
               ds.City          = s.ThanhPho,
               ds.ManagerName   = s.QuanLy,
               ds.StoreArea_m2  = s.DienTich_m2
        FROM dbo.DimStore ds
        INNER JOIN dbo.STG_StoreRaw s ON s.MaCH = ds.StoreCode
        WHERE ds.TenantId = @TenantId;

        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, RowsInserted, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimStore', 'SUCCESS', @RowsInserted, GETDATE());

        PRINT 'sp_Load_DimStore: ' + CAST(@RowsInserted AS VARCHAR) + ' inserted.';

    END TRY
    BEGIN CATCH
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, ErrorMessage, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimStore', 'FAILED', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_DimStore created.';
GO
