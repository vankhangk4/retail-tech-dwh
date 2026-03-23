# ============================================================
# dashboard_05_employee.py
# FR-14: Dashboard Hieu suat Nhan vien
# ============================================================
# KHONG dung ORDER BY vi Superset tu dong sort.

DASHBOARD_CONFIG = {
    "dashboard_title": "FR-14: Hieu suat Nhan vien",
    "description": "Doanh so, hieu qua theo nhan vien va ca lam viec",
    "charts": [
        {
            "name": "TOP 20 Nhan vien theo Doanh so",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT TOP 20
                    e.FullName,
                    e.Position,
                    s.StoreName,
                    SUM(f.NetSalesAmount) AS Revenue,
                    SUM(f.GrossProfitAmount) AS Profit
                FROM FactSales f
                JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
                JOIN DimStore s ON s.StoreKey = f.StoreKey
                WHERE f.ReturnFlag = 0
                GROUP BY e.FullName, e.Position, s.StoreName
            """,
        },
        {
            "name": "Doanh so theo Bo phan",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    e.Department,
                    SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
                WHERE f.ReturnFlag = 0
                GROUP BY e.Department
            """,
        },
        {
            "name": "Doanh so theo Cua hang",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    s.StoreName,
                    e.Department,
                    SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimStore s ON s.StoreKey = f.StoreKey
                JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
                WHERE f.ReturnFlag = 0
                GROUP BY s.StoreName, e.Department
            """,
        },
        {
            "name": "Phuong thuc Thanh toan",
            "viz_type": "pie",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    PaymentMethod,
                    COUNT(*) AS TransactionCount,
                    SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                WHERE f.ReturnFlag = 0
                GROUP BY PaymentMethod
            """,
        },
    ],
    "filters": ["Time Range", "Store", "Department"],
}
