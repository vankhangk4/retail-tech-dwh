-- ============================================================
-- Script: 04_dim/dim_supplier.sql
-- Mục đích: Tạo DimSupplier
-- Thứ tự chạy: 9
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.DimSupplier', 'U') IS NOT NULL DROP TABLE dbo.DimSupplier;
CREATE TABLE dbo.DimSupplier (
    SupplierKey        INT IDENTITY(1,1) PRIMARY KEY,
    TenantId          VARCHAR(50)      NOT NULL,
    SupplierCode      VARCHAR(50)     NOT NULL,
    SupplierName     NVARCHAR(200)   NOT NULL,
    Country           NVARCHAR(100)   NOT NULL,
    ContactPerson     NVARCHAR(150)   NULL,
    Phone             VARCHAR(30)     NULL,
    Email             VARCHAR(150)    NULL,
    PaymentTerm_Days  TINYINT         NULL,
    IsActive          BIT             NOT NULL DEFAULT 1,
    LoadDatetime      DATETIME2       NOT NULL DEFAULT GETDATE()
);

CREATE UNIQUE INDEX UQ_DimSupplier_Tenant_SupplierCode ON dbo.DimSupplier(TenantId, SupplierCode);
CREATE INDEX IX_DimSupplier_Country ON dbo.DimSupplier(Country);
GO

PRINT 'DimSupplier table created.';
GO
