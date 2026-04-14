-- ============================================================
-- FILE: sql/schema/04_create_staging.sql
-- Mô tả: Tạo Staging Layer, ETL Logs, ETL Watermark, Error Log
-- ============================================================

-- 4.5. STG_SalesRaw — Staging bán hàng (có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_SalesRaw')
BEGIN
    CREATE TABLE STG_SalesRaw (
        STG_SalesRawID  INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        MaHoaDon       VARCHAR(50)   NOT NULL,
        MaSP           VARCHAR(50)   NOT NULL,
        MaKH           VARCHAR(50)   NULL,
        MaCH           VARCHAR(20)   NOT NULL,
        MaNV           VARCHAR(20)   NULL,
        NgayBan         DATETIME2    NULL,
        SoLuong         INT          NULL,
        DonGiaBan       DECIMAL(18,2) NULL,
        ChietKhau       DECIMAL(18,2) NULL DEFAULT 0,
        ThueVAT         DECIMAL(18,2) NULL DEFAULT 0,
        PhuongThucTT    VARCHAR(30)   NULL,
        KenhBan         VARCHAR(20)   NULL DEFAULT 'InStore',
        IsHoanTra       BIT          NULL DEFAULT 0,
        STG_LoadDatetime DATETIME2   NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_STG_Sales_Tenant FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: STG_SalesRaw';
END

-- 4.5. STG_InventoryRaw — Staging tồn kho (có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_InventoryRaw')
BEGIN
    CREATE TABLE STG_InventoryRaw (
        STG_InventoryRawID INT IDENTITY(1,1) PRIMARY KEY,
        TenantID          VARCHAR(20)   NOT NULL,
        MaSP              VARCHAR(50)   NOT NULL,
        MaCH              VARCHAR(20)   NOT NULL,
        NgayChupAnh       DATE          NOT NULL,
        TonDauNgay        INT          NULL DEFAULT 0,
        TonCuoiNgay       INT          NULL DEFAULT 0,
        NhapTrongNgay     INT          NULL DEFAULT 0,
        BanTrongNgay      INT          NULL DEFAULT 0,
        DieuChinh         INT          NULL DEFAULT 0,
        DonGiaVon         DECIMAL(18,2) NULL,
        STG_LoadDatetime  DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_STG_Inv_Tenant FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: STG_InventoryRaw';
END

-- 4.5. STG_PurchaseRaw — Staging nhập hàng (có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_PurchaseRaw')
BEGIN
    CREATE TABLE STG_PurchaseRaw (
        STG_PurchaseRawID  INT IDENTITY(1,1) PRIMARY KEY,
        TenantID          VARCHAR(20)   NOT NULL,
        SoPhieuDat        VARCHAR(50)   NOT NULL,
        MaSP              VARCHAR(50)   NOT NULL,
        MaNCC             VARCHAR(50)   NOT NULL,
        MaCH              VARCHAR(20)   NOT NULL,
        NgayDat           DATE          NOT NULL,
        NgayNhan          DATE          NULL,
        SoLuongDat        INT          NULL,
        SoLuongNhan       INT          NULL,
        DonGiaNhap        DECIMAL(18,2) NULL,
        STG_LoadDatetime  DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_STG_Pur_Tenant FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: STG_PurchaseRaw';
END

-- 4.5. STG_ProductRaw — Staging sản phẩm (Shared — không cần TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_ProductRaw')
BEGIN
    CREATE TABLE STG_ProductRaw (
        STG_ProductRawID INT IDENTITY(1,1) PRIMARY KEY,
        MaSP             VARCHAR(50)  NOT NULL,
        TenSP            NVARCHAR(255) NOT NULL,
        ThuongHieu       NVARCHAR(100) NOT NULL,
        DanhMuc          NVARCHAR(100) NOT NULL,
        DanhMucCon       NVARCHAR(100) NULL,
        GiaVon           DECIMAL(18,2) NOT NULL,
        GiaNiemYet       DECIMAL(18,2) NOT NULL,
        DonViTinh        VARCHAR(20)   NULL DEFAULT N'cái',
        BaoHanh_Thang    TINYINT      NULL,
        STG_LoadDatetime DATETIME2    NOT NULL DEFAULT GETDATE()
    );
    PRINT 'Created: STG_ProductRaw';
END

-- 4.5. STG_CustomerRaw — Staging khách hàng (có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_CustomerRaw')
BEGIN
    CREATE TABLE STG_CustomerRaw (
        STGCustomerID    INT IDENTITY(1,1) PRIMARY KEY,
        TenantID        VARCHAR(20)   NOT NULL,
        MaKH            VARCHAR(50)   NOT NULL,
        HoTen           NVARCHAR(150) NOT NULL,
        GioiTinh         CHAR(1)       NULL,
        NgaySinh         DATE          NULL,
        ThanhPho         NVARCHAR(100) NULL,
        TinhTP          NVARCHAR(100) NULL,
        SoDienThoai      VARCHAR(20)   NULL,
        Email            VARCHAR(150)  NULL,
        LoaiKH           VARCHAR(20)   NOT NULL DEFAULT N'Le',
        DiemTichLuy      INT          NULL DEFAULT 0,
        NgayDangKy       DATE         NOT NULL,
        STG_LoadDatetime DATETIME2   NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_STG_Cust_Tenant FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: STG_CustomerRaw';
END

-- 4.8. STG_ErrorLog — Bảng ghi nhận bản ghi lỗi trong quá trình Transform
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'STG_ErrorLog')
BEGIN
    CREATE TABLE STG_ErrorLog (
        ErrorLogID      INT IDENTITY(1,1) PRIMARY KEY,
        TenantID        VARCHAR(20)   NOT NULL,
        SourceTable      VARCHAR(100)  NOT NULL,
        ErrorType        VARCHAR(50)   NOT NULL,
        RawData          NVARCHAR(MAX) NULL,
        ErrorMessage     NVARCHAR(MAX) NULL,
        LoadDatetime     DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_STG_Err_Tenant FOREIGN KEY (TenantID) REFERENCES Tenants(TenantID)
    );
    PRINT 'Created: STG_ErrorLog';
END

-- 4.9. ETLLogs — Bảng ghi lịch sử mỗi lần chạy ETL
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ETLLogs')
BEGIN
    CREATE TABLE ETLLogs (
        LogID          INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        BatchDate      DATE          NOT NULL,
        SourceTable    VARCHAR(100)  NOT NULL,
        RunStatus      VARCHAR(20)  NOT NULL,
        RowsExtracted  INT          NULL,
        RowsInserted   INT          NULL,
        RowsRejected   INT          NULL,
        StartTime      DATETIME2    NOT NULL DEFAULT GETDATE(),
        EndTime        DATETIME2    NULL,
        ErrorMessage   NVARCHAR(MAX) NULL,
        CreatedAt     DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT CHK_RunStatus CHECK (RunStatus IN ('SUCCESS', 'FAILED', 'RUNNING'))
    );
    PRINT 'Created: ETLLogs';
END

-- 5.2.2. ETL_Watermark — Mốc thời gian incremental (có TenantID)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ETL_Watermark')
BEGIN
    CREATE TABLE ETL_Watermark (
        WatermarkID    INT IDENTITY(1,1) PRIMARY KEY,
        TenantID       VARCHAR(20)   NOT NULL,
        TableName      VARCHAR(100)  NOT NULL,
        LastRunTime    DATETIME2    NULL,
        LastRunStatus  VARCHAR(20)  NOT NULL DEFAULT 'PENDING',
        UpdatedAt      DATETIME2    NOT NULL DEFAULT GETDATE(),
        CONSTRAINT UQ_ETL_Watermark UNIQUE (TenantID, TableName),
        CONSTRAINT CHK_WatermarkStatus CHECK (LastRunStatus IN ('PENDING', 'RUNNING', 'SUCCESS', 'FAILED'))
    );
    PRINT 'Created: ETL_Watermark';
END

-- Bước 3: Thêm Index cho TenantID và composite indexes
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ETLLogs_Tenant_Date')
    CREATE INDEX IX_ETLLogs_Tenant_Date ON ETLLogs(TenantID, BatchDate);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ETLLogs_Status')
    CREATE INDEX IX_ETLLogs_Status ON ETLLogs(RunStatus, StartTime);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_ETL_Watermark_Tenant')
    CREATE INDEX IX_ETL_Watermark_Tenant ON ETL_Watermark(TenantID, TableName);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_STG_Sales_Tenant')
    CREATE INDEX IX_STG_Sales_Tenant ON STG_SalesRaw(TenantID, NgayBan);
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = 'IX_STG_Inv_Tenant')
    CREATE INDEX IX_STG_Inv_Tenant ON STG_InventoryRaw(TenantID, NgayChupAnh);

PRINT 'Done: 04_create_staging.sql';
