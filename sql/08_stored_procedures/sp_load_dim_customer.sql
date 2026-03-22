-- ============================================================
-- Script: 08_stored_procedures/sp_load_dim_customer.sql
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_DimCustomer', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_DimCustomer;
GO
CREATE PROCEDURE dbo.sp_Load_DimCustomer
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @ProcessDate DATE = CAST(GETDATE() AS DATE);
    DECLARE @RowsInserted INT = 0;

    BEGIN TRY
        -- Insert new customers (no SCD - simple overwrite for non-key attributes)
        INSERT INTO dbo.DimCustomer (
            CustomerCode, FullName, Gender, DateOfBirth, AgeGroup,
            Phone, Email, City, Province, CustomerType,
            LoyaltyPoint, MemberSince, IsActive
        )
        SELECT
            s.MaKH,
            s.HoTen,
            s.GioiTinh,
            s.NgaySinh,
            CASE
                WHEN s.NgaySinh IS NOT NULL THEN
                    CASE
                        WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) < 18 THEN '0-17'
                        WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 18 AND 24 THEN '18-24'
                        WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 25 AND 34 THEN '25-34'
                        WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 35 AND 44 THEN '35-44'
                        WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 45 AND 54 THEN '45-54'
                        ELSE '55+'
                    END
                ELSE NULL
            END,
            s.DienThoai,
            s.Email,
            s.ThanhPho,
            NULL,
            ISNULL(s.LoaiKH, N'Lẻ'),
            ISNULL(s.DiemTichLuy, 0),
            s.NgayDangKy,
            1
        FROM dbo.STG_CustomerRaw s
        WHERE NOT EXISTS (
            SELECT 1 FROM dbo.DimCustomer dc WHERE dc.CustomerCode = s.MaKH
        );

        SET @RowsInserted = @@ROWCOUNT;

        -- Update existing customers
        UPDATE dc
        SET    dc.FullName       = s.HoTen,
               dc.Gender         = s.GioiTinh,
               dc.DateOfBirth    = s.NgaySinh,
               dc.AgeGroup       = CASE
                   WHEN s.NgaySinh IS NOT NULL THEN
                       CASE
                           WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) < 18 THEN '0-17'
                           WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 18 AND 24 THEN '18-24'
                           WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 25 AND 34 THEN '25-34'
                           WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 35 AND 44 THEN '35-44'
                           WHEN DATEDIFF(YEAR, s.NgaySinh, GETDATE()) BETWEEN 45 AND 54 THEN '45-54'
                           ELSE '55+'
                       END
                   ELSE dc.AgeGroup
               END,
               dc.Phone          = s.DienThoai,
               dc.Email          = s.Email,
               dc.City           = s.ThanhPho,
               dc.CustomerType   = ISNULL(s.LoaiKH, dc.CustomerType),
               dc.LoyaltyPoint   = ISNULL(s.DiemTichLuy, dc.LoyaltyPoint)
        FROM dbo.DimCustomer dc
        INNER JOIN dbo.STG_CustomerRaw s ON s.MaKH = dc.CustomerCode;

        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, RowsInserted, Duration_Seconds, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimCustomer', 'SUCCESS',
                @RowsInserted, 0, GETDATE());

        PRINT 'sp_Load_DimCustomer: ' + CAST(@RowsInserted AS VARCHAR) + ' inserted.';

    END TRY
    BEGIN CATCH
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, ErrorMessage, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_DimCustomer', 'FAILED', ERROR_MESSAGE(), GETDATE());
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_DimCustomer created.';
GO
