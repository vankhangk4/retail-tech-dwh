-- ============================================================
-- FILE: sql/00_run_all_schema.sql
-- Mô tả: Script chạy tất cả schema theo thứ tự
-- Chạy script này trên SQL Server để tạo toàn bộ DW
-- ============================================================

PRINT '============================================================';
PRINT 'BAT DAU TAO DATA WAREHOUSE - MULTI-TENANT';
PRINT '============================================================';

-- Thứ tự chạy rất quan trọng (Dimension trước Fact)
PRINT 'Chay: 01_create_tenants.sql';
:r sql/schema/01_create_tenants.sql

PRINT 'Chay: 02_create_dimensions.sql';
:r sql/schema/02_create_dimensions.sql

PRINT 'Chay: 03_create_facts.sql';
:r sql/schema/03_create_facts.sql

PRINT 'Chay: 04_create_staging.sql';
:r sql/schema/04_create_staging.sql

PRINT 'Chay: 05_create_datamart.sql';
:r sql/schema/05_create_datamart.sql

PRINT 'Chay: 06_create_indexes.sql';
:r sql/schema/06_create_indexes.sql

-- Stored Procedures
PRINT 'Chay SP: usp_Load_DimDate';
:r sql/sp/usp_Load_DimDate.sql

PRINT 'Chay SP: usp_Load_DimProduct';
:r sql/sp/usp_Load_DimProduct.sql

PRINT 'Chay SP: usp_Load_DimCustomer';
:r sql/sp/usp_Load_DimCustomer.sql

PRINT 'Chay SP: usp_Transform_FactSales';
:r sql/sp/usp_Transform_FactSales.sql

PRINT 'Chay SP: usp_Transform_FactInventory';
:r sql/sp/usp_Transform_FactInventory.sql

PRINT 'Chay SP: usp_Transform_FactPurchase';
:r sql/sp/usp_Transform_FactPurchase.sql

PRINT 'Chay SP: usp_Load_DimStore';
:r sql/sp/usp_Load_DimStore.sql

PRINT 'Chay SP: usp_Load_DimEmployee';
:r sql/sp/usp_Load_DimEmployee.sql

PRINT 'Chay SP: usp_Update_Watermark';
:r sql/sp/usp_Update_Watermark.sql

PRINT 'Chay SP: usp_Refresh_DM_SalesSummary';
:r sql/sp/usp_Refresh_DM_SalesSummary.sql

PRINT 'Chay SP: usp_Refresh_DM_CustomerRFM';
:r sql/sp/usp_Refresh_DM_CustomerRFM.sql

-- Views
PRINT 'Chay Views';
:r sql/views/v_FactSales_ByTenant.sql

-- Populate DimDate
PRINT 'Populate DimDate (2015-2030)...';
EXEC usp_Load_DimDate @StartDate = '2015-01-01', @EndDate = '2030-12-31';

PRINT '============================================================';
PRINT 'HOAN TAT TAO DATA WAREHOUSE - MULTI-TENANT';
PRINT '============================================================';
