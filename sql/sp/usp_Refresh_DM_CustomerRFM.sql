-- ============================================================
-- FILE: sql/sp/usp_Refresh_DM_CustomerRFM.sql
-- Mô tả: Refresh Data Mart DM_CustomerRFM (RFM Analysis)
-- ============================================================

IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'usp_Refresh_DM_CustomerRFM')
BEGIN
    DROP PROCEDURE usp_Refresh_DM_CustomerRFM;
END
GO

CREATE PROCEDURE usp_Refresh_DM_CustomerRFM
    @TenantID VARCHAR(20),
    @AnalysisDate DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF @AnalysisDate IS NULL
        SET @AnalysisDate = CAST(GETDATE() AS DATE);

    -- Xóa data cũ của tenant
    DELETE FROM DM_CustomerRFM WHERE TenantID = @TenantID;

    -- Tính RFM cho từng khách hàng
    -- Dùng CTE để tránh compute RFM_Score 2 lần trong subquery
    ;
    WITH SalesRFM AS (
        SELECT
            f.TenantID,
            f.CustomerKey,
            MAX(CONVERT(DATE, CONVERT(VARCHAR(8), f.DateKey), 112)) AS LastSaleDate,
            COUNT(DISTINCT f.InvoiceNumber) AS Frequency,
            SUM(f.NetSalesAmount) AS Monetary,
            DATEDIFF(DAY,
                MAX(CONVERT(DATE, CONVERT(VARCHAR(8), f.DateKey), 112)),
                @AnalysisDate
            ) AS Recency
        FROM FactSales f
        WHERE f.TenantID = @TenantID
          AND f.CustomerKey > 0
          AND f.ReturnFlag = 0
        GROUP BY f.TenantID, f.CustomerKey
    ),
    ScoredRFM AS (
        SELECT
            s.TenantID,
            s.CustomerKey,
            s.Recency,
            s.Frequency,
            s.Monetary,
            NTILE(5) OVER (PARTITION BY s.TenantID ORDER BY s.Recency DESC) AS R_Score,
            NTILE(5) OVER (PARTITION BY s.TenantID ORDER BY s.Frequency) AS F_Score,
            NTILE(5) OVER (PARTITION BY s.TenantID ORDER BY s.Monetary) AS M_Score
        FROM SalesRFM s
    )
    INSERT INTO DM_CustomerRFM (
        TenantID, CustomerKey, CustomerCode, FullName,
        Recency, Frequency, Monetary,
        R_Score, F_Score, M_Score, RFM_Score, Segment, LastRefreshed
    )
    SELECT
        r.TenantID,
        r.CustomerKey,
        dc.CustomerCode,
        dc.FullName,
        r.Recency,
        r.Frequency,
        r.Monetary,
        r.R_Score,
        r.F_Score,
        r.M_Score,
        r.R_Score + r.F_Score + r.M_Score AS RFM_Score,
        CASE
            WHEN r.R_Score + r.F_Score + r.M_Score >= 13 THEN N'Champions'
            WHEN r.R_Score + r.F_Score + r.M_Score >= 10 THEN N'Loyal'
            WHEN r.R_Score + r.F_Score + r.M_Score >= 7  THEN N'Potential'
            WHEN r.R_Score + r.F_Score + r.M_Score >= 4  THEN N'At Risk'
            ELSE N'Lost'
        END AS Segment,
        GETDATE()
    FROM ScoredRFM r
    INNER JOIN DimCustomer dc
        ON dc.CustomerKey = r.CustomerKey
       AND dc.TenantID = r.TenantID
       AND dc.IsCurrent = 1;
END;
GO

PRINT 'Created: usp_Refresh_DM_CustomerRFM';
