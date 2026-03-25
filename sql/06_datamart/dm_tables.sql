-- ============================================================
-- Script: 06_datamart/dm_tables.sql
-- Mục đích: Tạo Data Mart tables (DM_*)
-- Thứ tự chạy: 13
-- ============================================================
USE DWH_RetailTech;
GO

-- ============================================================
-- DM_SalesDailySummary: Aggregate table cho báo cáo doanh thu
-- ============================================================
IF OBJECT_ID('dbo.DM_SalesDailySummary', 'U') IS NOT NULL DROP TABLE dbo.DM_SalesDailySummary;
CREATE TABLE dbo.DM_SalesDailySummary (
    SummaryID           BIGINT IDENTITY(1,1) PRIMARY KEY,
    TenantId           VARCHAR(50)   NOT NULL,
    DateKey            INT           NOT NULL,
    StoreKey           INT           NULL,
    ProductKey         INT           NULL,
    CategoryName       NVARCHAR(100) NULL,
    GrossSalesAmount   DECIMAL(18,2) NOT NULL DEFAULT 0,
    NetSalesAmount     DECIMAL(18,2) NOT NULL DEFAULT 0,
    CostAmount         DECIMAL(18,2) NOT NULL DEFAULT 0,
    GrossProfitAmount   DECIMAL(18,2) NOT NULL DEFAULT 0,
    QuantitySold       INT           NOT NULL DEFAULT 0,
    TransactionCount   INT           NOT NULL DEFAULT 0,
    ReturnCount        INT           NOT NULL DEFAULT 0,
    LoadDatetime       DATETIME2     NOT NULL DEFAULT GETDATE(),
    CONSTRAINT UQ_DM_SalesDailySummary UNIQUE (TenantId, DateKey, StoreKey, ProductKey)
);

CREATE NONCLUSTERED INDEX IX_DM_SalesDailySummary_Tenant_StoreKey ON dbo.DM_SalesDailySummary(TenantId, StoreKey);
GO

-- ============================================================
-- DM_InventoryAlert: Cảnh báo tồn kho
-- ============================================================
IF OBJECT_ID('dbo.DM_InventoryAlert', 'U') IS NOT NULL DROP TABLE dbo.DM_InventoryAlert;
CREATE TABLE dbo.DM_InventoryAlert (
    AlertID            BIGINT IDENTITY(1,1) PRIMARY KEY,
    TenantId           VARCHAR(50)    NOT NULL,
    AlertDate          DATE           NOT NULL,
    ProductKey         INT           NOT NULL,
    StoreKey           INT           NOT NULL,
    AlertLevel         VARCHAR(10)   NOT NULL,  -- LOW, MEDIUM, HIGH
    CurrentStock       INT           NOT NULL,
    ReorderPoint       INT           NULL,
    DaysOfSupply       DECIMAL(10,1) NULL,
    SuggestedOrderQty  INT           NULL,
    AvgDailySales      DECIMAL(10,2) NULL,
    IsAcknowledged     BIT           NOT NULL DEFAULT 0,
    LoadDatetime       DATETIME2     NOT NULL DEFAULT GETDATE(),
    CONSTRAINT UQ_DM_InventoryAlert UNIQUE (TenantId, AlertDate, ProductKey, StoreKey)
);

CREATE NONCLUSTERED INDEX IX_DM_InventoryAlert_Tenant_AlertLevel ON dbo.DM_InventoryAlert(TenantId, AlertLevel);
CREATE NONCLUSTERED INDEX IX_DM_InventoryAlert_IsAcknowledged ON dbo.DM_InventoryAlert(IsAcknowledged);
GO

PRINT 'Data Mart tables (DM_SalesDailySummary, DM_InventoryAlert) created.';
GO
