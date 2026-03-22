-- ============================================================
-- Script: 04_dim/dim_employee.sql
-- Mục đích: Tạo DimEmployee
-- Thứ tự chạy: 8
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.DimEmployee', 'U') IS NOT NULL DROP TABLE dbo.DimEmployee;
CREATE TABLE dbo.DimEmployee (
    EmployeeKey       INT IDENTITY(1,1) PRIMARY KEY,
    EmployeeCode      VARCHAR(20)     NOT NULL UNIQUE,
    FullName          NVARCHAR(150)   NOT NULL,
    Department        NVARCHAR(100)  NOT NULL,
    Position          NVARCHAR(100)  NOT NULL,
    StoreKey          INT            NULL,
    HireDate          DATE           NOT NULL,
    IsActive          BIT            NOT NULL DEFAULT 1,
    LoadDatetime      DATETIME2      NOT NULL DEFAULT GETDATE()
);

CREATE INDEX IX_DimEmployee_EmployeeCode ON dbo.DimEmployee(EmployeeCode);
CREATE INDEX IX_DimEmployee_StoreKey ON dbo.DimEmployee(StoreKey);
CREATE INDEX IX_DimEmployee_Department ON dbo.DimEmployee(Department);
GO

PRINT 'DimEmployee table created.';
GO
