from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from models.master import User, Tenant
from schemas import StatsResponse
from api.deps import get_db, get_current_active_user
from core.tenant import get_tenant_session

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_active_user),
):
    tenant_id = current_user.TenantId
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User không thuộc tenant nào")

    db_name = "DWH_" + str(tenant_id)

    try:
        with get_tenant_session(db_name) as conn:
            revenue_row = conn.execute(
                text("SELECT ISNULL(SUM(GrossSalesAmount), 0) FROM FactSales")
            ).fetchone()
            total_revenue = float(revenue_row[0]) if revenue_row else 0.0

            orders_row = conn.execute(
                text("SELECT COUNT(*) FROM FactSales")
            ).fetchone()
            total_orders = orders_row[0] if orders_row else 0

            customers_row = conn.execute(
                text("SELECT COUNT(*) FROM DimCustomer WHERE IsCurrent = 1")
            ).fetchone()
            total_customers = customers_row[0] if customers_row else 0

            top_products_rows = conn.execute(
                text("""
                    SELECT TOP 10
                        dp.ProductName,
                        dp.Category,
                        SUM(fs.Quantity) as TotalQty,
                        SUM(fs.GrossSalesAmount) as TotalRevenue
                    FROM FactSales fs
                    JOIN DimProduct dp ON fs.ProductKey = dp.ProductKey
                    WHERE dp.IsCurrent = 1
                    GROUP BY dp.ProductName, dp.Category
                    ORDER BY SUM(fs.GrossSalesAmount) DESC
                """)
            ).fetchall()

            top_products = []
            for row in top_products_rows:
                top_products.append({
                    "product_name": row[0],
                    "category": row[1],
                    "total_qty": row[2],
                    "total_revenue": float(row[3]) if row[3] else 0,
                })

        return StatsResponse(
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_customers=total_customers,
            top_products=top_products,
        )
    except Exception as e:
        # Database chưa init hoặc chưa có data -> trả empty
        return StatsResponse(
            total_revenue=0,
            total_orders=0,
            total_customers=0,
            top_products=[],
        )


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_active_user),
):
    tenant_id = current_user.TenantId
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User không thuộc tenant nào")

    db_name = "DWH_" + str(tenant_id)

    try:
        with get_tenant_session(db_name) as conn:
            monthly = conn.execute(
                text("""
                    SELECT
                        dd.Year,
                        dd.Month,
                        SUM(fs.GrossSalesAmount) as Revenue,
                        SUM(fs.NetSalesAmount) as Profit,
                        COUNT(*) as OrderCount
                    FROM FactSales fs
                    JOIN DimDate dd ON fs.DateKey = dd.DateKey
                    WHERE dd.Date >= DATEADD(MONTH, -12, GETDATE())
                    GROUP BY dd.Year, dd.Month
                    ORDER BY dd.Year, dd.Month
                """)
            ).fetchall()

            monthly_data = []
            for row in monthly:
                monthly_data.append({
                    "year": row[0],
                    "month": row[1],
                    "revenue": float(row[2]) if row[2] else 0,
                    "profit": float(row[3]) if row[3] else 0,
                    "orders": row[4],
                })

            stores = conn.execute(
                text("""
                    SELECT TOP 5
                        ds.StoreName,
                        ds.City,
                        SUM(fs.GrossSalesAmount) as Revenue,
                        COUNT(*) as Orders
                    FROM FactSales fs
                    JOIN DimStore ds ON fs.StoreKey = ds.StoreKey
                    WHERE ds.IsCurrent = 1
                    GROUP BY ds.StoreName, ds.City
                    ORDER BY SUM(fs.GrossSalesAmount) DESC
                """)
            ).fetchall()

            store_data = []
            for row in stores:
                store_data.append({
                    "store_name": row[0],
                    "city": row[1],
                    "revenue": float(row[2]) if row[2] else 0,
                    "orders": row[3],
                })

        return {
            "monthly": monthly_data,
            "stores": store_data,
        }
    except Exception:
        # Database chưa init hoặc chưa có data -> trả empty
        return {
            "monthly": [],
            "stores": [],
        }
