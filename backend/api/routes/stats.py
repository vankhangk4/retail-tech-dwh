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
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    db_name = f"DWH_{tenant_id}"

    try:
        with get_tenant_session(db_name) as conn:
            # Total revenue
            revenue_row = conn.execute(
                text("SELECT ISNULL(SUM(TotalAmount), 0) FROM FactSales")
            ).fetchone()
            total_revenue = float(revenue_row[0]) if revenue_row else 0.0

            # Total orders
            orders_row = conn.execute(
                text("SELECT COUNT(*) FROM FactSales")
            ).fetchone()
            total_orders = orders_row[0] if orders_row else 0

            # Total customers
            customers_row = conn.execute(
                text("SELECT COUNT(*) FROM DimCustomer WHERE IsCurrent = 1")
            ).fetchone()
            total_customers = customers_row[0] if customers_row else 0

            # Top 10 products
            top_products_rows = conn.execute(
                text("""
                    SELECT TOP 10
                        dp.ProductName,
                        dp.Category,
                        SUM(fs.QuantitySold) as TotalQty,
                        SUM(fs.TotalAmount) as TotalRevenue
                    FROM FactSales fs
                    JOIN DimProduct dp ON fs.ProductKey = dp.ProductKey
                    WHERE dp.IsCurrent = 1
                    GROUP BY dp.ProductName, dp.Category
                    ORDER BY SUM(fs.TotalAmount) DESC
                """)
            ).fetchall()

            top_products = [
                {
                    "product_name": row[0],
                    "category": row[1],
                    "total_qty": row[2],
                    "total_revenue": float(row[3]),
                }
                for row in top_products_rows
            ]

        return StatsResponse(
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_customers=total_customers,
            top_products=top_products,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn stats: {str(e)}")


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_active_user),
):
    """Trả về tổng quan cho dashboard."""
    tenant_id = current_user.TenantId
    if not tenant_id:
        raise HTTPException(status_code=400, detail="User phải thuộc tenant")

    db_name = f"DWH_{tenant_id}"

    try:
        with get_tenant_session(db_name) as conn:
            # Monthly revenue last 12 months
            monthly = conn.execute(
                text("""
                    SELECT
                        dd.Year,
                        dd.Month,
                        SUM(fs.TotalAmount) as Revenue,
                        SUM(fs.TotalProfit) as Profit,
                        COUNT(*) as OrderCount
                    FROM FactSales fs
                    JOIN DimDate dd ON fs.DateKey = dd.DateKey
                    WHERE dd.Date >= DATEADD(MONTH, -12, GETDATE())
                    GROUP BY dd.Year, dd.Month
                    ORDER BY dd.Year, dd.Month
                """)
            ).fetchall()

            monthly_data = [
                {
                    "year": row[0],
                    "month": row[1],
                    "revenue": float(row[2]),
                    "profit": float(row[3]),
                    "orders": row[4],
                }
                for row in monthly
            ]

            # Store performance
            stores = conn.execute(
                text("""
                    SELECT TOP 5
                        ds.StoreName,
                        ds.City,
                        SUM(fs.TotalAmount) as Revenue,
                        COUNT(*) as Orders
                    FROM FactSales fs
                    JOIN DimStore ds ON fs.StoreKey = ds.StoreKey
                    WHERE ds.IsCurrent = 1
                    GROUP BY ds.StoreName, ds.City
                    ORDER BY SUM(fs.TotalAmount) DESC
                """)
            ).fetchall()

            store_data = [
                {
                    "store_name": row[0],
                    "city": row[1],
                    "revenue": float(row[2]),
                    "orders": row[3],
                }
                for row in stores
            ]

        return {
            "monthly": monthly_data,
            "stores": store_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn summary: {str(e)}")
