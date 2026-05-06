#!/usr/bin/env python3
"""
Fix chart metrics with empty column objects in Superset.
Superset 3.x requires proper column references in metrics, not empty objects.
"""

import os
import sys
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def fix_chart_metrics():
    """Fix charts with malformed metrics (empty column objects)."""
    from superset.extensions import db
    from superset.models.slice import Slice

    try:
        # Get all charts
        charts = db.session.query(Slice).all()
        logger.info(f'Found {len(charts)} charts to check')

        fixed_count = 0

        for chart in charts:
            try:
                params = json.loads(chart.params)
                metrics = params.get('metrics', [])

                if not metrics:
                    continue

                changed = False

                for metric in metrics:
                    # Check if metric has empty column object
                    col = metric.get('column', {})
                    if isinstance(col, dict) and not col.get('column_name'):
                        # This metric has empty column - needs fixing
                        logger.info(f'[CHART {chart.id}] Metric "{metric.get("label")}" has empty column')

                        # Try to extract column name from label or sql expression
                        label = metric.get('label', '')
                        sql_expr = metric.get('sqlExpression', '')

                        # Parse column name from SUM(ColumnName) pattern
                        import re
                        match = re.search(r'(SUM|AVG|COUNT|MIN|MAX|STDDEV)\((\w+)\)', sql_expr or label)
                        if match:
                            col_name = match.group(2)
                            logger.info(f'[CHART {chart.id}] Extracted column: {col_name}')

                            # Update metric with proper column reference
                            metric['column'] = {
                                'column_name': col_name,
                                'type': 'NUMERIC',
                            }
                            changed = True
                        else:
                            logger.warning(f'[CHART {chart.id}] Could not extract column from: {sql_expr}')

                if changed:
                    chart.params = json.dumps(params)
                    db.session.commit()
                    logger.info(f'[FIXED] Chart "{chart.slice_name}" (id={chart.id})')
                    fixed_count += 1

            except Exception as e:
                logger.error(f'[ERROR] Chart {chart.id}: {str(e)[:100]}')
                db.session.rollback()
                continue

        logger.info(f'Fixed {fixed_count} charts')
        return fixed_count > 0

    except Exception as e:
        logger.error(f'Fatal error: {e}')
        return False


if __name__ == '__main__':
    print('[METRIC-FIX] Fixing chart metrics with empty column objects...')
    print()

    # Initialize Superset app
    os.environ['SUPERSET_CONFIG_PATH'] = '/app/pythonpath/superset_config.py'
    from superset.app import create_app

    app = create_app()
    with app.app_context():
        success = fix_chart_metrics()
        if success:
            print()
            print('[METRIC-FIX] ✓ Charts fixed successfully!')
            print('[METRIC-FIX] Refresh your browser to see the charts now working')
            sys.exit(0)
        else:
            print()
            print('[METRIC-FIX] ✗ No charts needed fixing or fix failed')
            sys.exit(1)
