# ============================================================
# dashboard_03_inventory.py
# FR-12: Dashboard Quan ly Ton kho
# ============================================================
# KHONG dung ORDER BY vi Superset tu dong sort.

DASHBOARD_CONFIG = {
    "dashboard_title": "FR-12: Quan ly Ton kho",
    "description": "Canh bao ton kho thap, xu huong ton kho",
    "charts": [
        {
            "name": "Gia tri Ton kho theo Ngay",
            "viz_type": "line",
            "datasource": "FactInventory",
            "sql": """
                SELECT
                    d.FullDate,
                    SUM(f.TotalInventoryValue) AS TotalInventoryValue,
                    SUM(f.ClosingStock) AS TotalUnits
                FROM FactInventory f
                JOIN DimDate d ON d.DateKey = f.DateKey
                GROUP BY d.FullDate
            """,
        },
        {
            "name": "Ton kho theo Cua hang",
            "viz_type": "bar",
            "datasource": "FactInventory",
            "sql": """
                SELECT TOP 10
                    s.StoreName,
                    SUM(f.TotalInventoryValue) AS InventoryValue,
                    SUM(f.ClosingStock) AS TotalUnits
                FROM FactInventory f
                JOIN DimStore s ON s.StoreKey = f.StoreKey AND s.TenantId = f.TenantId
                GROUP BY s.StoreName
            """,
        },
        {
            "name": "Ton kho theo San pham (TOP 20)",
            "viz_type": "bar",
            "datasource": "FactInventory",
            "sql": """
                SELECT TOP 20
                    p.ProductName,
                    SUM(f.ClosingStock) AS CurrentStock
                FROM FactInventory f
                JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.TenantId = f.TenantId
                GROUP BY p.ProductName
            """,
        },
        {
            "name": "So luong ton kho theo Thang",
            "viz_type": "line",
            "datasource": "FactInventory",
            "sql": """
                SELECT
                    d.Year,
                    d.MonthNumber,
                    SUM(f.ClosingStock) AS TotalClosingStock
                FROM FactInventory f
                JOIN DimDate d ON d.DateKey = f.DateKey
                GROUP BY d.Year, d.MonthNumber
            """,
        },
    ],
    "filters": ["Time Range", "Store", "Product"],
}
