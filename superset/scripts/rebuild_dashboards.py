#!/usr/bin/env python3
"""
Rebuild all dashboards and charts from scratch.
This is a simplified version that handles all the provisioning properly.
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Configuration
ADMIN_USER = os.environ.get('SUPERSET_ADMIN_USER', 'admin')
ADMIN_PWD = os.environ.get('SUPERSET_ADMIN_PWD', 'M1tjtnrx')
MSSQL_URI = os.environ.get(
    'MSSQL_DATABASE_URL',
    'mssql+pymssql://sa:M1tjtnrx@mssql:1433/DWH_MultiTenant'
)

def rebuild_dashboards():
    """Rebuild all dashboards and charts"""
    from superset.extensions import db
    from superset.models.core import Database
    from superset.models.slice import Slice
    from superset.models.dashboard import Dashboard
    from superset.connectors.sqla.models import SqlaTable

    try:
        # Clean up old data
        logger.info('[REBUILD] Deleting old dashboards and charts...')
        db.session.query(Dashboard).delete()
        db.session.query(Slice).delete()
        db.session.commit()
        logger.info('[REBUILD] Old data deleted')

        # Get or create MSSQL database
        logger.info('[REBUILD] Setting up MSSQL database connection...')
        mssql_db = db.session.query(Database).filter_by(
            database_name='DWH_MultiTenant_MSSQL'
        ).first()

        if not mssql_db:
            logger.warning('[REBUILD] MSSQL database not configured')
            return False

        logger.info('[REBUILD] MSSQL database ready')

        # Get FactSales table
        fact_sales = db.session.query(SqlaTable).filter_by(
            table_name='FactSales',
            database_id=mssql_db.id
        ).first()

        if not fact_sales:
            logger.warning('[REBUILD] FactSales table not found')
            return False

        logger.info(f'[REBUILD] Found FactSales table (id={fact_sales.id})')

        # Create charts with proper column configuration
        charts = []

        # Chart 1: Revenue by Employee (bar chart)
        chart1 = Slice(
            slice_name='Revenue by Employee',
            description='Total revenue by employee',
            datasource_id=fact_sales.id,
            datasource_type='table',
            viz_type='bar',
            params=json.dumps({
                'viz_type': 'bar',
                'datasource': f'{fact_sales.id}__table',
                'groupby': ['EmployeeName'],
                'metrics': [{
                    'expressionType': 'SIMPLE',
                    'column': {'column_name': 'Revenue', 'type': 'NUMERIC'},
                    'aggregate': 'SUM',
                    'label': 'Total Revenue'
                }],
                'order_desc': True,
                'row_limit': 100,
            }),
        )
        db.session.add(chart1)
        db.session.commit()
        charts.append({'id': chart1.id, 'name': chart1.slice_name})
        logger.info(f'[REBUILD] Created chart: {chart1.slice_name}')

        # Chart 2: Quantity by Product (bar chart)
        chart2 = Slice(
            slice_name='Quantity by Product',
            description='Total quantity by product',
            datasource_id=fact_sales.id,
            datasource_type='table',
            viz_type='bar',
            params=json.dumps({
                'viz_type': 'bar',
                'datasource': f'{fact_sales.id}__table',
                'groupby': ['ProductName'],
                'metrics': [{
                    'expressionType': 'SIMPLE',
                    'column': {'column_name': 'Quantity', 'type': 'NUMERIC'},
                    'aggregate': 'SUM',
                    'label': 'Total Quantity'
                }],
                'order_desc': True,
                'row_limit': 100,
            }),
        )
        db.session.add(chart2)
        db.session.commit()
        charts.append({'id': chart2.id, 'name': chart2.slice_name})
        logger.info(f'[REBUILD] Created chart: {chart2.slice_name}')

        # Chart 3: Total Revenue (big number)
        chart3 = Slice(
            slice_name='Total Revenue',
            description='Total revenue across all sales',
            datasource_id=fact_sales.id,
            datasource_type='table',
            viz_type='big_number',
            params=json.dumps({
                'viz_type': 'big_number',
                'datasource': f'{fact_sales.id}__table',
                'metrics': [{
                    'expressionType': 'SIMPLE',
                    'column': {'column_name': 'Revenue', 'type': 'NUMERIC'},
                    'aggregate': 'SUM',
                    'label': 'SUM(Revenue)'
                }],
            }),
        )
        db.session.add(chart3)
        db.session.commit()
        charts.append({'id': chart3.id, 'name': chart3.slice_name})
        logger.info(f'[REBUILD] Created chart: {chart3.slice_name}')

        # Create dashboard
        logger.info('[REBUILD] Creating dashboard...')
        dashboard = Dashboard(
            dashboard_title='Sales Dashboard',
            slug='sales',
            description='Main sales dashboard with key metrics'
        )

        # Add charts to dashboard
        for chart_id in [chart1.id, chart2.id, chart3.id]:
            chart = db.session.query(Slice).get(chart_id)
            if chart:
                dashboard.slices.append(chart)

        db.session.add(dashboard)
        db.session.commit()
        logger.info('[REBUILD] Dashboard created successfully')

        logger.info('[REBUILD] ✓ Rebuild complete!')
        logger.info(f'[REBUILD] Created {len(charts)} charts and 1 dashboard')
        return True

    except Exception as e:
        logger.error(f'[REBUILD] Error: {e}')
        import traceback
        logger.error(traceback.format_exc())
        db.session.rollback()
        return False


if __name__ == '__main__':
    os.environ['SUPERSET_CONFIG_PATH'] = '/app/pythonpath/superset_config.py'
    from superset.app import create_app

    app = create_app()
    with app.app_context():
        success = rebuild_dashboards()
        sys.exit(0 if success else 1)
