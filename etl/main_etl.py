# ============================================================
# main_etl.py - ETL Orchestrator
# Entry point cho toàn bộ pipeline ETL
# ============================================================
import sys
import logging
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import pyodbc
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from etl import config
from etl.logger import setup_logger
from etl.load.load_to_staging import StagingLoader

# Import extractors
from etl.extract.extract_sales import extract_sales
from etl.extract.extract_inventory import extract_inventory
from etl.extract.extract_product import extract_product
from etl.extract.extract_customer import extract_customer
from etl.extract.extract_store import extract_store
from etl.extract.extract_employee import extract_employee
from etl.extract.extract_supplier import extract_supplier

logger = setup_logger("etl.main")


def get_watermark(source_name: str, conn_str: str = None) -> datetime:
    """Lấy watermark từ database."""
    try:
        conn = pyodbc.connect(conn_str or config.CONN_STR)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT WatermarkValue FROM ETL_Watermark WHERE SourceName = ?",
            (source_name,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if row and row[0]:
            return row[0]
        return datetime(2020, 1, 1)
    except Exception as e:
        logger.warning(f"Failed to get watermark for {source_name}: {e}. Using default.")
        return datetime(2020, 1, 1)


def run_stored_procedure(sp_name: str, params: dict = None, conn_str: str = None) -> bool:
    """Thực thi stored procedure trên SQL Server."""
    try:
        conn = pyodbc.connect(conn_str or config.CONN_STR)
        cursor = conn.cursor()
        if params:
            param_str = ", ".join([f"@{k}=?" for k in params.keys()])
            cursor.execute(f"EXEC {sp_name} {param_str}", list(params.values()))
        else:
            cursor.execute(f"EXEC {sp_name}")
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Executed SP: {sp_name}")
        return True
    except Exception as e:
        logger.error(f"SP execution failed - {sp_name}: {e}")
        return False


def log_run(
    pipeline_name: str,
    step_name: str,
    status: str,
    rows_processed: int = None,
    error: str = None,
    conn_str: str = None
):
    """Ghi log vào ETL_RunLog."""
    try:
        conn = pyodbc.connect(conn_str or config.CONN_STR)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO ETL_RunLog
               (RunDate, PipelineName, StepName, Status, RowsProcessed, ErrorMessage, LoadDatetime)
               VALUES (?, ?, ?, ?, ?, ?, GETDATE())""",
            (date.today(), pipeline_name, step_name, status, rows_processed, error)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to write to ETL_RunLog: {e}")


def etl_run(batch_date: Optional[date] = None, full_load: bool = False, tenant_id: str = None):
    """
    Chạy toàn bộ ETL pipeline.

    Args:
        batch_date: Ngày xử lý (mặc định: hôm nay)
        full_load: Nếu True, bỏ qua watermark và load tất cả
        tenant_id: Tenant context để gắn TenantId vào Dim/Fact trong shared DB
    """
    if batch_date is None:
        batch_date = date.today()

    # Shared DB model: always use one DB, tenant_id is logical context only.
    conn_str = config.CONN_STR
    if tenant_id:
        file_paths = config.get_tenant_file_paths(tenant_id)
    else:
        file_paths = {
            "SALES_FILE": config.SALES_FILE,
            "INVENTORY_FILE": config.INVENTORY_FILE,
            "PRODUCT_FILE": config.PRODUCT_FILE,
            "CUSTOMER_FILE": config.CUSTOMER_FILE,
            "STORE_FILE": config.STORE_FILE,
            "EMPLOYEE_FILE": config.EMPLOYEE_FILE,
            "SUPPLIER_FILE": config.SUPPLIER_FILE,
        }
    db_label = config.MSSQL_DATABASE

    batch_date_str = batch_date.strftime("%Y-%m-%d")
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"  ETL PIPELINE STARTED | DB: {db_label} | BatchDate: {batch_date_str}")
    if tenant_id:
        logger.info(f"  Tenant: {tenant_id}")
    logger.info("=" * 60)

    loader = StagingLoader(conn_str=conn_str)
    total_rows = 0
    overall_status = "SUCCESS"

    try:
        # =============================================
        # PHASE 1: EXTRACT → LOAD TO STAGING
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 1] EXTRACT & LOAD TO STAGING")

        # Get watermarks
        if full_load:
            watermark = datetime(2020, 1, 1)
            logger.info("Full load mode: ignoring watermarks")
        else:
            watermark = get_watermark("STG_SalesRaw", conn_str=conn_str)

        # Extract & Load: Sales
        try:
            df_sales = extract_sales(file_paths["SALES_FILE"], watermark)
            if not df_sales.empty:
                rows = loader.load(df_sales, "STG_SalesRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Sales: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Sales extraction failed: {e}")

        # Extract & Load: Inventory
        try:
            df_inv = extract_inventory(file_paths["INVENTORY_FILE"], watermark)
            if not df_inv.empty:
                rows = loader.load(df_inv, "STG_InventoryRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Inventory: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Inventory extraction failed: {e}")

        # Extract & Load: Product
        try:
            df_prod = extract_product(file_paths["PRODUCT_FILE"])
            if not df_prod.empty:
                rows = loader.load(df_prod, "STG_ProductRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Product: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Product extraction failed: {e}")

        # Extract & Load: Customer
        try:
            df_cust = extract_customer(file_paths["CUSTOMER_FILE"])
            if not df_cust.empty:
                rows = loader.load(df_cust, "STG_CustomerRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Customer: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Customer extraction failed: {e}")

        # Extract & Load: Store
        try:
            df_store = extract_store(file_paths["STORE_FILE"])
            if not df_store.empty:
                rows = loader.load(df_store, "STG_StoreRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Store: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Store extraction failed: {e}")

        # Extract & Load: Employee
        try:
            df_emp = extract_employee(file_paths["EMPLOYEE_FILE"])
            if not df_emp.empty:
                rows = loader.load(df_emp, "STG_EmployeeRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Employee: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Employee extraction failed: {e}")

        # Extract & Load: Supplier
        try:
            df_sup = extract_supplier(file_paths["SUPPLIER_FILE"])
            if not df_sup.empty:
                rows = loader.load(df_sup, "STG_SupplierRaw", if_exists="truncate")
                total_rows += rows
                logger.info(f"  Supplier: {rows} rows loaded")
        except Exception as e:
            logger.error(f"  Supplier extraction failed: {e}")

        # =============================================
        # PHASE 2: LOAD DIMENSIONS
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 2] LOAD DIMENSIONS")

        dim_sps = [
            "sp_Load_DimSupplier",
            "sp_Load_DimProduct",
            "sp_Load_DimCustomer",
            "sp_Load_DimStore",
            "sp_Load_DimEmployee",
        ]
        if not tenant_id:
            raise ValueError("tenant_id is required for shared multi-tenant ETL")

        for sp in dim_sps:
            try:
                run_stored_procedure(sp, {"TenantId": tenant_id}, conn_str=conn_str)
            except Exception as e:
                logger.error(f"  {sp} failed: {e}")

        # =============================================
        # PHASE 3: LOAD FACTS
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 3] LOAD FACTS")

        fact_sps = [
            (
                "sp_Load_FactSales",
                {
                    "BatchDate": batch_date_str,
                    "FullLoad": 1 if full_load else 0,
                    "TenantId": tenant_id,
                },
            ),
            (
                "sp_Load_FactInventory",
                {
                    "BatchDate": batch_date_str,
                    "FullLoad": 1 if full_load else 0,
                    "TenantId": tenant_id,
                },
            ),
            ("sp_Load_FactPurchase", {"BatchDate": batch_date_str, "TenantId": tenant_id}),
        ]
        for sp_name, params in fact_sps:
            try:
                run_stored_procedure(sp_name, params, conn_str=conn_str)
            except Exception as e:
                logger.error(f"  {sp_name} failed: {e}")

        # =============================================
        # PHASE 4: REFRESH DATA MARTS
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 4] REFRESH DATA MARTS")

        try:
            run_stored_procedure(
                "sp_Refresh_DM_SalesSummary",
                {"BatchDate": batch_date_str, "TenantId": tenant_id},
                conn_str=conn_str,
            )
        except Exception as e:
            logger.error(f"  sp_Refresh_DM_SalesSummary failed: {e}")

        try:
            run_stored_procedure(
                "sp_Refresh_DM_InventoryAlert",
                {"TenantId": tenant_id},
                conn_str=conn_str,
            )
        except Exception as e:
            logger.error(f"  sp_Refresh_DM_InventoryAlert failed: {e}")

        # =============================================
        # PHASE 5: UPDATE WATERMARKS
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 5] UPDATE WATERMARKS")

        try:
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            # Get actual max dates from staging data
            cursor.execute("SELECT ISNULL(MAX(NgayBan), GETDATE()) FROM STG_SalesRaw")
            max_sales_date = cursor.fetchone()[0]
            cursor.execute("SELECT ISNULL(MAX(NgayChot), GETDATE()) FROM STG_InventoryRaw")
            max_inv_date = cursor.fetchone()[0]
            cursor.close()
            conn.close()

            # Update watermarks with actual data dates
            updates = [
                ("STG_SalesRaw",     max_sales_date, total_rows),
                ("STG_InventoryRaw", max_inv_date,    total_rows),
                ("STG_ProductRaw",   datetime.now(),  total_rows),
                ("STG_CustomerRaw",  datetime.now(),  total_rows),
                ("STG_StoreRaw",     datetime.now(),  total_rows),
                ("STG_EmployeeRaw",  datetime.now(),  total_rows),
                ("STG_SupplierRaw",  datetime.now(),  total_rows),
            ]
            for src, wm_date, rows in updates:
                try:
                    conn = pyodbc.connect(conn_str)
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE ETL_Watermark
                           SET LastRunStatus = 'SUCCESS',
                               LastRunDatetime = GETDATE(),
                               WatermarkValue = ?,
                               RowsExtracted = ?
                           WHERE SourceName = ?""",
                        (wm_date, rows, src)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logger.info(f"  Watermark updated: {src} = {wm_date}")
                except Exception as e:
                    logger.error(f"  Watermark update failed for {src}: {e}")
        except Exception as e:
            logger.error(f"  Failed to get max dates: {e}")

        logger.info("")
        logger.info("=" * 60)
        logger.info(f"  ETL PIPELINE COMPLETED | DB: {db_label} | Status: {overall_status}")
        logger.info(f"  Total rows processed: {total_rows}")
        logger.info("=" * 60)

    except Exception as e:
        overall_status = "FAILED"
        logger.error(f"ETL PIPELINE FAILED: {e}", exc_info=True)
        log_run("ETL_Main", "Orchestrator", "FAILED", total_rows, str(e), conn_str=conn_str)

    finally:
        loader.close()


def run_scheduled():
    """Entry point cho scheduler."""
    scheduler = BlockingScheduler()
    scheduler.add_job(
        etl_run,
        CronTrigger(hour=2, minute=0),
        id="daily_etl",
        name="Daily ETL Run (02:00 AM)",
        replace_existing=True
    )
    logger.info("Scheduler started. ETL will run daily at 02:00 AM.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ETL Pipeline for DWH_RetailTech")
    parser.add_argument("--date", type=str, help="Batch date (YYYY-MM-DD)")
    parser.add_argument("--full", action="store_true", help="Full load (ignore watermark)")
    parser.add_argument("--schedule", action="store_true", help="Run as scheduled job")
    parser.add_argument("--tenant", type=str, help="Tenant ID (chạy ETL cho database DWH_{tenant_id})")

    args = parser.parse_args()

    if args.schedule:
        run_scheduled()
    else:
        batch_date = None
        if args.date:
            batch_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        etl_run(batch_date=batch_date, full_load=args.full, tenant_id=args.tenant)
