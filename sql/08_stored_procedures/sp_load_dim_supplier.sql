-- ============================================================
-- Script: 08_stored_procedures/sp_load_dim_supplier.sql
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_DimSupplier', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_DimSupplier;
GO
CREATE PROCEDURE dbo.sp_Load_DimSupplier
    @TenantId VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ProcessDate DATE = CAST(GETDATE() AS DATE);
    DECLARE @RowsInserted INT = 0;

    BEGIN TRY
        INSERT INTO dbo.DimSupplier (
            TenantId, SupplierCode, SupplierName, Country, ContactPerson, Phone, Email,
            PaymentTerm_Days, IsActive
        )
        SELECT
            @TenantId,
            s.MaNCC,
            s.TenNCC,
            s.QuocGia,
            s.NguoiLienHe,
            s.DienThoai,
            s.Email,
            s.DieuKhoanTT_Ngay,
            1
        FROM dbo.STG_SupplierRaw s
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.DimSupplier ds WHERE ds.TenantId = @TenantId AND ds.SupplierCode = s.MaNCC
        );

        SET @RowsInserted = @@ROWCOUNT;

        UPDATE ds
        SET    ds.SupplierName    = s.TenNCC,
               ds.Country         = s.QuocGia,
               ds.ContactPerson   = s.NguoiLienHe,
               ds.Phone           = s.DienThoai,
               ds.Email           = s.Email,
               ds.PaymentTerm_Days = s.DieuKhoanTT_Ngay
        FROM dbo.DimSupplier ds
        INNER JOIN dbo.STG_SupplierRaw s ON s.MaNCC = ds.SupplierCode
        WHERE ds.TenantId = @TenantId;

        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, RowsInserted, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimSupplier', 'SUCCESS', @RowsInserted, GETDATE());

        PRINT 'sp_Load_DimSupplier: ' + CAST(@RowsInserted AS VARCHAR) + ' inserted.';

    END TRY
    BEGIN CATCH
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, ErrorMessage, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimSupplier', 'FAILED', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_DimSupplier created.';
GO
