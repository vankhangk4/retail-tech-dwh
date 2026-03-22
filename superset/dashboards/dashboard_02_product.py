# ============================================================
# dashboard_02_product.py
# FR-11: Dashboard Phân tích Sản phẩm
# ============================================================
DASHBOARD_CONFIG = {
    "dashboard_title": "FR-11: Dashboard Phân tích Sản phẩm",
    "description": "TOP bán chạy, đóng góp doanh thu, biên lợi nhuận theo sản phẩm",
    "charts": [
        {
            "name": "TOP 10 Sản phẩm bán chạy",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT TOP 10 p.ProductName,
                       SUM(f.Quantity) AS TotalQtySold,
                       SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey
                WHERE f.ReturnFlag = 0
                GROUP BY p.ProductName
                ORDER BY TotalQtySold DESC
            """,
        },
        {
            "name": "Tỷ lệ Doanh thu theo Danh mục",
            "viz_type": "pie",
            "datasource": "FactSales",
            "sql": """
                SELECT p.CategoryName,
                       SUM(f.NetSalesAmount) AS Revenue,
                       ROUND(SUM(f.NetSalesAmount) * 100.0 /
                             SUM(SUM(f.NetSalesAmount)) OVER(), 2) AS RevenuePct
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey
                GROUP BY p.CategoryName
            """,
        },
        {
            "name": "Biên Lợi nhuận theo Sản phẩm",
            "viz_type": "line",
            "datasource": "FactSales",
            "sql": """
                SELECT p.ProductName,
                       AVG(CASE WHEN f.NetSalesAmount > 0
                           THEN f.GrossProfitAmount / f.NetSalesAmount * 100
                           ELSE 0 END) AS AvgProfitMarginPct
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey
                GROUP BY p.ProductName
                ORDER BY AvgProfitMarginPct DESC
            """,
        },
        {
            "name": "Số lượng sản phẩm theo Thương hiệu",
            "viz_type": "treemap",
            "datasource": "DimProduct",
            "sql": """
                SELECT Brand, CategoryName, COUNT(*) AS ProductCount
                FROM DimProduct
                WHERE IsCurrent = 1
                GROUP BY Brand, CategoryName
            """,
        },
    ],
    "filters": ["Time Range", "Store", "Brand", "Category"],
}
