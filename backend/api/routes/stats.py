from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import text
from models.master import User, Tenant
from schemas import StatsResponse
from api.deps import get_db, get_current_active_user, get_current_superadmin
from core.tenant import get_tenant_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stats", tags=["Stats"])


def _resolve_tenant_id(
    current_user: User,
    impersonate_tenant: str | None = None,
) -> str | None:
    """SuperAdmin có thể impersonate tenant qua header X-Impersonate-Tenant."""
    if current_user.Role == "SuperAdmin" and impersonate_tenant:
        return impersonate_tenant
    return current_user.TenantId


@router.get("", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User không thuộc tenant nào")

    try:
        with get_tenant_session() as conn:
            revenue_row = conn.execute(
                text("SELECT ISNULL(SUM(GrossSalesAmount), 0) FROM FactSales WHERE ReturnFlag = 0 AND TenantId = :tenant_id"),
                {"tenant_id": tenant_id},
            ).fetchone()
            total_revenue = float(revenue_row[0]) if revenue_row else 0.0

            orders_row = conn.execute(
                text("SELECT COUNT(*) FROM FactSales WHERE ReturnFlag = 0 AND TenantId = :tenant_id"),
                {"tenant_id": tenant_id},
            ).fetchone()
            total_orders = orders_row[0] if orders_row else 0

            # Fixed: DimCustomer has IsActive
            customers_row = conn.execute(
                text("SELECT COUNT(*) FROM DimCustomer WHERE IsActive = 1 AND TenantId = :tenant_id"),
                {"tenant_id": tenant_id},
            ).fetchone()
            total_customers = customers_row[0] if customers_row else 0

            top_products_rows = conn.execute(
                text("""
                    SELECT TOP 10
                        p.ProductName,
                        p.CategoryName,
                        SUM(f.Quantity) AS TotalQty,
                        SUM(f.NetSalesAmount) AS TotalRevenue
                    FROM FactSales f
                    JOIN DimProduct p ON p.ProductKey = f.ProductKey AND p.TenantId = f.TenantId
                    WHERE f.ReturnFlag = 0 AND p.IsCurrent = 1 AND f.TenantId = :tenant_id
                    GROUP BY p.ProductName, p.CategoryName
                    ORDER BY TotalQty DESC
                """),
                {"tenant_id": tenant_id},
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
        logger.error(f"get_stats error for tenant {tenant_id}: {e}")
        return StatsResponse(
            total_revenue=0,
            total_orders=0,
            total_customers=0,
            top_products=[],
        )


@router.get("/summary")
async def get_summary(
    current_user: User = Depends(get_current_active_user),
    x_impersonate_tenant: str | None = Header(default=None),
):
    tenant_id = _resolve_tenant_id(current_user, x_impersonate_tenant)
    if not tenant_id:
        raise HTTPException(status_code=403, detail="User không thuộc tenant nào")

    try:
        with get_tenant_session() as conn:
            monthly = conn.execute(
                text("""
                    SELECT
                        d.Year,
                        d.MonthNumber,
                        SUM(f.NetSalesAmount) AS Revenue,
                        SUM(f.GrossProfitAmount) AS Profit,
                        COUNT(*) AS OrderCount
                    FROM FactSales f
                    JOIN DimDate d ON d.DateKey = f.DateKey
                    WHERE f.ReturnFlag = 0
                      AND f.TenantId = :tenant_id
                      AND d.FullDate >= DATEADD(MONTH, -12, GETDATE())
                    GROUP BY d.Year, d.MonthNumber
                """),
                {"tenant_id": tenant_id},
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
                        s.StoreName,
                        s.City,
                        SUM(f.NetSalesAmount) AS Revenue,
                        COUNT(*) AS Orders
                    FROM FactSales f
                    JOIN DimStore s ON s.StoreKey = f.StoreKey AND s.TenantId = f.TenantId
                    WHERE f.ReturnFlag = 0
                      AND f.TenantId = :tenant_id
                    GROUP BY s.StoreName, s.City
                """),
                {"tenant_id": tenant_id},
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
    except Exception as e:
        logger.error(f"get_summary error for tenant {tenant_id}: {e}")
        return {
            "month": [],
            "stores": [],
        }
