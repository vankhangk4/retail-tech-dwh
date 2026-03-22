# ============================================================
# dashboard_01_revenue.py
# FR-10: Dashboard Phân tích Doanh thu
# ============================================================
# This file defines the dashboard configuration for Superset.
# Import into Superset via: superset import_dashboards -f dashboard_01_revenue.py
#
# Alternatively, create charts manually in Superset UI:
#
# Chart 1: Doanh thu theo Tháng (Line Chart)
# SQL:
#   SELECT
#       d.Year,
#       d.MonthNumber,
#       d.MonthName,
#       SUM(f.NetSalesAmount) AS NetRevenue,
#       SUM(f.GrossProfitAmount) AS GrossProfit
#   FROM FactSales f
#   JOIN DimDate d ON d.DateKey = f.DateKey
#   GROUP BY d.Year, d.MonthNumber, d.MonthName
#   ORDER BY d.Year, d.MonthNumber
#
# Chart 2: Doanh thu theo Cửa hàng (Bar Chart)
# SQL:
#   SELECT
#       s.StoreName,
#       SUM(f.NetSalesAmount) AS Revenue,
#       SUM(f.GrossProfitAmount) AS Profit
#   FROM FactSales f
#   JOIN DimStore s ON s.StoreKey = f.StoreKey
#   GROUP BY s.StoreName
#   ORDER BY Revenue DESC
#
# Chart 3: Doanh thu theo Danh mục (Pie Chart)
# SQL:
#   SELECT
#       p.CategoryName,
#       SUM(f.NetSalesAmount) AS Revenue
#   FROM FactSales f
#   JOIN DimProduct p ON p.ProductKey = f.ProductKey
#   GROUP BY p.CategoryName
#
# KPI Card 1: Tổng Doanh thu
# KPI Card 2: Tổng Lợi nhuận
# KPI Card 3: Số hóa đơn
# KPI Card 4: Tỷ lệ lợi nhuận (%)
#
# Filter: Time Range (Month/Quarter/Year), Store, Category

DASHBOARD_CONFIG = {
    "dashboard_title": "FR-10: Dashboard Phân tích Doanh thu",
    "description": "Phân tích doanh thu theo thời gian, cửa hàng, danh mục sản phẩm",
    "charts": [
        {
            "name": "Doanh thu theo Tháng",
            "viz_type": "line",
            "datasource": "FactSales",
            "sql": """
                SELECT d.Year, d.MonthNumber, d.MonthName,
                       SUM(f.NetSalesAmount) AS NetRevenue,
                       SUM(f.GrossProfitAmount) AS GrossProfit
                FROM FactSales f
                JOIN DimDate d ON d.DateKey = f.DateKey
                GROUP BY d.Year, d.MonthNumber, d.MonthName
                ORDER BY d.Year, d.MonthNumber
            """,
            "fields": {
                "x_axis": "MonthName",
                "metrics": [{"label": "NetRevenue"}, {"label": "GrossProfit"}],
            }
        },
        {
            "name": "Doanh thu theo Cửa hàng",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT s.StoreName,
                       SUM(f.NetSalesAmount) AS Revenue,
                       SUM(f.GrossProfitAmount) AS Profit
                FROM FactSales f
                JOIN DimStore s ON s.StoreKey = f.StoreKey
                GROUP BY s.StoreName
                ORDER BY Revenue DESC
            """,
        },
        {
            "name": "Doanh thu theo Danh mục",
            "viz_type": "pie",
            "datasource": "FactSales",
            "sql": """
                SELECT p.CategoryName,
                       SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey
                GROUP BY p.CategoryName
            """,
        },
        {
            "name": "Tổng Doanh thu",
            "viz_type": "big_number",
            "datasource": "FactSales",
            "sql": "SELECT SUM(NetSalesAmount) AS TotalRevenue FROM FactSales",
        },
    ],
    "filters": ["Time Range", "Store", "Category"],
}
