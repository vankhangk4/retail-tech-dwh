-- ============================================================
-- FILE: sql/schema/07_user_profile.sql
-- Mô tả: Migration — Thêm cột hồ sơ người dùng và bảng LoginHistory
-- Idempotent: có thể chạy nhiều lần mà không lỗi
-- ============================================================

-- Thêm cột DisplayName vào AppUsers
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('AppUsers') AND name = 'DisplayName'
)
    ALTER TABLE AppUsers ADD DisplayName NVARCHAR(200) NULL;

-- Thêm cột Email
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('AppUsers') AND name = 'Email'
)
    ALTER TABLE AppUsers ADD Email VARCHAR(255) NULL;

-- Thêm cột Phone
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('AppUsers') AND name = 'Phone'
)
    ALTER TABLE AppUsers ADD Phone VARCHAR(30) NULL;

-- Thêm cột AvatarData (base64 image)
IF NOT EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID('AppUsers') AND name = 'AvatarData'
)
    ALTER TABLE AppUsers ADD AvatarData NVARCHAR(MAX) NULL;

-- Tạo bảng LoginHistory
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LoginHistory')
BEGIN
    CREATE TABLE LoginHistory (
        HistoryID  INT IDENTITY(1,1) PRIMARY KEY,
        UserID     INT NOT NULL,
        LoginAt    DATETIME2 NOT NULL DEFAULT GETDATE(),
        IPAddress  VARCHAR(45) NULL,
        UserAgent  VARCHAR(500) NULL,
        Status     VARCHAR(20) NOT NULL DEFAULT 'success',
        CONSTRAINT CHK_LoginStatus CHECK (Status IN ('success', 'failed')),
        CONSTRAINT FK_LoginHistory_User FOREIGN KEY (UserID)
            REFERENCES AppUsers(UserID)
    );
    CREATE INDEX IX_LoginHistory_UserID ON LoginHistory (UserID, LoginAt DESC);
    PRINT 'Created: LoginHistory';
END

PRINT 'Done: 07_user_profile.sql';
