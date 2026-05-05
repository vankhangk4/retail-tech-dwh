-- ============================================================
-- MIGRATION: Add ExpiresAt column to Tenants table
-- Chạy migration này trên SQL Server để thêm cột ExpiresAt
-- ============================================================

IF NOT EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID('Tenants') AND name = 'ExpiresAt')
BEGIN
    ALTER TABLE Tenants ADD ExpiresAt DATETIME2 NULL;
    PRINT 'Migration: Added ExpiresAt column to Tenants';
END
ELSE
BEGIN
    PRINT 'Migration: ExpiresAt column already exists in Tenants';
END
