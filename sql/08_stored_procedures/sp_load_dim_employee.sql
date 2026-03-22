-- ============================================================
-- Script: 08_stored_procedures/sp_load_dim_employee.sql
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_DimEmployee', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_DimEmployee;
GO
CREATE PROCEDURE dbo.sp_Load_DimEmployee
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ProcessDate DATE = CAST(GETDATE() AS DATE);
    DECLARE @RowsInserted INT = 0;

    BEGIN TRY
        INSERT INTO dbo.DimEmployee (
            EmployeeCode, FullName, Department, Position, StoreKey, HireDate, IsActive
        )
        SELECT
            s.MaNV,
            s.HoTen,
            s.PhongBan,
            s.ChucVu,
            (SELECT TOP 1 ds.StoreKey FROM dbo.DimStore ds WHERE ds.StoreCode = s.MaCH),
            s.NgayVaoLam,
            1
        FROM dbo.STG_EmployeeRaw s
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.DimEmployee de WHERE de.EmployeeCode = s.MaNV
        );

        SET @RowsInserted = @@ROWCOUNT;

        UPDATE de
        SET    de.FullName   = s.HoTen,
               de.Department = s.PhongBan,
               de.Position   = s.ChucVu,
               de.StoreKey   = (SELECT TOP 1 ds.StoreKey FROM dbo.DimStore ds WHERE ds.StoreCode = s.MaCH)
        FROM dbo.DimEmployee de
        INNER JOIN dbo.STG_EmployeeRaw s ON s.MaNV = de.EmployeeCode;

        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, RowsInserted, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimEmployee', 'SUCCESS', @RowsInserted, GETDATE());

        PRINT 'sp_Load_DimEmployee: ' + CAST(@RowsInserted AS VARCHAR) + ' inserted.';

    END TRY
    BEGIN CATCH
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, ErrorMessage, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimEmployee', 'FAILED', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_DimEmployee created.';
GO
