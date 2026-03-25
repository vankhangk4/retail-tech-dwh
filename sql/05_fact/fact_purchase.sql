-- ============================================================
-- Script: 05_fact/fact_purchase.sql
-- Mục đích: Tạo FactPurchase (Transaction Fact)
-- Thứ tự chạy: 12
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.FactPurchase', 'U') IS NOT NULL DROP TABLE dbo.FactPurchase;
CREATE TABLE dbo.FactPurchase (
    PurchaseKey         BIGINT IDENTITY(1,1) NOT NULL,
    TenantId            VARCHAR(50)    NOT NULL,
    DateKey            INT           NOT NULL,
    ProductKey         INT           NOT NULL,
    SupplierKey        INT           NOT NULL,
    StoreKey           INT           NOT NULL,
    PurchaseOrderNo     VARCHAR(50)   NOT NULL,
    QuantityOrdered     INT           NOT NULL,
    QuantityReceived    INT           NOT NULL,
    UnitPurchasePrice  DECIMAL(18,2) NOT NULL,
    TotalPurchaseAmount DECIMAL(18,2) NOT NULL,
    LeadTime_Days      SMALLINT       NULL,
    LoadDatetime       DATETIME2      NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_FactPurchase PRIMARY KEY NONCLUSTERED (PurchaseKey)
);

CREATE CLUSTERED INDEX IX_FactPurchase_Tenant_DateKey ON dbo.FactPurchase(TenantId, DateKey);
CREATE NONCLUSTERED INDEX IX_FactPurchase_ProductKey ON dbo.FactPurchase(ProductKey);
CREATE NONCLUSTERED INDEX IX_FactPurchase_SupplierKey ON dbo.FactPurchase(SupplierKey);
CREATE NONCLUSTERED INDEX IX_FactPurchase_StoreKey ON dbo.FactPurchase(StoreKey);
GO

PRINT 'FactPurchase table created.';
GO
