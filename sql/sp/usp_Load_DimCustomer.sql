-- ============================================================
-- FILE: sql/sp/usp_Load_DimCustomer.sql
-- Mô tả: SCD Type 2 cho DimCustomer (Có @TenantID)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimCustomer')
BEGIN
    DROP PROCEDURE usp_Load_DimCustomer;
END
GO

CREATE PROCEDURE usp_Load_DimCustomer
    @TenantID VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    IF NOT EXISTS (SELECT 1 FROM Tenants WHERE TenantID = @TenantID AND IsActive = 1)
    BEGIN
        RAISERROR('Tenant khong hop le hoac khong hoat dong.', 16, 1);
        RETURN;
    END

    -- Bước 1: Đóng bản ghi cũ khi thông tin thay đổi (SCD Type 2)
    UPDATE dc
    SET dc.ExpirationDate = DATEADD(DAY, -1, CAST(GETDATE() AS DATE)),
        dc.IsCurrent = 0
    FROM DimCustomer dc
    INNER JOIN STG_CustomerRaw s
        ON s.MaKH = dc.CustomerCode AND dc.TenantID = @TenantID
    WHERE dc.IsCurrent = 1
      AND dc.TenantID = @TenantID
      AND (
          dc.FullName <> s.HoTen
          OR dc.CustomerType <> s.LoaiKH
          OR dc.City <> s.ThanhPho
      );

    -- Bước 2: Chèn bản ghi mới (khách hàng mới hoặc thay đổi thông tin)
    INSERT INTO DimCustomer (
        CustomerCode, TenantID, FullName, Gender,
        City, CustomerType, LoyaltyPoint, MemberSince,
        IsActive, EffectiveDate, ExpirationDate, IsCurrent,
        Phone, Email, Province, DateOfBirth
    )
    SELECT
        s.MaKH,
        @TenantID,
        s.HoTen,
        s.GioiTinh,
        s.ThanhPho,
        s.LoaiKH,
        ISNULL(s.DiemTichLuy, 0),
        s.NgayDangKy,
        1,
        CAST(GETDATE() AS DATE),
        NULL,
        1,
        s.SoDienThoai,
        s.Email,
        s.TinhTP,
        s.NgaySinh
    FROM STG_CustomerRaw s
    WHERE s.TenantID = @TenantID
      AND NOT EXISTS (
          SELECT 1 FROM DimCustomer dc
          WHERE dc.CustomerCode = s.MaKH
            AND dc.TenantID = @TenantID
            AND dc.IsCurrent = 1
      );
END;
GO

PRINT 'Created: usp_Load_DimCustomer';