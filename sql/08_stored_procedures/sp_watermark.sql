-- ============================================================
-- Script: 08_stored_procedures/sp_watermark.sql
-- Mục đích: CRUD cho bảng ETL_Watermark
-- ============================================================
USE DWH_RetailTech;
GO

-- ============================================================
-- SP: sp_Get_Watermark
-- ============================================================
IF OBJECT_ID('dbo.sp_Get_Watermark', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Get_Watermark;
GO
CREATE PROCEDURE dbo.sp_Get_Watermark
    @SourceName VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT WatermarkID, SourceName, WatermarkValue, LastRunStatus, LastRunDatetime, RowsExtracted, Notes
    FROM dbo.ETL_Watermark
    WHERE SourceName = @SourceName;
END;
GO

-- ============================================================
-- SP: sp_Update_Watermark
-- ============================================================
IF OBJECT_ID('dbo.sp_Update_Watermark', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Update_Watermark;
GO
CREATE PROCEDURE dbo.sp_Update_Watermark
    @SourceName     VARCHAR(100),
    @Status         VARCHAR(20),
    @RowsExtracted  INT = NULL,
    @Notes          NVARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    UPDATE dbo.ETL_Watermark
    SET    LastRunStatus   = @Status,
           LastRunDatetime = GETDATE(),
           RowsExtracted   = ISNULL(@RowsExtracted, RowsExtracted),
           Notes           = ISNULL(@Notes, Notes)
    WHERE  SourceName = @SourceName;
END;
GO

-- ============================================================
-- SP: sp_Get_All_Watermarks
-- ============================================================
IF OBJECT_ID('dbo.sp_Get_All_Watermarks', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_Get_All_Watermarks;
GO
CREATE PROCEDURE dbo.sp_Get_All_Watermarks
AS
BEGIN
    SET NOCOUNT ON;
    SELECT WatermarkID, SourceName, WatermarkValue, LastRunStatus, LastRunDatetime, RowsExtracted, Notes
    FROM dbo.ETL_Watermark
    ORDER BY SourceName;
END;
GO

PRINT 'Watermark stored procedures created.';
GO
