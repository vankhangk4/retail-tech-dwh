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

    ;WITH GroupedCustomer AS (
        SELECT
            CustomerID,
            MAX(CustomerName) AS CustomerName,
            MAX(Phone) AS Phone,
            MAX(Email) AS Email,
            MAX(City) AS City,
            MAX(Region) AS Region,
            MAX(CustomerType) AS CustomerType,
            TenantID
        FROM STG_CustomerRaw
        WHERE CustomerID IS NOT NULL AND CustomerID != ''
        GROUP BY TenantID, CustomerID
    )

    -- Upsert DimCustomer
    UPDATE dc
    SET dc.CustomerName  = stg.CustomerName,
        dc.Phone         = stg.Phone,
        dc.Email          = stg.Email,
        dc.City           = stg.City,
        dc.Region          = stg.Region,
        dc.CustomerType   = stg.CustomerType
    FROM DimCustomer dc
    INNER JOIN GroupedCustomer stg ON stg.CustomerID = dc.CustomerID AND stg.TenantID = dc.TenantID;

    ;WITH GroupedCustomer AS (
        SELECT
            CustomerID,
            MAX(CustomerName) AS CustomerName,
            MAX(Phone) AS Phone,
            MAX(Email) AS Email,
            MAX(City) AS City,
            MAX(Region) AS Region,
            MAX(CustomerType) AS CustomerType,
            TenantID
        FROM STG_CustomerRaw
        WHERE CustomerID IS NOT NULL AND CustomerID != ''
        GROUP BY TenantID, CustomerID
    )

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
    FROM GroupedCustomer stg
    WHERE NOT EXISTS (
        SELECT 1 FROM DimCustomer dc
        WHERE dc.CustomerID = stg.CustomerID AND dc.TenantID = stg.TenantID
    );

    PRINT 'usp_Load_DimCustomer: Done';
END;
GO
