-- ============================================================
-- Script: 07_indexes/create_indexes.sql
-- Mục đích: Bổ sung indexes và constraints cho Dim/Fact tables
-- Thứ tự chạy: 14
-- ============================================================
USE DWH_RetailTech;
GO

-- ============================================================
-- Foreign Key constraints (after all tables exist)
-- ============================================================

-- FactSales FKs
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactSales_DimDate')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT FK_FactSales_DimDate
        FOREIGN KEY (DateKey) REFERENCES dbo.DimDate(DateKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactSales_DimProduct')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT FK_FactSales_DimProduct
        FOREIGN KEY (ProductKey) REFERENCES dbo.DimProduct(ProductKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactSales_DimCustomer')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT FK_FactSales_DimCustomer
        FOREIGN KEY (CustomerKey) REFERENCES dbo.DimCustomer(CustomerKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactSales_DimStore')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT FK_FactSales_DimStore
        FOREIGN KEY (StoreKey) REFERENCES dbo.DimStore(StoreKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactSales_DimEmployee')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT FK_FactSales_DimEmployee
        FOREIGN KEY (EmployeeKey) REFERENCES dbo.DimEmployee(EmployeeKey);

-- FactInventory FKs
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactInventory_DimDate')
    ALTER TABLE dbo.FactInventory ADD CONSTRAINT FK_FactInventory_DimDate
        FOREIGN KEY (DateKey) REFERENCES dbo.DimDate(DateKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactInventory_DimProduct')
    ALTER TABLE dbo.FactInventory ADD CONSTRAINT FK_FactInventory_DimProduct
        FOREIGN KEY (ProductKey) REFERENCES dbo.DimProduct(ProductKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactInventory_DimStore')
    ALTER TABLE dbo.FactInventory ADD CONSTRAINT FK_FactInventory_DimStore
        FOREIGN KEY (StoreKey) REFERENCES dbo.DimStore(StoreKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactInventory_DimSupplier')
    ALTER TABLE dbo.FactInventory ADD CONSTRAINT FK_FactInventory_DimSupplier
        FOREIGN KEY (SupplierKey) REFERENCES dbo.DimSupplier(SupplierKey);

-- FactPurchase FKs
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactPurchase_DimDate')
    ALTER TABLE dbo.FactPurchase ADD CONSTRAINT FK_FactPurchase_DimDate
        FOREIGN KEY (DateKey) REFERENCES dbo.DimDate(DateKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactPurchase_DimProduct')
    ALTER TABLE dbo.FactPurchase ADD CONSTRAINT FK_FactPurchase_DimProduct
        FOREIGN KEY (ProductKey) REFERENCES dbo.DimProduct(ProductKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactPurchase_DimSupplier')
    ALTER TABLE dbo.FactPurchase ADD CONSTRAINT FK_FactPurchase_DimSupplier
        FOREIGN KEY (SupplierKey) REFERENCES dbo.DimSupplier(SupplierKey);
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_FactPurchase_DimStore')
    ALTER TABLE dbo.FactPurchase ADD CONSTRAINT FK_FactPurchase_DimStore
        FOREIGN KEY (StoreKey) REFERENCES dbo.DimStore(StoreKey);

-- DimEmployee FK
IF NOT EXISTS (SELECT * FROM sys.foreign_keys WHERE name = 'FK_DimEmployee_DimStore')
    ALTER TABLE dbo.DimEmployee ADD CONSTRAINT FK_DimEmployee_DimStore
        FOREIGN KEY (StoreKey) REFERENCES dbo.DimStore(StoreKey);

PRINT 'All foreign key constraints created successfully.';
GO

-- ============================================================
-- Additional covering indexes for BI queries
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.FactSales') AND name = 'IX_FactSales_DateStoreCategory')
    CREATE NONCLUSTERED INDEX IX_FactSales_DateStoreCategory
        ON dbo.FactSales(DateKey, StoreKey)
        INCLUDE (NetSalesAmount, GrossProfitAmount, Quantity);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.FactSales') AND name = 'IX_FactSales_ProductDate')
    CREATE NONCLUSTERED INDEX IX_FactSales_ProductDate
        ON dbo.FactSales(ProductKey, DateKey)
        INCLUDE (NetSalesAmount, GrossProfitAmount, Quantity);

-- Covering index for stats aggregation queries (GrossSalesAmount)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.FactSales') AND name = 'IX_FactSales_DateKey_GrossSales')
    CREATE NONCLUSTERED INDEX IX_FactSales_DateKey_GrossSales
        ON dbo.FactSales(DateKey)
        INCLUDE (GrossSalesAmount, NetSalesAmount, Quantity);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.FactSales') AND name = 'IX_FactSales_StoreKey_GrossSales')
    CREATE NONCLUSTERED INDEX IX_FactSales_StoreKey_GrossSales
        ON dbo.FactSales(StoreKey)
        INCLUDE (GrossSalesAmount);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.FactInventory') AND name = 'IX_FactInventory_DateClosingStock')
    CREATE NONCLUSTERED INDEX IX_FactInventory_DateClosingStock
        ON dbo.FactInventory(DateKey, ClosingStock)
        INCLUDE (TotalInventoryValue);

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('dbo.DimDate') AND name = 'IX_DimDate_YearMonth')
    CREATE NONCLUSTERED INDEX IX_DimDate_YearMonth ON dbo.DimDate(Year, MonthNumber);

PRINT 'Additional covering indexes created.';
GO

-- ============================================================
-- Check constraints for data quality
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CK_FactSales_Quantity')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT CK_FactSales_Quantity CHECK (Quantity > 0);

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CK_FactSales_Amounts')
    ALTER TABLE dbo.FactSales ADD CONSTRAINT CK_FactSales_Amounts CHECK (GrossSalesAmount >= 0 AND NetSalesAmount >= 0);

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE name = 'CK_FactInventory_Stock')
    ALTER TABLE dbo.FactInventory ADD CONSTRAINT CK_FactInventory_Stock CHECK (ClosingStock >= 0);

PRINT 'Check constraints created.';
PRINT 'All indexes and constraints created successfully.';
GO
