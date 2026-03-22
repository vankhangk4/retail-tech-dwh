-- ============================================================
-- Script: init_database.sql
-- Mục đích: Tạo database DWH_RetailTech
-- Chạy đầu tiên trên database master
-- ============================================================
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'DWH_RetailTech')
BEGIN
    CREATE DATABASE DWH_RetailTech;
    PRINT 'Database DWH_RetailTech created successfully.';
END
ELSE
BEGIN
    PRINT 'Database DWH_RetailTech already exists. Skipping.';
END
GO
