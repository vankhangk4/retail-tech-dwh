-- ============================================================
-- FILE: sql/sp/usp_Load_DimEmployee.sql
-- Mô tả: Load/Update DimEmployee từ STG (có @TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimEmployee')
BEGIN
    DROP PROCEDURE usp_Load_DimEmployee;
END
GO

CREATE PROCEDURE usp_Load_DimEmployee
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    -- DimEmployee: lấy từ STG_SalesRaw hoặc tạo mặc định
    -- Nếu MaNV chưa có → INSERT với IsActive = 1

    -- Bước 1: Insert nhân viên mới từ STG_SalesRaw (nếu có)
    INSERT INTO DimEmployee (
        EmployeeCode, TenantID, FullName, Department,
        Position, StoreKey, HireDate, IsActive
    )
    SELECT DISTINCT
        s.MaNV,
        @TenantID,
        CASE
            WHEN s.MaNV = 'NV001' THEN CASE WHEN @TenantID = 'STORE_HN' THEN N'Lê Văn Cường' ELSE N'Phạm Minh Đức' END
            WHEN s.MaNV = 'NV002' THEN CASE WHEN @TenantID = 'STORE_HN' THEN N'Hoàng Thị Dung' ELSE N'Võ Thị Hương' END
            ELSE N'Nhân viên ' + s.MaNV
        END,
        N'Bán hàng',
        CASE WHEN s.MaNV = 'NV001' THEN N'Trưởng ca' ELSE N'Nhân viên' END,
        (SELECT StoreKey FROM DimStore WHERE TenantID = @TenantID),
        CAST(GETDATE() AS DATE),
        1
    FROM STG_SalesRaw s
    WHERE s.TenantID = @TenantID
      AND s.MaNV IS NOT NULL
      AND s.MaNV <> 'UNKNOWN'
      AND NOT EXISTS (
          SELECT 1 FROM DimEmployee e
          WHERE e.EmployeeCode = s.MaNV AND e.TenantID = @TenantID
      );
END;
GO

PRINT 'Created: usp_Load_DimEmployee';