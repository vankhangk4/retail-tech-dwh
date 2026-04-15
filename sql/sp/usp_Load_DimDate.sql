-- ============================================================
-- FILE: sql/sp/usp_Load_DimDate.sql
-- Mô tả: Pre-populate DimDate từ 2015-01-01 đến 2030-12-31
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Load_DimDate')
BEGIN
    DROP PROCEDURE usp_Load_DimDate;
END
GO

CREATE PROCEDURE usp_Load_DimDate
    @StartDate DATE = '2015-01-01',
    @EndDate   DATE = '2030-12-31'
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @CurrentDate DATE = @StartDate;

    WHILE @CurrentDate <= @EndDate
    BEGIN
        -- Check nếu DateKey đã tồn tại thì skip
        IF NOT EXISTS (SELECT 1 FROM DimDate WHERE DateKey = FORMAT(@CurrentDate, 'yyyyMMdd'))
        BEGIN
            INSERT INTO DimDate (
                DateKey, FullDate, DayOfWeek, DayName, DayOfMonth,
                WeekOfYear, MonthNumber, MonthName, Quarter, QuarterName,
                Year, IsWeekend, IsHoliday, HolidayName,
                FiscalYear, FiscalQuarter
            )
            VALUES (
                FORMAT(@CurrentDate, 'yyyyMMdd'),
                @CurrentDate,
                DATEPART(WEEKDAY, @CurrentDate),
                CASE DATEPART(WEEKDAY, @CurrentDate)
                    WHEN 1 THEN N'Chủ Nhật'
                    WHEN 2 THEN N'Thứ Hai'
                    WHEN 3 THEN N'Thứ Ba'
                    WHEN 4 THEN N'Thứ Tư'
                    WHEN 5 THEN N'Thứ Năm'
                    WHEN 6 THEN N'Thứ Sáu'
                    WHEN 7 THEN N'Thứ Bảy'
                END,
                DAY(@CurrentDate),
                DATEPART(WEEK, @CurrentDate),
                MONTH(@CurrentDate),
                CASE MONTH(@CurrentDate)
                    WHEN 1  THEN N'Tháng 1'
                    WHEN 2  THEN N'Tháng 2'
                    WHEN 3  THEN N'Tháng 3'
                    WHEN 4  THEN N'Tháng 4'
                    WHEN 5  THEN N'Tháng 5'
                    WHEN 6  THEN N'Tháng 6'
                    WHEN 7  THEN N'Tháng 7'
                    WHEN 8  THEN N'Tháng 8'
                    WHEN 9  THEN N'Tháng 9'
                    WHEN 10 THEN N'Tháng 10'
                    WHEN 11 THEN N'Tháng 11'
                    WHEN 12 THEN N'Tháng 12'
                END,
                DATEPART(QUARTER, @CurrentDate),
                'Q' + CAST(DATEPART(QUARTER, @CurrentDate) AS CHAR(1)),
                YEAR(@CurrentDate),
                CASE WHEN DATEPART(WEEKDAY, @CurrentDate) IN (1, 7) THEN 1 ELSE 0 END,
                0,
                NULL,
                -- FiscalYear = CalendarYear (có thể tùy chỉnh theo doanh nghiệp)
                YEAR(@CurrentDate),
                DATEPART(QUARTER, @CurrentDate)
            );
        END

        SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
    END

    PRINT 'DimDate populated from ' + CAST(@StartDate AS VARCHAR) + ' to ' + CAST(@EndDate AS VARCHAR);
END;
GO

PRINT 'Created: usp_Load_DimDate';

-- Chạy để tạo dữ liệu DimDate
-- EXEC usp_Load_DimDate @StartDate = '2015-01-01', @EndDate = '2030-12-31';