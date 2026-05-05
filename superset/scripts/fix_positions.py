#!/usr/bin/env python3
"""
Fix dashboard positions: build position_json for all 5 dashboards.
Chạy TRONG container: docker exec dwh_superset python3 /superset_scripts/fix_positions.py
"""
import os
import sys
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def build_position(chart_ids: list) -> dict:
    """Build Superset 3.x dashboard position layout."""
    children = [f'CHART-{cid}' for cid in chart_ids]

    meta = {}
    for i, cid in enumerate(chart_ids):
        # Layout: 2 columns, charts alternate left/right, then wrap
        col = i % 2
        row = i // 2
        meta[f'CHART-{cid}'] = {
            'type': 'CHART',
            'id': f'CHART-{cid}',
            'meta': {
                'chartId': cid,
                'width': 6,
                'height': 50,
                'uuid': f'chart-uuid-{cid}',
            },
        }

    layout = {
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {
            'type': 'GRID',
            'id': 'GRID_ID',
            'children': children,
            'parents': ['ROOT_ID'],
            'gridSize': {'default': {'rows': 600, 'columns': 12, 'rowHeight': 50}},
        },
        'DASHBOARD_VERSION_KEY': 'v2',
    }
    layout.update(meta)
    return layout


# Dashboard configs: dash_id -> list of chart IDs (413-442 sau khi recreate)
DASHBOARDS = {
    11: {'title': 'Phan tich Doanh thu', 'charts': list(range(413, 420))},
    12: {'title': 'Phan tich San pham', 'charts': list(range(420, 427))},
    13: {'title': 'Quan ly Ton kho', 'charts': list(range(427, 433))},
    14: {'title': 'Phan tich Khach hang', 'charts': list(range(433, 438))},
    15: {'title': 'Hieu suat Nhan vien', 'charts': list(range(438, 443))},
}


def main():
    logger.info('=' * 60)
    logger.info('Fixing dashboard positions')
    logger.info('=' * 60)

    from superset.app import create_app
    app = create_app()

    with app.app_context():
        from superset.extensions import db
        from superset.models.dashboard import Dashboard
        from superset.models.slice import Slice

        for dash_id, cfg in DASHBOARDS.items():
            dash = db.session.query(Dashboard).filter_by(id=dash_id).first()
            if not dash:
                logger.warning(f'[SKIP] Dashboard {dash_id} not found')
                continue

            # Verify charts exist
            valid_charts = []
            for cid in cfg['charts']:
                chart = db.session.query(Slice).filter_by(id=cid).first()
                if chart:
                    valid_charts.append(cid)
                else:
                    logger.warning(f'  Chart {cid} not found')

            if not valid_charts:
                logger.error(f'  No valid charts for dashboard {dash_id}')
                continue

            position = build_position(valid_charts)
            dash.position_json = json.dumps(position)
            db.session.commit()

            logger.info(f'[OK] Dashboard {dash_id} ({cfg["title"]}): '
                        f'{len(valid_charts)} charts, position_json updated')

    logger.info('=' * 60)
    logger.info('Done! Refresh dashboards in Superset UI.')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
