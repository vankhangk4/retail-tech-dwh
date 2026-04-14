-- ============================================================
-- FILE: sql/sp/usp_Load_DimProduct.sql
-- Mô tả: SCD Type 2 cho DimProduct (Shared — không cần TenantID)
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

    -- Bước 1: Đóng bản ghi cũ khi giá thay đổi (SCD Type 2)
    UPDATE dp
    SET dp.ExpirationDate = DATEADD(DAY, -1, CAST(GETDATE() AS DATE)),
        dp.IsCurrent = 0
    FROM DimProduct dp
    INNER JOIN STG_ProductRaw s
        ON s.MaSP = dp.ProductCode
    WHERE dp.IsCurrent = 1
      AND (dp.UnitCostPrice <> s.GiaVon
       OR dp.UnitListPrice <> s.GiaNiemYet);

    -- Bước 2: Chèn bản ghi mới (sản phẩm mới hoặc giá thay đổi)
    INSERT INTO DimProduct (
        ProductCode, ProductName, Brand, CategoryName,
        SubCategory, UnitCostPrice, UnitListPrice,
        UnitOfMeasure, Warranty_Months, IsActive,
        EffectiveDate, ExpirationDate, IsCurrent
    )
    SELECT
        s.MaSP,
        s.TenSP,
        s.ThuongHieu,
        s.DanhMuc,
        s.DanhMucCon,
        s.GiaVon,
        s.GiaNiemYet,
        ISNULL(s.DonViTinh, N'cái'),
        s.BaoHanh_Thang,
        1,
        CAST(GETDATE() AS DATE),
        NULL,
        1
    FROM STG_ProductRaw s
    WHERE NOT EXISTS (
        SELECT 1 FROM DimProduct dp
        WHERE dp.ProductCode = s.MaSP AND dp.IsCurrent = 1
    );
END;
GO

PRINT 'Created: usp_Load_DimProduct';