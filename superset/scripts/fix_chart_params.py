#!/usr/bin/env python3
"""
Strip invalid fields from chart params (Superset 3.x compatibility).
Run on every startup to ensure charts work correctly.
Chạy TRONG container: docker exec dwh_superset python3 /superset_scripts/fix_chart_params.py
"""
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Các field hợp lệ trong params cho Superset 3.x
VALID_PARAM_KEYS = [
    'viz_type', 'datasource', 'datasource_id', 'datasource_name',
    'groupby', 'metrics', 'row_limit', 'order_desc',
    'show_legend', 'color_scheme', 'x_axis_show', 'show_values',
    'page_length', 'color', 'mapping', 'columns',
    'all_columns_x', 'histogram',
    'granularity', 'time_range', 'frequency',
    'extra_filters', 'adhoc_filters',
]


def main():
    logger.info('Fixing chart params (strip invalid fields)...')

    from superset.app import create_app
    app = create_app()

    with app.app_context():
        import json
        from superset.extensions import db
        from superset.models.slice import Slice

        fixed = 0
        for chart in db.session.query(Slice).all():
            try:
                params = json.loads(chart.params)
                cleaned = {k: params[k] for k in VALID_PARAM_KEYS if k in params}
                if len(cleaned) != len(params):
                    chart.params = json.dumps(cleaned)
                    db.session.commit()
                    fixed += 1
            except Exception:
                pass

        logger.info(f'Fixed {fixed} charts')

    logger.info('Chart params fix complete')
    return 0


if __name__ == '__main__':
    sys.exit(main())
