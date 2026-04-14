-- ============================================================
-- FILE: sql/sp/usp_Transform_FactPurchase.sql
-- Mô tả: Transform và Load FactPurchase (có @TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Transform_FactPurchase')
BEGIN
    DROP PROCEDURE usp_Transform_FactPurchase;
END
GO

CREATE PROCEDURE usp_Transform_FactPurchase
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

        INSERT INTO FactPurchase (
            TenantID, DateKey, ProductKey, SupplierKey, StoreKey,
            PurchaseOrderNo, QuantityOrdered, QuantityReceived,
            UnitPurchasePrice, TotalPurchaseAmount, LoadDatetime
        )
        SELECT
            @TenantID,
            CONVERT(INT, FORMAT(pur.NgayDat, 'yyyyMMdd')),
            prod.ProductKey,
            sup.SupplierKey,
            st.StoreKey,
            UPPER(LTRIM(RTRIM(pur.SoPhieuDat))),
            ISNULL(pur.SoLuongDat, 0),
            ISNULL(pur.SoLuongNhan, 0),
            ISNULL(pur.DonGiaNhap, 0),
            ISNULL(pur.SoLuongNhan, 0) * ISNULL(pur.DonGiaNhap, 0),
            GETDATE()
        FROM STG_PurchaseRaw pur
        INNER JOIN DimProduct prod ON prod.ProductCode = pur.MaSP AND prod.IsCurrent = 1
        INNER JOIN DimSupplier sup ON sup.SupplierCode = pur.MaNCC
        INNER JOIN DimStore st ON st.StoreCode = pur.MaCH AND st.TenantID = @TenantID
        WHERE pur.TenantID = @TenantID
          AND pur.NgayDat = @BatchDate
          AND NOT EXISTS (
              SELECT 1 FROM FactPurchase f
              WHERE f.TenantID = @TenantID
                AND f.PurchaseOrderNo = UPPER(LTRIM(RTRIM(pur.SoPhieuDat)))
                AND f.ProductKey = prod.ProductKey
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

PRINT 'Created: usp_Transform_FactPurchase';