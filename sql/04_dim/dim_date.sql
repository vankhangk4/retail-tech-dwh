-- ============================================================
-- Script: 04_dim/dim_date.sql
-- Mục đích: Tạo và populate DimDate (2015-01-01 → 2030-12-31)
-- Thứ tự chạy: 4
-- ============================================================
USE DWH_RetailTech;
GO

IF OBJECT_ID('dbo.DimDate', 'U') IS NOT NULL DROP TABLE dbo.DimDate;
CREATE TABLE dbo.DimDate (
    DateKey           INT           NOT NULL,
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
    FiscalQuarter     TINYINT       NOT NULL,
    PRIMARY KEY CLUSTERED (DateKey)
);
GO

-- Vietnamese day names
DECLARE @DayNames TABLE (d INT, name NVARCHAR(15));
INSERT INTO @DayNames VALUES
    (1, N'Thứ Hai'), (2, N'Thứ Ba'), (3, N'Thứ Tư'),
    (4, N'Thứ Năm'), (5, N'Thứ Sáu'), (6, N'Thứ Bảy'), (7, N'Chủ Nhật');

-- Vietnamese month names
DECLARE @MonthNames TABLE (m INT, name NVARCHAR(15));
INSERT INTO @MonthNames VALUES
    (1, N'Tháng 1'), (2, N'Tháng 2'), (3, N'Tháng 3'),
    (4, N'Tháng 4'), (5, N'Tháng 5'), (6, N'Tháng 6'),
    (7, N'Tháng 7'), (8, N'Tháng 8'), (9, N'Tháng 9'),
    (10, N'Tháng 10'), (11, N'Tháng 11'), (12, N'Tháng 12');

-- Vietnamsese holidays
DECLARE @Holidays TABLE (holiday_date DATE, holiday_name NVARCHAR(100));
INSERT INTO @Holidays VALUES
    ('2015-01-01', N'Tết Dương lịch'),
    ('2015-02-19', N'Tết Nguyên Đán 2015'), ('2015-02-20', N'Tết Nguyên Đán 2015'), ('2015-02-21', N'Tết Nguyên Đán 2015'),
    ('2015-04-30', N'Ngày Giải phóng miền Nam'), ('2015-05-01', N'Ngày Quốc tế Lao động'),
    ('2016-01-01', N'Tết Dương lịch'),
    ('2016-02-08', N'Tết Nguyên Đán 2016'), ('2016-02-09', N'Tết Nguyên Đán 2016'), ('2016-02-10', N'Tết Nguyên Đán 2016'),
    ('2016-04-30', N'Ngày Giải phóng miền Nam'), ('2016-05-01', N'Ngày Quốc tế Lao động'),
    ('2017-01-01', N'Tết Dương lịch'),
    ('2017-01-28', N'Tết Nguyên Đán 2017'), ('2017-01-29', N'Tết Nguyên Đán 2017'), ('2017-01-30', N'Tết Nguyên Đán 2017'),
    ('2017-04-30', N'Ngày Giải phóng miền Nam'), ('2017-05-01', N'Ngày Quốc tế Lao động'),
    ('2018-01-01', N'Tết Dương lịch'),
    ('2018-02-16', N'Tết Nguyên Đán 2018'), ('2018-02-17', N'Tết Nguyên Đán 2018'), ('2018-02-18', N'Tết Nguyên Đán 2018'),
    ('2018-04-30', N'Ngày Giải phóng miền Nam'), ('2018-05-01', N'Ngày Quốc tế Lao động'),
    ('2019-01-01', N'Tết Dương lịch'),
    ('2019-02-05', N'Tết Nguyên Đán 2019'), ('2019-02-06', N'Tết Nguyên Đán 2019'), ('2019-02-07', N'Tết Nguyên Đán 2019'),
    ('2019-04-30', N'Ngày Giải phóng miền Nam'), ('2019-05-01', N'Ngày Quốc tế Lao động'),
    ('2020-01-01', N'Tết Dương lịch'),
    ('2020-01-25', N'Tết Nguyên Đán 2020'), ('2020-01-26', N'Tết Nguyên Đán 2020'), ('2020-01-27', N'Tết Nguyên Đán 2020'),
    ('2020-04-30', N'Ngày Giải phóng miền Nam'), ('2020-05-01', N'Ngày Quốc tế Lao động'),
    ('2021-01-01', N'Tết Dương lịch'),
    ('2021-02-12', N'Tết Nguyên Đán 2021'), ('2021-02-13', N'Tết Nguyên Đán 2021'), ('2021-02-14', N'Tết Nguyên Đán 2021'),
    ('2021-04-30', N'Ngày Giải phóng miền Nam'), ('2021-05-01', N'Ngày Quốc tế Lao động'),
    ('2022-01-01', N'Tết Dương lịch'),
    ('2022-02-01', N'Tết Nguyên Đán 2022'), ('2022-02-02', N'Tết Nguyên Đán 2022'), ('2022-02-03', N'Tết Nguyên Đán 2022'),
    ('2022-04-30', N'Ngày Giải phóng miền Nam'), ('2022-05-01', N'Ngày Quốc tế Lao động'),
    ('2023-01-01', N'Tết Dương lịch'),
    ('2023-01-22', N'Tết Nguyên Đán 2023'), ('2023-01-23', N'Tết Nguyên Đán 2023'), ('2023-01-24', N'Tết Nguyên Đán 2023'),
    ('2023-04-30', N'Ngày Giải phóng miền Nam'), ('2023-05-01', N'Ngày Quốc tế Lao động'),
    ('2024-01-01', N'Tết Dương lịch'),
    ('2024-02-10', N'Tết Nguyên Đán 2024'), ('2024-02-11', N'Tết Nguyên Đán 2024'), ('2024-02-12', N'Tết Nguyên Đán 2024'),
    ('2024-04-30', N'Ngày Giải phóng miền Nam'), ('2024-05-01', N'Ngày Quốc tế Lao động'),
    ('2025-01-01', N'Tết Dương lịch'),
    ('2025-01-29', N'Tết Nguyên Đán 2025'), ('2025-01-30', N'Tết Nguyên Đán 2025'), ('2025-01-31', N'Tết Nguyên Đán 2025'),
    ('2025-04-30', N'Ngày Giải phóng miền Nam'), ('2025-05-01', N'Ngày Quốc tế Lao động'),
    ('2026-01-01', N'Tết Dương lịch'),
    ('2026-02-17', N'Tết Nguyên Đán 2026'), ('2026-02-18', N'Tết Nguyên Đán 2026'), ('2026-02-19', N'Tết Nguyên Đán 2026'),
    ('2026-04-30', N'Ngày Giải phóng miền Nam'), ('2026-05-01', N'Ngày Quốc tế Lao động'),
    ('2027-01-01', N'Tết Dương lịch'),
    ('2027-02-06', N'Tết Nguyên Đán 2027'), ('2027-02-07', N'Tết Nguyên Đán 2027'), ('2027-02-08', N'Tết Nguyên Đán 2027'),
    ('2027-04-30', N'Ngày Giải phóng miền Nam'), ('2027-05-01', N'Ngày Quốc tế Lao động'),
    ('2028-01-01', N'Tết Dương lịch'),
    ('2028-01-26', N'Tết Nguyên Đán 2028'), ('2028-01-27', N'Tết Nguyên Đán 2028'), ('2028-01-28', N'Tết Nguyên Đán 2028'),
    ('2028-04-30', N'Ngày Giải phóng miền Nam'), ('2028-05-01', N'Ngày Quốc tế Lao động'),
    ('2029-01-01', N'Tết Dương lịch'),
    ('2029-02-13', N'Tết Nguyên Đán 2029'), ('2029-02-14', N'Tết Nguyên Đán 2029'), ('2029-02-15', N'Tết Nguyên Đán 2029'),
    ('2029-04-30', N'Ngày Giải phóng miền Nam'), ('2029-05-01', N'Ngày Quốc tế Lao động'),
    ('2030-01-01', N'Tết Dương lịch'),
    ('2030-02-03', N'Tết Nguyên Đán 2030'), ('2030-02-04', N'Tết Nguyên Đán 2030'), ('2030-02-05', N'Tết Nguyên Đán 2030'),
    ('2030-04-30', N'Ngày Giải phóng miền Nam'), ('2030-05-01', N'Ngày Quốc tế Lao động');

-- Populate DimDate
;WITH Dates AS (
    SELECT CAST('2015-01-01' AS DATE) AS DateValue
    UNION ALL
    SELECT DATEADD(DAY, 1, DateValue)
    FROM Dates
    WHERE DateValue < '2030-12-31'
)
INSERT INTO dbo.DimDate (
    DateKey, FullDate, DayOfWeek, DayName, DayOfMonth,
    WeekOfYear, MonthNumber, MonthName, Quarter, QuarterName,
    Year, IsWeekend, IsHoliday, HolidayName, FiscalYear, FiscalQuarter
)
SELECT
    CAST(FORMAT(DateValue, 'yyyyMMdd') AS INT)                   AS DateKey,
    DateValue,
    DATEPART(WEEKDAY, DateValue)                                 AS DayOfWeek,
    dn.name                                                       AS DayName,
    DATEPART(DAY, DateValue)                                     AS DayOfMonth,
    DATEPART(ISO_WEEK, DateValue)                               AS WeekOfYear,
    DATEPART(MONTH, DateValue)                                   AS MonthNumber,
    mn.name                                                       AS MonthName,
    DATEPART(QUARTER, DateValue)                                 AS Quarter,
    'Q' + CAST(DATEPART(QUARTER, DateValue) AS CHAR(1))          AS QuarterName,
    DATEPART(YEAR, DateValue)                                    AS Year,
    CASE WHEN DATEPART(WEEKDAY, DateValue) IN (1, 7) THEN 1 ELSE 0 END AS IsWeekend,
    CASE WHEN h.holiday_date IS NOT NULL THEN 1 ELSE 0 END       AS IsHoliday,
    h.holiday_name                                               AS HolidayName,
    DATEPART(YEAR, DateValue)                                    AS FiscalYear,
    DATEPART(QUARTER, DateValue)                                 AS FiscalQuarter
FROM Dates d
JOIN @DayNames dn ON dn.d = DATEPART(WEEKDAY, d.DateValue)
JOIN @MonthNames mn ON mn.m = DATEPART(MONTH, d.DateValue)
LEFT JOIN @Holidays h ON h.holiday_date = d.DateValue
OPTION (MAXRECURSION 6000);

PRINT 'DimDate populated: ' + CAST((SELECT COUNT(*) FROM DimDate) AS VARCHAR) + ' rows';
GO
