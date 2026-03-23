# ============================================================
# dashboard_02_product.py
# FR-11: Dashboard Phan tich San pham
# ============================================================
# KHONG dung ORDER BY vi Superset tu dong sort.

DASHBOARD_CONFIG = {
    "dashboard_title": "FR-11: Phan tich San pham",
    "description": "TOP ban chay, dong gop doanh thu, bien loi nhuan theo san pham",
    "charts": [
        {
            "name": "TOP 10 San pham ban chay",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT TOP 10
                    p.ProductName,
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
            "name": "Doanh thu theo Danh muc",
            "viz_type": "pie",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    p.CategoryName,
                    SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey
                WHERE f.ReturnFlag = 0
                GROUP BY p.CategoryName
            """,
        },
        {
            "name": "Bien loi nhuan theo San pham",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT TOP 20
                    p.ProductName,
                    CASE
                        WHEN SUM(f.NetSalesAmount) > 0
                        THEN ROUND(SUM(f.GrossProfitAmount) * 100.0 / SUM(f.NetSalesAmount), 2)
                        ELSE 0
                    END AS ProfitMarginPct
                FROM FactSales f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey
                WHERE f.ReturnFlag = 0
                GROUP BY p.ProductName
            """,
        },
        {
            "name": "San pham theo Thuong hieu",
            "viz_type": "pie",
            "datasource": "DimProduct",
            "sql": """
                SELECT Brand, COUNT(*) AS ProductCount
                FROM DimProduct
                WHERE IsCurrent = 1
                GROUP BY Brand
            """,
        },
    ],
    "filters": ["Time Range", "Store", "Brand", "Category"],
}
