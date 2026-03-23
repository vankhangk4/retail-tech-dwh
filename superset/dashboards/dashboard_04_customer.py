# ============================================================
# dashboard_04_customer.py
# FR-13: Dashboard Phan tich Khach hang
# ============================================================
# KHONG dung ORDER BY vi Superset tu dong sort.

DASHBOARD_CONFIG = {
    "dashboard_title": "FR-13: Phan tich Khach hang",
    "description": "Phan boc khach hang, ty le quay lai, hanh vi mua hang",
    "charts": [
        {
            "name": "So luong Khach hang theo Thang",
            "viz_type": "line",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    d.Year,
                    d.MonthNumber,
                    COUNT(DISTINCT f.CustomerKey) AS CustomerCount,
                    COUNT(DISTINCT f.InvoiceNumber) AS TransactionCount
                FROM FactSales f
                JOIN DimDate d ON d.DateKey = f.DateKey
                WHERE f.ReturnFlag = 0
                GROUP BY d.Year, d.MonthNumber
            """,
        },
        {
            "name": "Khach hang theo Loai",
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
            "name": "Khach hang theo Thanh pho",
            "viz_type": "bar",
            "datasource": "DimCustomer",
            "sql": """
                SELECT TOP 20
                    City,
                    COUNT(*) AS CustomerCount
                FROM DimCustomer
                WHERE IsActive = 1
                GROUP BY City
            """,
        },
        {
            "name": "Doanh thu theo Nhom tuoi",
            "viz_type": "bar",
            "datasource": "FactSales",
            "sql": """
                SELECT
                    c.AgeGroup,
                    SUM(f.NetSalesAmount) AS Revenue
                FROM FactSales f
                JOIN DimCustomer c ON c.CustomerKey = f.CustomerKey
                WHERE f.ReturnFlag = 0
                GROUP BY c.AgeGroup
            """,
        },
    ],
    "filters": ["Time Range", "Customer Type", "City"],
}
