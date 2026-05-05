#!/usr/bin/env python3
"""
Clean Superset provisioning - creates dashboards and charts with proper configs.
This script is simpler and more robust than provision_v2.py
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main provisioning logic"""
    from superset.extensions import db
    from superset.models.core import Database
    from superset.models.slice import Slice
    from superset.models.dashboard import Dashboard
    from superset.connectors.sqla.models import SqlaTable

    try:
        # Step 1: Check if MSSQL database exists
        mssql_db = db.session.query(Database).filter_by(database_name='DWH_MultiTenant_MSSQL').first()
        if not mssql_db:
            logger.warning('[PROV] MSSQL database not found - skipping dashboard creation')
            return False

        logger.info('[PROV] Found MSSQL database')

        # Step 2: Get FactSales dataset
        fact_sales = db.session.query(SqlaTable).filter_by(
            table_name='FactSales',
            database_id=mssql_db.id
        ).first()

        if not fact_sales:
            logger.warning('[PROV] FactSales table not found')
            return False

        logger.info(f'[PROV] Found FactSales table (id={fact_sales.id})')

        # Step 3: Create a simple bar chart
        chart_params = {
            'viz_type': 'bar',
            'datasource': f'{fact_sales.id}__table',
            'groupby': ['EmployeeName'],
            'metrics': [
                {
                    'expressionType': 'SIMPLE',
                    'column': {
                        'column_name': 'Revenue',
                        'type': 'NUMERIC'
                    },
                    'aggregate': 'SUM',
                    'label': 'SUM(Revenue)',
                    'sqlExpression': None
                }
            ],
            'order_desc': True,
            'row_limit': 100,
        }

        # Check if chart already exists
        existing_chart = db.session.query(Slice).filter_by(
            slice_name='Doanh số theo nhân viên',
            datasource_id=fact_sales.id
        ).first()

        if not existing_chart:
            chart = Slice(
                slice_name='Doanh số theo nhân viên',
                description='Revenue by employee',
                datasource_id=fact_sales.id,
                datasource_type='table',
                viz_type='bar',
                params=json.dumps(chart_params),
                cache_timeout=300,
            )
            db.session.add(chart)
            db.session.commit()
            logger.info('[PROV] Created chart "Doanh số theo nhân viên"')
            chart_id = chart.id
        else:
            logger.info('[PROV] Chart already exists')
            chart_id = existing_chart.id

        # Step 4: Create dashboard
        existing_dash = db.session.query(Dashboard).filter_by(slug='test').first()
        if not existing_dash:
            dashboard = Dashboard(
                dashboard_title='Test Dashboard',
                slug='test',
                description='Test dashboard with one chart'
            )
            dashboard.slices.append(db.session.query(Slice).get(chart_id))
            db.session.add(dashboard)
            db.session.commit()
            logger.info('[PROV] Created dashboard')
        else:
            logger.info('[PROV] Dashboard already exists')

        logger.info('[PROV] ✓ Provisioning complete')
        return True

    except Exception as e:
        logger.error(f'[PROV] Error: {e}')
        db.session.rollback()
        return False


if __name__ == '__main__':
    os.environ['SUPERSET_CONFIG_PATH'] = '/app/pythonpath/superset_config.py'
    from superset.app import create_app

    app = create_app()
    with app.app_context():
        success = main()
        sys.exit(0 if success else 1)
