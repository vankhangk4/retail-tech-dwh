# ============================================================
# dashboard_03_inventory.py
# FR-12: Dashboard Quản lý Tồn kho
# ============================================================
DASHBOARD_CONFIG = {
    "dashboard_title": "FR-12: Dashboard Quản lý Tồn kho",
    "description": "Cảnh báo tồn kho thấp, xu hướng tồn kho, dự báo",
    "charts": [
        {
            "name": "Cảnh báo Tồn kho thấp",
            "viz_type": "table",
            "datasource": "DM_InventoryAlert",
            "sql": """
                SELECT
                    p.ProductName,
                    s.StoreName,
                    da.AlertLevel,
                    da.CurrentStock,
                    da.ReorderPoint,
                    da.DaysOfSupply,
                    da.SuggestedOrderQty,
                    da.AlertDate
                FROM DM_InventoryAlert da
                JOIN DimProduct p ON p.ProductKey = da.ProductKey
                JOIN DimStore s ON s.StoreKey = da.StoreKey
                WHERE da.IsAcknowledged = 0
                ORDER BY
                    CASE da.AlertLevel WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
                    da.CurrentStock ASC
            """,
        },
        {
            "name": "Giá trị Tồn kho theo Ngày",
            "viz_type": "line",
            "datasource": "FactInventory",
            "sql": """
                SELECT d.FullDate,
                       SUM(f.TotalInventoryValue) AS TotalInventoryValue,
                       SUM(f.ClosingStock) AS TotalUnits
                FROM FactInventory f
                JOIN DimDate d ON d.DateKey = f.DateKey
                GROUP BY d.FullDate
                ORDER BY d.FullDate
            """,
        },
        {
            "name": "Tồn kho theo Cửa hàng",
            "viz_type": "bar",
            "datasource": "FactInventory",
            "sql": """
                SELECT s.StoreName,
                       SUM(f.TotalInventoryValue) AS InventoryValue,
                       SUM(f.ClosingStock) AS TotalUnits
                FROM FactInventory f
                JOIN DimStore s ON s.StoreKey = f.StoreKey
                GROUP BY s.StoreName
                ORDER BY InventoryValue DESC
            """,
        },
        {
            "name": "Phân bố Cảnh báo theo Mức độ",
            "viz_type": "pie",
            "datasource": "DM_InventoryAlert",
            "sql": """
                SELECT AlertLevel, COUNT(*) AS AlertCount
                FROM DM_InventoryAlert
                WHERE IsAcknowledged = 0
                GROUP BY AlertLevel
            """,
        },
    ],
    "filters": ["Alert Level", "Store", "Time Range"],
}
