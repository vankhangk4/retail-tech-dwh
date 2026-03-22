-- ============================================================
-- Script: 08_stored_procedures/sp_load_dim_product.sql
-- Mục đích: Load DimProduct với SCD Type 2
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_DimProduct', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_DimProduct;
GO
CREATE PROCEDURE dbo.sp_Load_DimProduct
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ProcessDate DATE = CAST(GETDATE() AS DATE);

    -- Log start
    INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, LoadDatetime)
    VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimProduct', 'RUNNING', GETDATE());

    DECLARE @RowsUpdated INT = 0;
    DECLARE @RowsInserted INT = 0;

    BEGIN TRY
        -- Bước 1: Đóng bản ghi cũ khi giá thay đổi (SCD Type 2)
        UPDATE dp
        SET    dp.ExpirationDate = DATEADD(DAY, -1, @ProcessDate),
               dp.IsCurrent       = 0
        FROM   dbo.DimProduct dp
        INNER JOIN dbo.STG_ProductRaw s ON s.MaSP = dp.ProductCode
        WHERE  dp.IsCurrent = 1
          AND  (dp.UnitCostPrice <> s.GiaVon OR dp.UnitListPrice <> s.GiaNiemYet);

        SET @RowsUpdated = @@ROWCOUNT;

        -- Bước 2: Chèn bản ghi mới (sản phẩm mới hoặc thay đổi)
        INSERT INTO dbo.DimProduct (
            ProductCode, ProductName, Brand, CategoryID, CategoryName, SubCategory,
            UnitCostPrice, UnitListPrice, UnitOfMeasure, Warranty_Months, IsActive,
            EffectiveDate, ExpirationDate, IsCurrent
        )
        SELECT
            s.MaSP,
            s.TenSP,
            s.ThuongHieu,
            NULL,
            s.DanhMuc,
            s.DanhMucCon,
            s.GiaVon,
            s.GiaNiemYet,
            s.DonViTinh,
            s.BaoHanh_Thang,
            1,
            @ProcessDate,
            NULL,
            1
        FROM dbo.STG_ProductRaw s
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.DimProduct dp
            WHERE dp.ProductCode = s.MaSP AND dp.IsCurrent = 1
        );

        SET @RowsInserted = @@ROWCOUNT;

        -- Log success
        UPDATE dbo.ETL_RunLog
        SET    Status = 'SUCCESS',
               RowsInserted = @RowsInserted,
               RowsUpdated = @RowsUpdated,
               Duration_Seconds = DATEDIFF(SECOND, LoadDatetime, GETDATE())
        WHERE  RunDate = @ProcessDate
          AND  PipelineName = 'ETL_Main'
          AND  StepName = 'sp_Load_DimProduct'
          AND  Status = 'RUNNING';

        PRINT 'sp_Load_DimProduct: ' + CAST(@RowsInserted AS VARCHAR) + ' inserted, '
            + CAST(@RowsUpdated AS VARCHAR) + ' updated.';

    END TRY
    BEGIN CATCH
        UPDATE dbo.ETL_RunLog
        SET    Status = 'FAILED',
               ErrorMessage = ERROR_MESSAGE(),
               Duration_Seconds = DATEDIFF(SECOND, LoadDatetime, GETDATE())
        WHERE  RunDate = @ProcessDate
          AND  PipelineName = 'ETL_Main'
          AND  StepName = 'sp_Load_DimProduct'
          AND  Status = 'RUNNING';

        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_DimProduct created (SCD Type 2).';
GO
