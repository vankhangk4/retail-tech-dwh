-- ============================================================
-- FILE: sql/sp/usp_Transform_FactSales.sql
-- Mô tả: Transform và Load FactSales (có @TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Transform_FactSales')
BEGIN
    DROP PROCEDURE usp_Transform_FactSales;
END
GO

CREATE PROCEDURE usp_Transform_FactSales
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

        -- Ghi nhận bản ghi lỗi (không tìm thấy Dimension)
        INSERT INTO STG_ErrorLog (TenantID, SourceTable, ErrorType, RawData, ErrorMessage, LoadDatetime)
        SELECT
            @TenantID,
            'STG_SalesRaw',
            'DIMENSION_NOT_FOUND',
            CONCAT('MaSP=', s.MaSP, ', MaKH=', s.MaKH),
            'Khong tim thay ProductKey hoac StoreKey hop le',
            GETDATE()
        FROM STG_SalesRaw s
        WHERE s.TenantID = @TenantID
          AND CAST(s.NgayBan AS DATE) = @BatchDate
          AND (
              NOT EXISTS (SELECT 1 FROM DimProduct p WHERE p.ProductCode = s.MaSP AND p.IsCurrent = 1)
              OR NOT EXISTS (SELECT 1 FROM DimStore st WHERE st.StoreCode = s.MaCH AND st.TenantID = @TenantID)
          );

        -- Nạp dữ liệu hợp lệ vào FactSales
        INSERT INTO FactSales (
            TenantID, DateKey, ProductKey, CustomerKey,
            StoreKey, EmployeeKey, InvoiceNumber, Quantity,
            UnitPrice, DiscountAmount, GrossSalesAmount,
            NetSalesAmount, CostAmount, GrossProfitAmount,
            TaxAmount, PaymentMethodKey, SalesChannel,
            ReturnFlag, LoadDatetime
        )
        SELECT
            @TenantID,
            CONVERT(INT, FORMAT(s.NgayBan, 'yyyyMMdd')),
            p.ProductKey,
            ISNULL(c.CustomerKey, -1),
            st.StoreKey,
            ISNULL(e.EmployeeKey, -1),
            UPPER(LTRIM(RTRIM(s.MaHoaDon))),
            s.SoLuong,
            s.DonGiaBan,
            ISNULL(s.ChietKhau, 0),
            s.SoLuong * s.DonGiaBan,
            (s.SoLuong * s.DonGiaBan) - ISNULL(s.ChietKhau, 0),
            s.SoLuong * p.UnitCostPrice,
            (s.SoLuong * s.DonGiaBan) - ISNULL(s.ChietKhau, 0) - (s.SoLuong * p.UnitCostPrice),
            ISNULL(s.ThueVAT, 0),
            ISNULL(pm.PaymentMethodKey, 1),
            ISNULL(s.KenhBan, 'InStore'),
            ISNULL(s.IsHoanTra, 0),
            GETDATE()
        FROM STG_SalesRaw s
        INNER JOIN DimProduct p
            ON p.ProductCode = s.MaSP AND p.IsCurrent = 1
        INNER JOIN DimStore st
            ON st.StoreCode = s.MaCH AND st.TenantID = @TenantID
        LEFT JOIN DimCustomer c
            ON c.CustomerCode = s.MaKH AND c.TenantID = @TenantID
        LEFT JOIN DimEmployee e
            ON e.EmployeeCode = s.MaNV AND e.TenantID = @TenantID
        LEFT JOIN DimPaymentMethod pm
            ON pm.PaymentMethodName = s.PhuongThucTT
        WHERE s.TenantID = @TenantID
          AND CAST(s.NgayBan AS DATE) = @BatchDate
          AND NOT EXISTS (
              SELECT 1 FROM FactSales f
              WHERE f.InvoiceNumber = UPPER(LTRIM(RTRIM(s.MaHoaDon)))
                AND f.TenantID = @TenantID
                AND f.ProductKey = p.ProductKey
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

PRINT 'Created: usp_Transform_FactSales';