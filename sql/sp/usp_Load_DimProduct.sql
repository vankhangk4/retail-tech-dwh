-- ============================================================
-- FILE: sql/sp/usp_Load_DimProduct.sql
-- Mô tả: Upsert DimProduct từ STG_ProductRaw (SHARED — không cần TenantID)
-- Schema: DimProduct(ProductKey, ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, IsActive, TenantID)
-- STG:   STG_ProductRaw(ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, LoadStatus, ErrorMessage, CreatedAt, TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimProduct')
BEGIN
    DROP PROCEDURE usp_Load_DimProduct;
END
GO

CREATE PROCEDURE usp_Load_DimProduct
AS
BEGIN
    SET NOCOUNT ON;

    -- Upsert: cập nhật nếu ProductID đã tồn tại, insert nếu mới
    UPDATE dp
    SET dp.ProductName = stg.ProductName,
        dp.Category    = stg.Category,
        dp.SubCategory = stg.SubCategory,
        dp.UnitPrice  = CAST(stg.UnitPrice AS DECIMAL(18,2)),
        dp.SupplierID  = stg.SupplierID,
        dp.IsActive    = 1
    FROM DimProduct dp
    INNER JOIN STG_ProductRaw stg ON stg.ProductID = dp.ProductID;

    INSERT INTO DimProduct (ProductID, ProductName, Category, SubCategory, UnitPrice, SupplierID, IsActive)
    SELECT
        stg.ProductID,
        stg.ProductName,
        stg.Category,
        stg.SubCategory,
        CAST(stg.UnitPrice AS DECIMAL(18,2)),
        stg.SupplierID,
        1
    FROM STG_ProductRaw stg
    WHERE NOT EXISTS (
        SELECT 1 FROM DimProduct dp WHERE dp.ProductID = stg.ProductID
    );

    PRINT 'usp_Load_DimProduct: Done';
END;
GO
