#!/usr/bin/env python3
"""
Sync dataset columns từ MSSQL vào Superset (programmatic approach).
Sử dụng SqlaTable.fetch_metadata() để trigger column sync.
Chạy TRONG container: docker exec dwh_superset python3 /superset_scripts/sync_columns.py
"""
import os
import sys
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

DATASETS = [
    {'id': 1,  'name': 'FactSales'},
    {'id': 2,  'name': 'FactInventory'},
    {'id': 3,  'name': 'FactPurchase'},
    {'id': 4,  'name': 'DimProduct'},
    {'id': 5,  'name': 'DimCustomer'},
    {'id': 6,  'name': 'DimStore'},
    {'id': 7,  'name': 'DimEmployee'},
    {'id': 8,  'name': 'DimDate'},
    {'id': 9,  'name': 'DM_SalesSummary'},
    {'id': 10, 'name': 'DM_CustomerRFM'},
]


def sync_columns(ds_id: int, ds_name: str):
    """Force-fetch columns bằng fetch_metadata()."""
    from superset.extensions import db
    from superset.connectors.sqla.models import SqlaTable, TableColumn

    ds = db.session.query(SqlaTable).filter_by(id=ds_id).first()
    if not ds:
        logger.warning(f'[{ds_name}] Dataset not found')
        return False

    try:
        # fetch_metadata() sẽ connect MSSQL, lấy schema, tạo TableColumn records
        ds.fetch_metadata()
        db.session.commit()

        col_count = db.session.query(TableColumn).filter_by(table_id=ds_id).count()
        logger.info(f'[{ds_name}] Fetched {col_count} columns')

        # Nếu vẫn 0 columns, thử cách khác
        if col_count == 0:
            logger.warning(f'[{ds_name}] No columns fetched — trying column_utils')
            try:
                from superset.connectors.sqla.utils import get_col_type
                from sqlalchemy import inspect as sqla_inspect

                db_engine = ds.database
                engine = db_engine.get_sqla_engine()
                insp = sqla_inspect(engine)
                schema = ds.schema or 'dbo'
                cols = insp.reflecttable(
                    sqla_inspect(engine).get_table_reference(ds.table_name),
                    schema=schema
                )
                logger.info(f'[{ds_name}] Reflection got {len(cols)} cols')
            except Exception as e2:
                logger.error(f'[{ds_name}] Reflection also failed: {e2}')

        return True

    except Exception as e:
        db.session.rollback()
        logger.error(f'[{ds_name}] Fetch failed: {e}')
        return False


def main():
    logger.info('=' * 60)
    logger.info('Syncing dataset columns (fetch_metadata)')
    logger.info('=' * 60)

    from superset.app import create_app
    app = create_app()

    with app.app_context():
        success = 0
        for ds in DATASETS:
            ok = sync_columns(ds['id'], ds['name'])
            if ok:
                success += 1
            time.sleep(1)

    logger.info('=' * 60)
    logger.info(f'Sync complete: {success}/{len(DATASETS)} datasets OK')
    logger.info('Refresh dashboards in Superset UI')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())