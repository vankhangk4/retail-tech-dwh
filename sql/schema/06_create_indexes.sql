-- ============================================================
-- FILE: sql/schema/06_create_indexes.sql
-- Mô tả: Tạo Indexes (SQL Server không hỗ trợ CREATE INDEX IF NOT EXISTS)
-- ============================================================

-- Index cho STG tables
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ETLLogs_Tenant_Date')
BEGIN CREATE INDEX IX_ETLLogs_Tenant_Date ON ETLLogs(TenantID, BatchDate); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ETLLogs_Status')
BEGIN CREATE INDEX IX_ETLLogs_Status ON ETLLogs(RunStatus, StartTime); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ETL_Watermark_Tenant')
BEGIN CREATE INDEX IX_ETL_Watermark_Tenant ON ETL_Watermark(TenantID, TableName); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_STG_Sales_Tenant')
BEGIN CREATE INDEX IX_STG_Sales_Tenant ON STG_SalesRaw(TenantID, NgayBan); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_STG_Inv_Tenant')
BEGIN CREATE INDEX IX_STG_Inv_Tenant ON STG_InventoryRaw(TenantID, NgayChupAnh); END

-- Index cho DM layer
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_Sales_Tenant_Date')
BEGIN CREATE INDEX IX_DM_Sales_Tenant_Date ON DM_SalesSummary(TenantID, DateKey); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_Sales_Store')
BEGIN CREATE INDEX IX_DM_Sales_Store ON DM_SalesSummary(TenantID, StoreKey, DateKey); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_CustRFM_Tenant')
BEGIN CREATE INDEX IX_DM_CustRFM_Tenant ON DM_CustomerRFM(TenantID, Segment); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_CustRFM_Customer')
BEGIN CREATE INDEX IX_DM_CustRFM_Customer ON DM_CustomerRFM(TenantID, CustomerKey); END

-- Unique Index SCD2 cho DimProduct và DimCustomer
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_DimProduct_Current')
BEGIN CREATE UNIQUE INDEX UQ_DimProduct_Current ON DimProduct(ProductCode) WHERE IsCurrent = 1; END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'UQ_DimCustomer_Current')
BEGIN CREATE UNIQUE INDEX UQ_DimCustomer_Current ON DimCustomer(TenantID, CustomerCode) WHERE IsCurrent = 1; END

-- Index cho Fact tables (trong schema 03 — copy nếu cần)
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FactSales_TenantID')
BEGIN CREATE INDEX IX_FactSales_TenantID ON FactSales(TenantID, DateKey); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FactInventory_TenantID')
BEGIN CREATE INDEX IX_FactInventory_TenantID ON FactInventory(TenantID, DateKey); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_FactPurchase_TenantID')
BEGIN CREATE INDEX IX_FactPurchase_TenantID ON FactPurchase(TenantID, DateKey); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DimProduct_ProductCode')
BEGIN CREATE INDEX IX_DimProduct_ProductCode ON DimProduct(ProductCode) WHERE IsCurrent = 1; END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DimCustomer_TenantCode')
BEGIN CREATE INDEX IX_DimCustomer_TenantCode ON DimCustomer(TenantID, CustomerCode) WHERE IsCurrent = 1; END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DimEmployee_TenantCode')
BEGIN CREATE INDEX IX_DimEmployee_TenantCode ON DimEmployee(TenantID, EmployeeCode); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DimStore_TenantCode')
BEGIN CREATE INDEX IX_DimStore_TenantCode ON DimStore(TenantID, StoreCode); END
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DimSupplier_Code')
BEGIN CREATE INDEX IX_DimSupplier_Code ON DimSupplier(SupplierCode); END

PRINT 'Done: 06_create_indexes.sql';
