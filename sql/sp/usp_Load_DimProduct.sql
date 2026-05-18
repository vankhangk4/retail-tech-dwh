-- ============================================================
-- FILE: sql/sp/usp_Load_DimProduct.sql
-- Mô tả: Upsert DimProduct từ STG_ProductRaw (SHARED — không cần TenantID)
-- Schema: DimProduct(ProductKey, ProductID, ProductName, Category, SubCategory, UnitPrice, UnitCost, SupplierID, IsActive, TenantID)
-- STG:   STG_ProductRaw(ProductID, ProductName, Category, SubCategory, UnitPrice, UnitCost, SupplierID, LoadStatus, ErrorMessage, CreatedAt, TenantID)
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

    ;WITH GroupedProduct AS (
        SELECT
            ProductID,
            MAX(ProductName) AS ProductName,
            MAX(Category) AS Category,
            MAX(SubCategory) AS SubCategory,
            MAX(TRY_CAST(NULLIF(UnitPrice, '') AS DECIMAL(18,2))) AS UnitPrice,
            MAX(TRY_CAST(NULLIF(UnitCost, '') AS DECIMAL(18,2))) AS UnitCost,
            MAX(SupplierID) AS SupplierID
        FROM STG_ProductRaw
        WHERE ProductID IS NOT NULL AND ProductID != ''
        GROUP BY ProductID
    )

    -- Upsert: cập nhật nếu ProductID đã tồn tại, insert nếu mới
    UPDATE dp
    SET dp.ProductName = stg.ProductName,
        dp.Category    = stg.Category,
        dp.SubCategory = stg.SubCategory,
        dp.UnitPrice   = COALESCE(stg.UnitPrice, 0),
        dp.UnitCost    = COALESCE(stg.UnitCost, 0),
        dp.SupplierID  = stg.SupplierID,
        dp.IsActive    = 1
    FROM DimProduct dp
    INNER JOIN GroupedProduct stg ON stg.ProductID = dp.ProductID;

    ;WITH GroupedProduct AS (
        SELECT
            ProductID,
            MAX(ProductName) AS ProductName,
            MAX(Category) AS Category,
            MAX(SubCategory) AS SubCategory,
            MAX(TRY_CAST(NULLIF(UnitPrice, '') AS DECIMAL(18,2))) AS UnitPrice,
            MAX(TRY_CAST(NULLIF(UnitCost, '') AS DECIMAL(18,2))) AS UnitCost,
            MAX(SupplierID) AS SupplierID
        FROM STG_ProductRaw
        WHERE ProductID IS NOT NULL AND ProductID != ''
        GROUP BY ProductID
    )

    INSERT INTO DimProduct (ProductID, ProductName, Category, SubCategory, UnitPrice, UnitCost, SupplierID, IsActive)
    SELECT
        stg.ProductID,
        stg.ProductName,
        stg.Category,
        stg.SubCategory,
        COALESCE(stg.UnitPrice, 0),
        COALESCE(stg.UnitCost, 0),
        stg.SupplierID,
        1
    FROM GroupedProduct stg
    WHERE NOT EXISTS (
        SELECT 1 FROM DimProduct dp WHERE dp.ProductID = stg.ProductID
    );

    PRINT 'usp_Load_DimProduct: Done';
END;
GO
