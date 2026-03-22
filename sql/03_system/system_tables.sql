-- ============================================================
-- Script: 03_system/system_tables.sql
-- Mục đích: Tạo bảng hệ thống ETL (Watermark, RunLog, ErrorLog)
-- Thứ tự chạy: 3
-- ============================================================
USE DWH_RetailTech;
GO

-- ============================================================
-- ETL_Watermark: Theo dõi mốc trích xuất tăng dần
-- ============================================================
IF OBJECT_ID('dbo.ETL_Watermark', 'U') IS NOT NULL DROP TABLE dbo.ETL_Watermark;
CREATE TABLE dbo.ETL_Watermark (
    WatermarkID        INT IDENTITY(1,1) PRIMARY KEY,
    SourceName         VARCHAR(100)    NOT NULL UNIQUE,
    WatermarkValue     DATETIME2       NOT NULL,
    LastRunStatus      VARCHAR(20)     NOT NULL DEFAULT 'NEVER_RUN',
    LastRunDatetime    DATETIME2       NULL,
    RowsExtracted      INT             NULL,
    Notes              NVARCHAR(500)   NULL,
    CreatedDatetime    DATETIME2       NOT NULL DEFAULT GETDATE()
);
GO

-- Seed initial watermark records
INSERT INTO dbo.ETL_Watermark (SourceName, WatermarkValue, LastRunStatus, Notes)
VALUES
    (N'STG_SalesRaw',      '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào'),
    (N'STG_InventoryRaw',  '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào'),
    (N'STG_ProductRaw',    '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào'),
    (N'STG_CustomerRaw',   '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào'),
    (N'STG_StoreRaw',      '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào'),
    (N'STG_EmployeeRaw',   '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào'),
    (N'STG_SupplierRaw',   '2020-01-01', 'NEVER_RUN', N'Chưa chạy lần nào');
GO

-- ============================================================
-- ETL_RunLog: Nhật ký kiểm toán pipeline
-- ============================================================
IF OBJECT_ID('dbo.ETL_RunLog', 'U') IS NOT NULL DROP TABLE dbo.ETL_RunLog;
CREATE TABLE dbo.ETL_RunLog (
    RunLogID           BIGINT IDENTITY(1,1) PRIMARY KEY,
    RunDate            DATE           NOT NULL,
    PipelineName       VARCHAR(100)   NOT NULL,
    StepName           VARCHAR(100)   NULL,
    Status             VARCHAR(20)    NOT NULL,
    RowsProcessed      INT            NULL,
    RowsInserted       INT            NULL,
    RowsUpdated       INT            NULL,
    RowsRejected       INT            NULL,
    Duration_Seconds   DECIMAL(10,2)  NULL,
    ErrorMessage       NVARCHAR(MAX)  NULL,
    LoadDatetime       DATETIME2      NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_ETL_RunLog_RunDate ON dbo.ETL_RunLog(RunDate);
CREATE INDEX IX_ETL_RunLog_PipelineName ON dbo.ETL_RunLog(PipelineName);
CREATE INDEX IX_ETL_RunLog_Status ON dbo.ETL_RunLog(Status);
GO

-- ============================================================
-- STG_ErrorLog: Bảng ghi nhận lỗi dữ liệu
-- ============================================================
IF OBJECT_ID('dbo.STG_ErrorLog', 'U') IS NOT NULL DROP TABLE dbo.STG_ErrorLog;
CREATE TABLE dbo.STG_ErrorLog (
    ErrorID            BIGINT IDENTITY(1,1) PRIMARY KEY,
    SourceTable        VARCHAR(100)   NOT NULL,
    ErrorType          VARCHAR(50)    NOT NULL,
    ErrorMessage       NVARCHAR(500)  NULL,
    RawData            NVARCHAR(MAX)  NULL,
    BatchDate          DATE           NULL,
    IsProcessed        BIT            NOT NULL DEFAULT 0,
    LoadDatetime       DATETIME2      NOT NULL DEFAULT GETDATE()
);
GO

CREATE INDEX IX_STG_ErrorLog_SourceTable ON dbo.STG_ErrorLog(SourceTable);
CREATE INDEX IX_STG_ErrorLog_IsProcessed ON dbo.STG_ErrorLog(IsProcessed);
GO

PRINT 'System tables (ETL_Watermark, ETL_RunLog, STG_ErrorLog) created successfully.';
GO
