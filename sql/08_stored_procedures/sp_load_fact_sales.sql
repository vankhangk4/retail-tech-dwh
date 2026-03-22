-- ============================================================
-- Script: 08_stored_procedures/sp_load_fact_sales.sql
-- Mục đích: Load FactSales
-- Fix: Thêm @FullLoad để load tất cả ngày khi --full
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.sp_Load_FactSales', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Load_FactSales;
GO
CREATE PROCEDURE dbo.sp_Load_FactSales
    @BatchDate DATE = NULL,
    @FullLoad  BIT = 0
AS
BEGIN
    SET NOCOUNT ON;
    IF @BatchDate IS NULL SET @BatchDate = CAST(GETDATE() AS DATE);
    DECLARE @ProcessDate DATE = @BatchDate;

    DECLARE @RowsLoaded INT = 0;

    BEGIN TRY
        -- Log start
        DECLARE @RunLogID BIGINT;
        INSERT INTO dbo.ETL_RunLog (RunDate, PipelineName, StepName, Status, LoadDatetime)
        VALUES (@ProcessDate, 'ETL_Main', 'sp_Load_FactSales', 'RUNNING', GETDATE());
        SET @RunLogID = SCOPE_IDENTITY();

        -- Step 1: Log missing dimensions
        INSERT INTO dbo.STG_ErrorLog (SourceTable, ErrorType, RawData, BatchDate, LoadDatetime)
        SELECT TOP 100
            'STG_SalesRaw',
            'DIMENSION_NOT_FOUND',
            CONCAT('MaSP=', s.MaSP, ', MaKH=', s.MaKH, ', MaCH=', s.MaCH, ', MaNV=', s.MaNV),
            @ProcessDate,
            GETDATE()
        FROM dbo.STG_SalesRaw s
        WHERE (@FullLoad = 1 OR CAST(s.NgayBan AS DATE) = @ProcessDate)
          AND NOT EXISTS (
              SELECT 1 FROM dbo.DimProduct p
              WHERE p.ProductCode = s.MaSP AND p.IsCurrent = 1
          );

        -- Step 2: Log missing stores
        INSERT INTO dbo.STG_ErrorLog (SourceTable, ErrorType, RawData, BatchDate, LoadDatetime)
        SELECT TOP 50
            'STG_SalesRaw',
            'STORE_NOT_FOUND',
            CONCAT('MaCH=', s.MaCH),
            @ProcessDate,
            GETDATE()
        FROM dbo.STG_SalesRaw s
        WHERE (@FullLoad = 1 OR CAST(s.NgayBan AS DATE) = @ProcessDate)
          AND NOT EXISTS (SELECT 1 FROM dbo.DimStore st WHERE st.StoreCode = s.MaCH);

        -- Step 3: Load FactSales (idempotent - skip if exists)
        INSERT INTO dbo.FactSales (
            DateKey, ProductKey, CustomerKey, StoreKey, EmployeeKey,
            InvoiceNumber, Quantity, UnitPrice, DiscountAmount,
            GrossSalesAmount, NetSalesAmount, CostAmount, GrossProfitAmount,
            TaxAmount, PaymentMethod, SalesChannel, ReturnFlag, LoadDatetime
        )
        SELECT
            CONVERT(INT, FORMAT(s.NgayBan, 'yyyyMMdd'))          AS DateKey,
            ISNULL(p.ProductKey, -1)                              AS ProductKey,
            ISNULL(c.CustomerKey, -1)                            AS CustomerKey,
            st.StoreKey,
            ISNULL(e.EmployeeKey, -1)                            AS EmployeeKey,
            UPPER(LTRIM(RTRIM(s.MaHoaDon)))                     AS InvoiceNumber,
            s.SoLuong                                            AS Quantity,
            s.DonGiaBan                                          AS UnitPrice,
            ISNULL(s.ChietKhau, 0)                              AS DiscountAmount,
            s.SoLuong * s.DonGiaBan                             AS GrossSalesAmount,
            (s.SoLuong * s.DonGiaBan) - ISNULL(s.ChietKhau, 0) AS NetSalesAmount,
            s.SoLuong * ISNULL(p.UnitCostPrice, 0)             AS CostAmount,
            ((s.SoLuong * s.DonGiaBan) - ISNULL(s.ChietKhau, 0))
                - (s.SoLuong * ISNULL(p.UnitCostPrice, 0))     AS GrossProfitAmount,
            ISNULL(s.ThueSuat, 0.10) * (s.SoLuong * s.DonGiaBan) AS TaxAmount,
            ISNULL(s.PhuongThucTT, N'Tiền mặt')                AS PaymentMethod,
            ISNULL(s.KenhBan, 'InStore')                         AS SalesChannel,
            ISNULL(s.IsHoanTra, 0)                               AS ReturnFlag,
            GETDATE()                                            AS LoadDatetime
        FROM dbo.STG_SalesRaw s
        INNER JOIN dbo.DimStore st ON st.StoreCode = s.MaCH
        LEFT  JOIN dbo.DimProduct p  ON p.ProductCode  = s.MaSP  AND p.IsCurrent = 1
        LEFT  JOIN dbo.DimCustomer c ON c.CustomerCode = s.MaKH
        LEFT  JOIN dbo.DimEmployee e ON e.EmployeeCode = s.MaNV
        WHERE (@FullLoad = 1 OR CAST(s.NgayBan AS DATE) = @ProcessDate)
          AND NOT EXISTS (
              SELECT 1 FROM dbo.FactSales f
              WHERE f.InvoiceNumber = UPPER(LTRIM(RTRIM(s.MaHoaDon)))
                AND f.ProductKey = ISNULL(p.ProductKey, -1)
          );

        SET @RowsLoaded = @@ROWCOUNT;

        -- Log success
        UPDATE dbo.ETL_RunLog
        SET    Status = 'SUCCESS',
               RowsProcessed = @RowsLoaded,
               RowsInserted  = @RowsLoaded,
               Duration_Seconds = DATEDIFF(SECOND, LoadDatetime, GETDATE())
        WHERE  RunLogID = @RunLogID;

        PRINT 'sp_Load_FactSales: ' + CAST(@RowsLoaded AS VARCHAR)
            + ' rows loaded (BatchDate=' + CAST(@ProcessDate AS VARCHAR)
            + ', FullLoad=' + CAST(@FullLoad AS VARCHAR) + ')';

    END TRY
    BEGIN CATCH
        UPDATE dbo.ETL_RunLog
        SET    Status = 'FAILED',
               ErrorMessage = ERROR_MESSAGE()
        WHERE  RunDate = @ProcessDate
          AND  PipelineName = 'ETL_Main'
          AND  StepName = 'sp_Load_FactSales'
          AND  Status = 'RUNNING';
        THROW;
    END CATCH
END;
GO

PRINT 'sp_Load_FactSales created.';
GO
