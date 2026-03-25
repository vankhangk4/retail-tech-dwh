-- ============================================================
-- Script: 04_dim/dim_product.sql
-- Mục đích: Tạo DimProduct (SCD Type 2)
-- Thứ tự chạy: 5
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.DimProduct', 'U') IS NOT NULL DROP TABLE dbo.DimProduct;
CREATE TABLE dbo.DimProduct (
    ProductKey        INT IDENTITY(1,1) PRIMARY KEY,
    TenantId          VARCHAR(50)      NOT NULL,
    ProductCode       VARCHAR(50)     NOT NULL,
    ProductName       NVARCHAR(255)  NOT NULL,
    Brand             NVARCHAR(100)  NOT NULL,
    CategoryID        INT            NULL,
    CategoryName      NVARCHAR(100)  NOT NULL,
    SubCategory       NVARCHAR(100)  NULL,
    UnitCostPrice     DECIMAL(18,2)  NOT NULL,
    UnitListPrice     DECIMAL(18,2)  NOT NULL,
    UnitOfMeasure     VARCHAR(20)     NOT NULL DEFAULT N'cái',
    Warranty_Months   TINYINT        NULL,
    IsActive          BIT            NOT NULL DEFAULT 1,
    EffectiveDate     DATE           NOT NULL,
    ExpirationDate    DATE           NULL,
    IsCurrent         BIT            NOT NULL DEFAULT 1,
    LoadDatetime      DATETIME2      NOT NULL DEFAULT GETDATE(),
    CONSTRAINT UQ_DimProduct_Tenant_Code_Current UNIQUE (TenantId, ProductCode, IsCurrent)
);

CREATE INDEX IX_DimProduct_Tenant_ProductCode ON dbo.DimProduct(TenantId, ProductCode);
CREATE INDEX IX_DimProduct_IsCurrent ON dbo.DimProduct(IsCurrent);
CREATE INDEX IX_DimProduct_CategoryName ON dbo.DimProduct(CategoryName);
CREATE INDEX IX_DimProduct_Brand ON dbo.DimProduct(Brand);
GO

PRINT 'DimProduct table created (SCD Type 2).';
GO
