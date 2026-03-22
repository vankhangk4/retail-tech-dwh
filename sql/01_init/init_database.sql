-- ============================================================
-- Script: 01_init/init_database.sql
-- Mục đích: Tạo database DWH_RetailTech
-- Thứ tự chạy: 1
-- ============================================================
USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'DWH_RetailTech')
BEGIN
    CREATE DATABASE DWH_RetailTech;
    PRINT 'Database DWH_RetailTech created successfully.';
END
ELSE
BEGIN
    PRINT 'Database DWH_RetailTech already exists.';
END
GO

USE DWH_RetailTech;
GO

-- Set database options for DWH workload
ALTER DATABASE DWH_RetailTech SET READ_WRITE;
GO

PRINT 'Database initialization complete. Using DWH_RetailTech.';
GO
