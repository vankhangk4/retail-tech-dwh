-- ============================================================
-- FILE: sql/sp/usp_Update_Watermark.sql
-- Mô tả: Cập nhật watermark sau mỗi lần ETL (RUNNING → SUCCESS/FAILED)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Update_Watermark')
BEGIN
    DROP PROCEDURE usp_Update_Watermark;
END
GO

CREATE PROCEDURE usp_Update_Watermark
    @TenantID    VARCHAR(20),
    @TableName   VARCHAR(100),
    @Status      VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;

    IF @Status = 'RUNNING'
    BEGIN
        IF EXISTS (SELECT 1 FROM ETL_Watermark WHERE TenantID = @TenantID AND TableName = @TableName)
        BEGIN
            UPDATE ETL_Watermark
            SET LastRunStatus = @Status, UpdatedAt = GETDATE()
            WHERE TenantID = @TenantID AND TableName = @TableName;
        END
        ELSE
        BEGIN
            INSERT INTO ETL_Watermark (TenantID, TableName, LastRunTime, LastRunStatus, UpdatedAt)
            VALUES (@TenantID, @TableName, NULL, @Status, GETDATE());
        END
    END
    ELSE IF @Status = 'SUCCESS'
    BEGIN
        UPDATE ETL_Watermark
        SET LastRunTime = GETDATE(), LastRunStatus = @Status, UpdatedAt = GETDATE()
        WHERE TenantID = @TenantID AND TableName = @TableName;
    END
    ELSE IF @Status = 'FAILED'
    BEGIN
        UPDATE ETL_Watermark
        SET LastRunStatus = @Status, UpdatedAt = GETDATE()
        WHERE TenantID = @TenantID AND TableName = @TableName;
    END

    PRINT 'Watermark updated: ' + @TenantID + '/' + @TableName + ' -> ' + @Status;
END;
GO

PRINT 'Created: usp_Update_Watermark';