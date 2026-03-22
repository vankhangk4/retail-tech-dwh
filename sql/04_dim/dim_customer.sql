-- ============================================================
-- Script: 04_dim/dim_customer.sql
-- Mục đích: Tạo DimCustomer
-- Thứ tự chạy: 6
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.DimCustomer', 'U') IS NOT NULL DROP TABLE dbo.DimCustomer;
CREATE TABLE dbo.DimCustomer (
    CustomerKey       INT IDENTITY(1,1) PRIMARY KEY,
    CustomerCode      VARCHAR(50)     NOT NULL UNIQUE,
    FullName          NVARCHAR(150)   NOT NULL,
    Gender            CHAR(1)         NULL,
    DateOfBirth       DATE            NULL,
    AgeGroup          VARCHAR(20)     NULL,
    Phone             VARCHAR(20)     NULL,
    Email             VARCHAR(150)    NULL,
    City              NVARCHAR(100)  NULL,
    Province          NVARCHAR(100)   NULL,
    CustomerType      VARCHAR(20)     NOT NULL DEFAULT N'Lẻ',
    LoyaltyPoint      INT             NOT NULL DEFAULT 0,
    MemberSince       DATE            NULL,
    IsActive          BIT             NOT NULL DEFAULT 1,
    LoadDatetime      DATETIME2       NOT NULL DEFAULT GETDATE()
);

CREATE INDEX IX_DimCustomer_CustomerCode ON dbo.DimCustomer(CustomerCode);
CREATE INDEX IX_DimCustomer_City ON dbo.DimCustomer(City);
CREATE INDEX IX_DimCustomer_CustomerType ON dbo.DimCustomer(CustomerType);
GO

PRINT 'DimCustomer table created.';
GO
