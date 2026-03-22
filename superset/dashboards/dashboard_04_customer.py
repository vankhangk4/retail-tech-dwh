# ============================================================
# dashboard_04_customer.py
# FR-13: Dashboard Phân tích Khách hàng
# ============================================================
DASHBOARD_CONFIG = {
    "dashboard_title": "FR-13: Dashboard Phân tích Khách hàng",
    "description": "RFM segmentation, tỷ lệ khách quay lại, phân tích hành vi",
    "charts": [
        {
            "name": "RFM - Phân khúc Khách hàng",
            "viz_type": "table",
            "datasource": "DimCustomer",
            "sql": """
                -- RFM Analysis
                WITH RFM AS (
                    SELECT
                        c.CustomerKey,
                        c.FullName,
                        MAX(f.DateKey) AS LastPurchaseDate,
                        COUNT(DISTINCT f.InvoiceNumber) AS Frequency,
                        SUM(f.NetSalesAmount) AS Monetary,
                        DATEDIFF(DAY, MAX(CONVERT(DATE, CAST(d.FullDate AS VARCHAR(8)))), GETDATE()) AS Recency
                    FROM FactSales f
                    JOIN DimCustomer c ON c.CustomerKey = f.CustomerKey
                    JOIN DimDate d ON d.DateKey = f.DateKey
                    WHERE f.ReturnFlag = 0
                    GROUP BY c.CustomerKey, c.FullName
                )
                SELECT
                    FullName,
                    Recency,
                    Frequency,
                    Monetary,
                    CASE WHEN Recency <= 30 THEN 'R-High' WHEN Recency <= 90 THEN 'R-Med' ELSE 'R-Low' END AS R_Score,
                    CASE WHEN Frequency >= 5 THEN 'F-High' WHEN Frequency >= 2 THEN 'F-Med' ELSE 'F-Low' END AS F_Score,
                    CASE WHEN Monetary >= 50000000 THEN 'M-High' WHEN Monetary >= 10000000 THEN 'M-Med' ELSE 'M-Low' END AS M_Score
                FROM RFM
                ORDER BY Monetary DESC
            """,
        },
        {
            "name": "Phân bố Khách hàng theo Loại",
            "viz_type": "pie",
            "datasource": "DimCustomer",
            "sql": """
                SELECT CustomerType, COUNT(*) AS CustomerCount
                FROM DimCustomer
                WHERE IsActive = 1
                GROUP BY CustomerType
            """,
        },
        {
            "name": "Tỷ lệ Khách quay lại theo Tháng",
            "viz_type": "line",
            "datasource": "FactSales",
            "sql": """
                WITH MonthlyCustomers AS (
                    SELECT
                        d.Year, d.MonthNumber,
                        c.CustomerKey,
                        COUNT(DISTINCT f.InvoiceNumber) AS Visits
                    FROM FactSales f
                    JOIN DimDate d ON d.DateKey = f.DateKey
                    JOIN DimCustomer c ON c.CustomerKey = f.CustomerKey
                    WHERE f.ReturnFlag = 0
                    GROUP BY d.Year, d.MonthNumber, c.CustomerKey
                ),
                ReturningCustomers AS (
                    SELECT Year, MonthNumber,
                           COUNT(*) AS ReturningCount,
                           COUNT(*) * 1.0 / (SELECT COUNT(DISTINCT CustomerKey) FROM FactSales) * 100 AS ReturnRatePct
                    FROM MonthlyCustomers
                    WHERE Visits > 1
                    GROUP BY Year, MonthNumber
                )
                SELECT mc.Year, mc.MonthNumber,
                       ISNULL(rc.ReturnRatePct, 0) AS ReturnRatePct
                FROM (
                    SELECT DISTINCT d.Year, d.MonthNumber
                    FROM DimDate d
                    WHERE d.Year = 2025
                ) mc
                LEFT JOIN ReturningCustomers rc ON rc.Year = mc.Year AND rc.MonthNumber = mc.MonthNumber
                ORDER BY mc.Year, mc.MonthNumber
            """,
        },
        {
            "name": "Doanh thu theo Nhóm Tuổi",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT ISNULL(c.AgeGroup, 'Unknown') AS AgeGroup,
                       SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimCustomer c ON c.CustomerKey = f.CustomerKey
                WHERE f.ReturnFlag = 0
                GROUP BY c.AgeGroup
                ORDER BY Revenue DESC
            """,
        },
    ],
    "filters": ["Time Range", "Customer Type", "City", "Age Group"],
}
