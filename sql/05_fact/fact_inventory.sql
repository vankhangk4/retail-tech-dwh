-- ============================================================
-- Script: 05_fact/fact_inventory.sql
-- Mục đích: Tạo FactInventory (Periodic Snapshot Fact)
-- Thứ tự chạy: 11
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.FactInventory', 'U') IS NOT NULL DROP TABLE dbo.FactInventory;
CREATE TABLE dbo.FactInventory (
    InventoryKey        BIGINT IDENTITY(1,1) NOT NULL,
    DateKey            INT           NOT NULL,
    ProductKey         INT           NOT NULL,
    StoreKey           INT           NOT NULL,
    SupplierKey        INT           NULL,
    OpeningStock       INT           NOT NULL DEFAULT 0,
    ClosingStock       INT           NOT NULL DEFAULT 0,
    StockReceived      INT           NOT NULL DEFAULT 0,
    StockSold          INT           NOT NULL DEFAULT 0,
    StockAdjusted      INT           NOT NULL DEFAULT 0,
    ReorderPoint       INT           NULL,
    UnitCost           DECIMAL(18,2) NOT NULL,
    TotalInventoryValue DECIMAL(18,2) NOT NULL,
    LoadDatetime       DATETIME2      NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_FactInventory PRIMARY KEY NONCLUSTERED (InventoryKey)
);

CREATE CLUSTERED INDEX IX_FactInventory_DateKey ON dbo.FactInventory(DateKey);
CREATE NONCLUSTERED INDEX IX_FactInventory_ProductKey ON dbo.FactInventory(ProductKey);
CREATE NONCLUSTERED INDEX IX_FactInventory_StoreKey ON dbo.FactInventory(StoreKey);
CREATE NONCLUSTERED INDEX IX_FactInventory_ProductStoreDate ON dbo.FactInventory(ProductKey, StoreKey, DateKey);
GO

PRINT 'FactInventory table created.';
GO
