# ============================================================
# dashboard_01_revenue.py
# FR-10: Dashboard Phan tich Doanh thu
# ============================================================
# Loi "ORDER BY invalid in views/subqueries" xay ra khi Superset wrap query.
# Fix: KHONG dung ORDER BY trong SQL. Superset se tu dong sort khi render chart.
# ============================================================

DASHBOARD_CONFIG = {
    "dashboard_title": "FR-10: Phan tich Doanh thu",
    "description": "Phan tich doanh thu theo thoi gian, cua hang, danh muc san pham",
    "charts": [
        {
            "name": "Doanh thu theo Thang",
            "viz_type": "line",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    d.Year,
                    d.MonthNumber,
                    d.MonthName,
                    SUM(f.NetSalesAmount) AS NetRevenue,
                    SUM(f.GrossProfitAmount) AS GrossProfit
                FROM FactSales f
                JOIN DimDate d ON d.DateKey = f.DateKey
                WHERE f.ReturnFlag = 0
                GROUP BY d.Year, d.MonthNumber, d.MonthName
            """,
        },
        {
            "name": "Doanh thu theo Cua hang",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    s.StoreName,
                    SUM(f.NetSalesAmount) AS Revenue,
                    SUM(f.GrossProfitAmount) AS Profit
                FROM FactSales f
                JOIN DimStore s ON s.StoreKey = f.StoreKey AND s.TenantId = f.TenantId
                WHERE f.ReturnFlag = 0
                GROUP BY s.StoreName
            """,
        },
        {
            "name": "Doanh thu theo Danh muc",
            "viz_type": "pie",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    p.CategoryName,
                    SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.TenantId = f.TenantId
                WHERE f.ReturnFlag = 0
                GROUP BY p.CategoryName
            """,
        },
        {
            "name": "Tong Doanh thu",
            "viz_type": "big_number",
            "datasource": "FactSales",
            "sql": """
                SELECT SUM(NetSalesAmount) AS TotalRevenue
                FROM FactSales
                WHERE ReturnFlag = 0
            """,
        },
    ],
    "filters": ["Time Range", "Store", "Category"],
}
