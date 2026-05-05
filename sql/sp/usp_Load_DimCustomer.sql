-- ============================================================
-- FILE: sql/sp/usp_Load_DimCustomer.sql
-- Mô tả: Upsert DimCustomer từ STG_CustomerRaw (theo TenantID)
-- Schema: DimCustomer(CustomerKey, CustomerID, CustomerName, Phone, Email, City, Region, CustomerType, TenantID, CreatedAt)
-- STG:   STG_CustomerRaw(CustomerID, CustomerName, Phone, Email, City, Region, CustomerType, LoadStatus, ErrorMessage, CreatedAt, TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimCustomer')
BEGIN
    DROP PROCEDURE usp_Load_DimCustomer;
END
GO

CREATE PROCEDURE usp_Load_DimCustomer
AS
BEGIN
    SET NOCOUNT ON;

    -- Upsert DimCustomer
    UPDATE dc
    SET dc.CustomerName  = stg.CustomerName,
        dc.Phone         = stg.Phone,
        dc.Email          = stg.Email,
        dc.City           = stg.City,
        dc.Region          = stg.Region,
        dc.CustomerType   = stg.CustomerType
    FROM DimCustomer dc
    INNER JOIN STG_CustomerRaw stg ON stg.CustomerID = dc.CustomerID AND stg.TenantID = dc.TenantID;

    INSERT INTO DimCustomer (CustomerID, CustomerName, Phone, Email, City, Region, CustomerType, TenantID)
    SELECT
        stg.CustomerID,
        stg.CustomerName,
        stg.Phone,
        stg.Email,
        stg.City,
        stg.Region,
        stg.CustomerType,
        stg.TenantID
    FROM STG_CustomerRaw stg
    WHERE NOT EXISTS (
        SELECT 1 FROM DimCustomer dc
        WHERE dc.CustomerID = stg.CustomerID AND dc.TenantID = stg.TenantID
    );

    PRINT 'usp_Load_DimCustomer: Done';
END;
GO
