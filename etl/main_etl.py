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

    if not tenant_id:
        raise ValueError("tenant_id is required for shared multi-tenant ETL")

    db_label = config.MSSQL_DATABASE
    batch_date_str = batch_date.strftime("%Y-%m-%d")

    logger.info("")
    logger.info("=" * 60)
    logger.info(f"  ETL PIPELINE STARTED | DB: {db_label} | BatchDate: {batch_date_str}")
    logger.info(f"  Tenant: {tenant_id}")
    logger.info("=" * 60)

    loader = StagingLoader(conn_str=conn_str)
    total_rows = 0
    overall_status = "SUCCESS"
    stg_row_counts = {}
    fact_ran = set()

    # Registry / dependency map
    source_configs = [
        ("sales", "SALES_FILE", extract_sales, "STG_SalesRaw", True, "Sales"),
        ("inventory", "INVENTORY_FILE", extract_inventory, "STG_InventoryRaw", True, "Inventory"),
        ("product", "PRODUCT_FILE", extract_product, "STG_ProductRaw", False, "Product"),
        ("customer", "CUSTOMER_FILE", extract_customer, "STG_CustomerRaw", False, "Customer"),
        ("store", "STORE_FILE", extract_store, "STG_StoreRaw", False, "Store"),
        ("employee", "EMPLOYEE_FILE", extract_employee, "STG_EmployeeRaw", False, "Employee"),
        ("supplier", "SUPPLIER_FILE", extract_supplier, "STG_SupplierRaw", False, "Supplier"),
    ]

    dim_sp_by_stg = {
        "STG_SupplierRaw": "sp_Load_DimSupplier",
        "STG_ProductRaw": "sp_Load_DimProduct",
        "STG_CustomerRaw": "sp_Load_DimCustomer",
        "STG_StoreRaw": "sp_Load_DimStore",
        "STG_EmployeeRaw": "sp_Load_DimEmployee",
    }

    fact_sp_by_stg = {
        "STG_SalesRaw": (
            "sp_Load_FactSales",
            {
                "BatchDate": batch_date_str,
                "FullLoad": 1 if full_load else 0,
                "TenantId": tenant_id,
            },
        ),
        "STG_InventoryRaw": (
            "sp_Load_FactInventory",
            {
                "BatchDate": batch_date_str,
                "FullLoad": 1 if full_load else 0,
                "TenantId": tenant_id,
            },
        ),
    }

    dm_sp_by_fact = {
        "sp_Load_FactSales": (
            "sp_Refresh_DM_SalesSummary",
            {"BatchDate": batch_date_str, "TenantId": tenant_id},
        ),
        "sp_Load_FactInventory": (
            "sp_Refresh_DM_InventoryAlert",
            {"TenantId": tenant_id},
        ),
    }

    watermark_date_sql_by_stg = {
        "STG_SalesRaw": "SELECT ISNULL(MAX(NgayBan), GETDATE()) FROM STG_SalesRaw",
        "STG_InventoryRaw": "SELECT ISNULL(MAX(NgayChot), GETDATE()) FROM STG_InventoryRaw",
    }

    try:
        # =============================================
        # PHASE 1: EXTRACT → LOAD TO STAGING
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 1] EXTRACT & LOAD TO STAGING")

        if full_load:
            watermark = datetime(2020, 1, 1)
            logger.info("Full load mode: ignoring watermarks")
        else:
            watermark = get_watermark("STG_SalesRaw", conn_str=conn_str)

        for src_name, file_key, extractor_fn, stg_table, use_watermark, label in source_configs:
            file_path = Path(file_paths[file_key])
            if not file_path.exists():
                logger.warning(f"{label} file not found: {file_path}")
                continue

            try:
                if use_watermark:
                    df = extractor_fn(file_path, watermark)
                else:
                    df = extractor_fn(file_path)

                if df.empty:
                    logger.info(f"  {label}: no data extracted, skipped")
                    continue

                rows = loader.load(df, stg_table, if_exists="truncate")
                if rows > 0:
                    stg_row_counts[stg_table] = rows
                    total_rows += rows
                logger.info(f"  {label}: {rows} rows loaded")
            except Exception as e:
                logger.error(f"  {label} extraction failed: {e}")

        # =============================================
        # PHASE 2: LOAD DIMENSIONS (selective)
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 2] LOAD DIMENSIONS")

        for stg_table, sp in dim_sp_by_stg.items():
            if stg_table not in stg_row_counts:
                logger.info(f"  {sp} skipped (no data in {stg_table})")
                continue
            try:
                run_stored_procedure(sp, {"TenantId": tenant_id}, conn_str=conn_str)
            except Exception as e:
                logger.error(f"  {sp} failed: {e}")

        # =============================================
        # PHASE 3: LOAD FACTS (selective)
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 3] LOAD FACTS")

        for stg_table, (sp_name, params) in fact_sp_by_stg.items():
            if stg_table not in stg_row_counts:
                logger.info(f"  {sp_name} skipped (no data in {stg_table})")
                continue
            try:
                ok = run_stored_procedure(sp_name, params, conn_str=conn_str)
                if ok:
                    fact_ran.add(sp_name)
            except Exception as e:
                logger.error(f"  {sp_name} failed: {e}")

        # Skip FactPurchase by default (no source file in upload-driven flow)
        logger.info("  sp_Load_FactPurchase skipped (no upload source mapping)")

        # =============================================
        # PHASE 4: REFRESH DATA MARTS (selective)
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 4] REFRESH DATA MARTS")

        for fact_sp, (dm_sp, dm_params) in dm_sp_by_fact.items():
            if fact_sp not in fact_ran:
                logger.info(f"  {dm_sp} skipped ({fact_sp} not executed)")
                continue
            try:
                run_stored_procedure(dm_sp, dm_params, conn_str=conn_str)
            except Exception as e:
                logger.error(f"  {dm_sp} failed: {e}")

        # =============================================
        # PHASE 5: UPDATE WATERMARKS (selective)
        # =============================================
        logger.info("")
        logger.info(">>> [PHASE 5] UPDATE WATERMARKS")

        try:
            for stg_table, rows in stg_row_counts.items():
                try:
                    if stg_table in watermark_date_sql_by_stg:
                        conn = pyodbc.connect(conn_str)
                        cursor = conn.cursor()
                        cursor.execute(watermark_date_sql_by_stg[stg_table])
                        wm_date = cursor.fetchone()[0]
                        cursor.close()
                        conn.close()
                    else:
                        wm_date = datetime.now()

                    conn = pyodbc.connect(conn_str)
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE ETL_Watermark
                           SET LastRunStatus = 'SUCCESS',
                               LastRunDatetime = GETDATE(),
                               WatermarkValue = ?,
                               RowsExtracted = ?
                           WHERE SourceName = ?""",
                        (wm_date, rows, stg_table)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    logger.info(f"  Watermark updated: {stg_table} = {wm_date}")
                except Exception as e:
                    logger.error(f"  Watermark update failed for {stg_table}: {e}")
        except Exception as e:
            logger.error(f"  Failed to update watermarks: {e}")

        if total_rows == 0:
            overall_status = "SKIPPED"

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
