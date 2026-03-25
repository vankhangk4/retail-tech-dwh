-- ============================================================
-- Script: 05_fact/fact_sales.sql
-- Mục đích: Tạo FactSales (Transaction Fact)
-- Thứ tự chạy: 10
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.FactSales', 'U') IS NOT NULL DROP TABLE dbo.FactSales;
CREATE TABLE dbo.FactSales (
    SalesKey          BIGINT IDENTITY(1,1) NOT NULL,
    TenantId          VARCHAR(50)    NOT NULL,
    DateKey          INT           NOT NULL,
    ProductKey       INT           NOT NULL,
    CustomerKey      INT           NOT NULL,
    StoreKey         INT           NOT NULL,
    EmployeeKey      INT           NOT NULL,
    InvoiceNumber    VARCHAR(50)   NOT NULL,
    Quantity         SMALLINT     NOT NULL,
    UnitPrice        DECIMAL(18,2) NOT NULL,
    DiscountAmount   DECIMAL(18,2) NOT NULL DEFAULT 0,
    GrossSalesAmount DECIMAL(18,2) NOT NULL,
    NetSalesAmount   DECIMAL(18,2) NOT NULL,
    CostAmount       DECIMAL(18,2) NOT NULL,
    GrossProfitAmount DECIMAL(18,2) NOT NULL,
    TaxAmount        DECIMAL(18,2) NOT NULL DEFAULT 0,
    PaymentMethod    VARCHAR(30)   NOT NULL,
    SalesChannel     VARCHAR(20)   NOT NULL DEFAULT 'InStore',
    ReturnFlag       BIT           NOT NULL DEFAULT 0,
    LoadDatetime     DATETIME2     NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_FactSales PRIMARY KEY NONCLUSTERED (SalesKey)
);

CREATE CLUSTERED INDEX IX_FactSales_Tenant_DateKey ON dbo.FactSales(TenantId, DateKey);
CREATE NONCLUSTERED INDEX IX_FactSales_InvoiceNumber ON dbo.FactSales(InvoiceNumber);
CREATE NONCLUSTERED INDEX IX_FactSales_ProductKey ON dbo.FactSales(ProductKey);
CREATE NONCLUSTERED INDEX IX_FactSales_StoreKey ON dbo.FactSales(StoreKey);
CREATE NONCLUSTERED INDEX IX_FactSales_EmployeeKey ON dbo.FactSales(EmployeeKey);
GO

PRINT 'FactSales table created.';
GO
