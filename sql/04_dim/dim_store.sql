-- ============================================================
-- Script: 04_dim/dim_store.sql
-- Mục đích: Tạo DimStore
-- Thứ tự chạy: 7
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.DimStore', 'U') IS NOT NULL DROP TABLE dbo.DimStore;
CREATE TABLE dbo.DimStore (
    StoreKey          INT IDENTITY(1,1) PRIMARY KEY,
    StoreCode         VARCHAR(20)     NOT NULL UNIQUE,
    StoreName         NVARCHAR(150)   NOT NULL,
    StoreType         VARCHAR(50)     NOT NULL,
    Address           NVARCHAR(255)   NOT NULL,
    District          NVARCHAR(100)   NULL,
    City              NVARCHAR(100)   NOT NULL,
    OpenDate          DATE            NOT NULL,
    ManagerName       NVARCHAR(150)   NULL,
    StoreArea_m2      DECIMAL(8,2)   NULL,
    IsActive          BIT             NOT NULL DEFAULT 1,
    LoadDatetime      DATETIME2       NOT NULL DEFAULT GETDATE()
);

CREATE INDEX IX_DimStore_StoreCode ON dbo.DimStore(StoreCode);
CREATE INDEX IX_DimStore_City ON dbo.DimStore(City);
CREATE INDEX IX_DimStore_IsActive ON dbo.DimStore(IsActive);
GO

PRINT 'DimStore table created.';
GO
