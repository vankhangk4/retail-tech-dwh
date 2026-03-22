-- ============================================================
-- Script: 04_dim/dim_date.sql
-- Muc dich: Tao va populate DimDate (2015-01-01 -> 2030-12-31)
-- ============================================================
USE DWH_RetailTech;
GO

-- Xoa FK references
DECLARE @fk_sql NVARCHAR(MAX) = N'';
SELECT @fk_sql += 'ALTER TABLE ' + OBJECT_SCHEMA_NAME(fk.parent_object_id) + '.[' + OBJECT_NAME(fk.parent_object_id) + '] DROP CONSTRAINT [' + fk.name + '];'
FROM sys.foreign_keys fk
INNER JOIN sys.tables t ON fk.referenced_object_id = t.object_id
WHERE t.name = 'DimDate';
EXEC sp_executesql @fk_sql;
GO

IF OBJECT_ID('dbo.DimDate', 'U') IS NOT NULL DROP TABLE dbo.DimDate;
GO

CREATE TABLE dbo.DimDate (
    DateKey           INT           NOT NULL PRIMARY KEY,
    FullDate          DATE          NOT NULL UNIQUE,
    DayOfWeek         TINYINT       NOT NULL,
    DayName           NVARCHAR(15)  NOT NULL,
    DayOfMonth        TINYINT       NOT NULL,
    WeekOfYear        TINYINT       NOT NULL,
    MonthNumber       TINYINT       NOT NULL,
    MonthName         NVARCHAR(15)  NOT NULL,
    Quarter           TINYINT       NOT NULL,
    QuarterName       CHAR(2)       NOT NULL,
    Year              SMALLINT      NOT NULL,
    IsWeekend         BIT           NOT NULL DEFAULT 0,
    IsHoliday         BIT           NOT NULL DEFAULT 0,
    HolidayName       NVARCHAR(100) NULL,
    FiscalYear        SMALLINT      NOT NULL,
    FiscalQuarter     TINYINT       NOT NULL
);
GO

CREATE TABLE #Holidays (DateKey INT PRIMARY KEY, HolidayName NVARCHAR(100));
INSERT INTO #Holidays (DateKey, HolidayName) VALUES
(20150101,N'Tết Dương lịch'),
(20150219,N'Tết Nguyên Đán 2015'),(20150220,N'Tết Nguyên Đán 2015'),(20150221,N'Tết Nguyên Đán 2015'),
(20150430,N'Ngày Giải phóng miền Nam'),(20150501,N'Ngày Quốc tế Lao động'),
(20160101,N'Tết Dương lịch'),
(20160208,N'Tết Nguyên Đán 2016'),(20160209,N'Tết Nguyên Đán 2016'),(20160210,N'Tết Nguyên Đán 2016'),
(20160430,N'Ngày Giải phóng miền Nam'),(20160501,N'Ngày Quốc tế Lao động'),
(20170101,N'Tết Dương lịch'),
(20170128,N'Tết Nguyên Đán 2017'),(20170129,N'Tết Nguyên Đán 2017'),(20170130,N'Tết Nguyên Đán 2017'),
(20170430,N'Ngày Giải phóng miền Nam'),(20170501,N'Ngày Quốc tế Lao động'),
(20180101,N'Tết Dương lịch'),
(20180216,N'Tết Nguyên Đán 2018'),(20180217,N'Tết Nguyên Đán 2018'),(20180218,N'Tết Nguyên Đán 2018'),
(20180430,N'Ngày Giải phóng miền Nam'),(20180501,N'Ngày Quốc tế Lao động'),
(20190101,N'Tết Dương lịch'),
(20190205,N'Tết Nguyên Đán 2019'),(20190206,N'Tết Nguyên Đán 2019'),(20190207,N'Tết Nguyên Đán 2019'),
(20190430,N'Ngày Giải phóng miền Nam'),(20190501,N'Ngày Quốc tế Lao động'),
(20200101,N'Tết Dương lịch'),
(20200125,N'Tết Nguyên Đán 2020'),(20200126,N'Tết Nguyên Đán 2020'),(20200127,N'Tết Nguyên Đán 2020'),
(20200430,N'Ngày Giải phóng miền Nam'),(20200501,N'Ngày Quốc tế Lao động'),
(20210101,N'Tết Dương lịch'),
(20210212,N'Tết Nguyên Đán 2021'),(20210213,N'Tết Nguyên Đán 2021'),(20210214,N'Tết Nguyên Đán 2021'),
(20210430,N'Ngày Giải phóng miền Nam'),(20210501,N'Ngày Quốc tế Lao động'),
(20220101,N'Tết Dương lịch'),
(20220201,N'Tết Nguyên Đán 2022'),(20220202,N'Tết Nguyên Đán 2022'),(20220203,N'Tết Nguyên Đán 2022'),
(20220430,N'Ngày Giải phóng miền Nam'),(20220501,N'Ngày Quốc tế Lao động'),
(20230101,N'Tết Dương lịch'),
(20230122,N'Tết Nguyên Đán 2023'),(20230123,N'Tết Nguyên Đán 2023'),(20230124,N'Tết Nguyên Đán 2023'),
(20230430,N'Ngày Giải phóng miền Nam'),(20230501,N'Ngày Quốc tế Lao động'),
(20240101,N'Tết Dương lịch'),
(20240210,N'Tết Nguyên Đán 2024'),(20240211,N'Tết Nguyên Đán 2024'),(20240212,N'Tết Nguyên Đán 2024'),
(20240430,N'Ngày Giải phóng miền Nam'),(20240501,N'Ngày Quốc tế Lao động'),
(20250101,N'Tết Dương lịch'),
(20250129,N'Tết Nguyên Đán 2025'),(20250130,N'Tết Nguyên Đán 2025'),(20250131,N'Tết Nguyên Đán 2025'),
(20250430,N'Ngày Giải phóng miền Nam'),(20250501,N'Ngày Quốc tế Lao động'),
(20260101,N'Tết Dương lịch'),
(20260217,N'Tết Nguyên Đán 2026'),(20260218,N'Tết Nguyên Đán 2026'),(20260219,N'Tết Nguyên Đán 2026'),
(20260430,N'Ngày Giải phóng miền Nam'),(20260501,N'Ngày Quốc tế Lao động'),
(20270101,N'Tết Dương lịch'),
(20270206,N'Tết Nguyên Đán 2027'),(20270207,N'Tết Nguyên Đán 2027'),(20270208,N'Tết Nguyên Đán 2027'),
(20270430,N'Ngày Giải phóng miền Nam'),(20270501,N'Ngày Quốc tế Lao động'),
(20280101,N'Tết Dương lịch'),
(20280126,N'Tết Nguyên Đán 2028'),(20280127,N'Tết Nguyên Đán 2028'),(20280128,N'Tết Nguyên Đán 2028'),
(20280430,N'Ngày Giải phóng miền Nam'),(20280501,N'Ngày Quốc tế Lao động'),
(20290101,N'Tết Dương lịch'),
(20290213,N'Tết Nguyên Đán 2029'),(20290214,N'Tết Nguyên Đán 2029'),(20290215,N'Tết Nguyên Đán 2029'),
(20290430,N'Ngày Giải phóng miền Nam'),(20290501,N'Ngày Quốc tế Lao động'),
(20300101,N'Tết Dương lịch'),
(20300203,N'Tết Nguyên Đán 2030'),(20300204,N'Tết Nguyên Đán 2030'),(20300205,N'Tết Nguyên Đán 2030'),
(20300430,N'Ngày Giải phóng miền Nam'),(20300501,N'Ngày Quốc tế Lao động');
GO

;WITH DateSeq AS (
    SELECT CAST('2015-01-01' AS DATE) AS DateValue
    UNION ALL
    SELECT DATEADD(DAY, 1, DateValue)
    FROM DateSeq
    WHERE DateValue < CAST('2030-12-31' AS DATE)
)
INSERT INTO dbo.DimDate (DateKey, FullDate, DayOfWeek, DayName, DayOfMonth, WeekOfYear, MonthNumber, MonthName, Quarter, QuarterName, Year, IsWeekend, IsHoliday, HolidayName, FiscalYear, FiscalQuarter)
SELECT
    CONVERT(INT, CONVERT(VARCHAR, d.DateValue, 112)) AS DateKey,
    d.DateValue,
    CASE DATEPART(WEEKDAY, d.DateValue)
        WHEN 7 THEN 1 WHEN 1 THEN 2 WHEN 2 THEN 3 WHEN 3 THEN 4
        WHEN 4 THEN 5 WHEN 5 THEN 6 WHEN 6 THEN 7
    END AS DayOfWeek,
    CASE DATEPART(WEEKDAY, d.DateValue)
        WHEN 1 THEN N'Chủ Nhật' WHEN 2 THEN N'Thứ Hai' WHEN 3 THEN N'Thứ Ba'
        WHEN 4 THEN N'Thứ Tư' WHEN 5 THEN N'Thứ Năm' WHEN 6 THEN N'Thứ Sáu' WHEN 7 THEN N'Thứ Bảy'
    END AS DayName,
    DATEPART(DAY, d.DateValue) AS DayOfMonth,
    DATEPART(ISO_WEEK, d.DateValue) AS WeekOfYear,
    DATEPART(MONTH, d.DateValue) AS MonthNumber,
    CASE DATEPART(MONTH, d.DateValue)
        WHEN 1 THEN N'Tháng 1' WHEN 2 THEN N'Tháng 2' WHEN 3 THEN N'Tháng 3'
        WHEN 4 THEN N'Tháng 4' WHEN 5 THEN N'Tháng 5' WHEN 6 THEN N'Tháng 6'
        WHEN 7 THEN N'Tháng 7' WHEN 8 THEN N'Tháng 8' WHEN 9 THEN N'Tháng 9'
        WHEN 10 THEN N'Tháng 10' WHEN 11 THEN N'Tháng 11' WHEN 12 THEN N'Tháng 12'
    END AS MonthName,
    DATEPART(QUARTER, d.DateValue) AS Quarter,
    'Q' + CAST(DATEPART(QUARTER, d.DateValue) AS CHAR(1)) AS QuarterName,
    DATEPART(YEAR, d.DateValue) AS Year,
    CASE WHEN DATEPART(WEEKDAY, d.DateValue) IN (1, 7) THEN 1 ELSE 0 END AS IsWeekend,
    CASE WHEN h.DateKey IS NOT NULL THEN 1 ELSE 0 END AS IsHoliday,
    h.HolidayName,
    DATEPART(YEAR, d.DateValue) AS FiscalYear,
    DATEPART(QUARTER, d.DateValue) AS FiscalQuarter
FROM DateSeq d
LEFT JOIN #Holidays h ON h.DateKey = CONVERT(INT, CONVERT(VARCHAR, d.DateValue, 112))
OPTION (MAXRECURSION 5844);
GO

DROP TABLE #Holidays;
GO

PRINT 'DimDate populated: ' + CAST((SELECT COUNT(*) FROM DimDate) AS VARCHAR) + ' rows';
GO
