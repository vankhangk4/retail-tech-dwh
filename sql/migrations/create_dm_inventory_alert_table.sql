-- ============================================================
-- FILE: sql/migrations/create_dm_inventory_alert_table.sql
-- Mô tả: Tạo bảng DM_InventoryAlert (thay thế view)
-- Chạy sau khi thêm usp_Refresh_DM_InventoryAlert
-- ============================================================

-- Bước 1: Xóa view nếu tồn tại (để replace bằng table)
IF EXISTS (SELECT * FROM sys.views WHERE name = 'DM_InventoryAlert')
BEGIN
    DROP VIEW DM_InventoryAlert;
    PRINT 'Dropped: View DM_InventoryAlert';
END
GO

-- Bước 2: Tạo bảng DM_InventoryAlert (Aggregate Table)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_InventoryAlert')
BEGIN
    CREATE TABLE DM_InventoryAlert (
        AlertKey      BIGINT IDENTITY(1,1) PRIMARY KEY,
        TenantID     VARCHAR(20)   NOT NULL,
        StoreKey     INT          NOT NULL,
        ProductKey   INT          NOT NULL,
        ProductCode  VARCHAR(50)  NOT NULL,
        ProductName  NVARCHAR(255) NOT NULL,
        CategoryName NVARCHAR(100) NOT NULL,
        LatestDateKey INT          NOT NULL,  -- DateKey tồn kho mới nhất
        ClosingStock INT          NOT NULL,  -- Tồn cuối cùng
        ReorderPoint INT          NULL,      -- Mức tồn tối thiểu
        AlertLevel   NVARCHAR(20) NOT NULL,  -- 'Cảnh báo', 'Sắp hết', 'Bình thường'
        StockShortage INT         NOT NULL DEFAULT 0,  -- Số lượng cần đặt hàng
        LastRefreshed DATETIME2   NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_DM_InventoryAlert_Tenant
            FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID)
    );

    PRINT 'Created: Table DM_InventoryAlert';
END
GO

-- Bước 3: Tạo indexes để tối ưu dashboard query
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'DM_InventoryAlert')
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_InventoryAlert_Tenant_Alert')
        CREATE INDEX IX_DM_InventoryAlert_Tenant_Alert
            ON DM_InventoryAlert(TenantID, AlertLevel, ProductKey);

    IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_DM_InventoryAlert_Store')
        CREATE INDEX IX_DM_InventoryAlert_Store
            ON DM_InventoryAlert(TenantID, StoreKey, AlertLevel);

    PRINT 'Created: Indexes for DM_InventoryAlert';
END
GO

PRINT 'Done: create_dm_inventory_alert_table.sql';
