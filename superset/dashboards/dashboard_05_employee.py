# ============================================================
# dashboard_05_employee.py
# FR-14: Dashboard Hiệu suất Nhân viên
# ============================================================
DASHBOARD_CONFIG = {
    "dashboard_title": "FR-14: Dashboard Hiệu suất Nhân viên",
    "description": "Doanh số, hiệu quả theo nhân viên và ca làm việc",
    "charts": [
        {
            "name": "Doanh số theo Nhân viên (TOP 20)",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT TOP 20 e.FullName,
                       e.Position,
                       s.StoreName,
                       SUM(f.NetSalesAmount) AS Revenue,
                       SUM(f.GrossProfitAmount) AS Profit,
                       COUNT(DISTINCT f.InvoiceNumber) AS InvoiceCount,
                       SUM(f.Quantity) AS TotalQtySold
                FROM FactSales f
                JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
                JOIN DimStore s ON s.StoreKey = f.StoreKey
                WHERE f.ReturnFlag = 0
                GROUP BY e.FullName, e.Position, s.StoreName
                ORDER BY Revenue DESC
            """,
        },
        {
            "name": "Hiệu suất Nhân viên (Pivot Table)",
            "viz_type": "pivot_table_v2",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    e.FullName,
                    e.Position,
                    d.QuarterName,
                    SUM(f.NetSalesAmount) AS Revenue,
                    AVG(f.NetSalesAmount) AS AvgPerInvoice,
                    COUNT(DISTINCT f.InvoiceNumber) AS InvoiceCount
                FROM FactSales f
                JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
                JOIN DimDate d ON d.DateKey = f.DateKey
                WHERE f.ReturnFlag = 0
                GROUP BY e.FullName, e.Position, d.QuarterName
            """,
        },
        {
            "name": "Doanh số theo Cửa hàng",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT s.StoreName,
                       e.Position,
                       SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimStore s ON s.StoreKey = f.StoreKey
                JOIN DimEmployee e ON e.EmployeeKey = f.EmployeeKey
                WHERE f.ReturnFlag = 0
                GROUP BY s.StoreName, e.Position
            """,
        },
        {
            "name": "Phương thức Thanh toán phổ biến",
            "viz_type": "pie",
            "datasource": "FactSales",
            "sql": """
                SELECT PaymentMethod,
                       COUNT(*) AS TransactionCount,
                       SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                WHERE f.ReturnFlag = 0
                GROUP BY PaymentMethod
                ORDER BY Revenue DESC
            """,
        },
    ],
    "filters": ["Time Range", "Store", "Position", "Department"],
}
