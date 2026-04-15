-- ============================================================
-- FILE: sql/sp/usp_Load_DimStore.sql
-- Mô tả: Load/Update DimStore từ Tenants (có @TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimStore')
BEGIN
    DROP PROCEDURE usp_Load_DimStore;
END
GO

CREATE PROCEDURE usp_Load_DimStore
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- DimStore được sync từ bảng Tenants
    -- Nếu StoreCode chưa có trong DimStore → INSERT
    INSERT INTO DimStore (StoreCode, TenantID, StoreName, StoreType, Address, District, City, OpenDate, ManagerName, IsActive)
    SELECT
        t.TenantID,
        t.TenantID,
        t.TenantName,
        CASE WHEN t.TenantID = 'STORE_HN' THEN 'Flagship' ELSE 'Chi nhánh' END,
        CASE
            WHEN t.TenantID = 'STORE_HN' THEN N'123 Đường Láng, Đống Đa'
            WHEN t.TenantID = 'STORE_HCM' THEN N'456 Đường CMT8, Q3'
            ELSE N'Chưa cập nhật'
        END,
        CASE
            WHEN t.TenantID = 'STORE_HN' THEN N'Đống Đa'
            WHEN t.TenantID = 'STORE_HCM' THEN N'Quận 3'
            ELSE N'Chưa cập nhật'
        END,
        CASE
            WHEN t.TenantID = 'STORE_HN' THEN N'Hà Nội'
            WHEN t.TenantID = 'STORE_HCM' THEN N'Hồ Chí Minh'
            ELSE N'Chưa cập nhật'
        END,
        t.CreatedAt,
        CASE WHEN t.TenantID = 'STORE_HN' THEN N'Nguyễn Văn A'
             WHEN t.TenantID = 'STORE_HCM' THEN N'Trần Thị B'
             ELSE N'Chưa cập nhật' END,
        t.IsActive
    FROM Tenants t
    WHERE t.TenantID = @TenantID
      AND NOT EXISTS (
          SELECT 1 FROM DimStore s WHERE s.TenantID = t.TenantID
      );
END;
GO

PRINT 'Created: usp_Load_DimStore';