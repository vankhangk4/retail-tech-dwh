#!/usr/bin/env python3
"""
Fix ALL existing dashboards' position_json to use proper Superset 3.x layout.
Each chart must be wrapped in a ROW node inside GRID — not placed directly under GRID.

Usage: docker exec dwh_superset python3 /superset_scripts/fix_dashboard_positions.py
"""
import json
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def build_position(chart_ids: list) -> dict:
    """
    Superset 3.x layout: ROOT -> GRID -> ROW[] -> CHART
    Placing CHART directly under GRID causes:
      TypeError: Cannot read properties of undefined (reading 'width')
    """
    row_ids = []
    meta = {}

    for i, cid in enumerate(chart_ids):
        chart_key = f'CHART-{cid}'
        row_key   = f'ROW-{i}'

        meta[chart_key] = {
            'type': 'CHART',
            'id': chart_key,
            'children': [],
            'parents': ['ROOT_ID', 'GRID_ID', row_key],
            'meta': {
                'chartId': cid,
                'width': 12,
                'height': 50,
            },
        }
        meta[row_key] = {
            'type': 'ROW',
            'id': row_key,
            'children': [chart_key],
            'parents': ['ROOT_ID', 'GRID_ID'],
            'meta': {'background': 'BACKGROUND_TRANSPARENT'},
        }
        row_ids.append(row_key)

    layout = {
        'ROOT_ID': {'type': 'ROOT', 'id': 'ROOT_ID', 'children': ['GRID_ID']},
        'GRID_ID': {
            'type': 'GRID',
            'id': 'GRID_ID',
            'children': row_ids,
            'parents': ['ROOT_ID'],
        },
        'DASHBOARD_VERSION_KEY': 'v2',
    }
    layout.update(meta)
    return layout


def main():
    from superset.app import create_app
    app = create_app()

    with app.app_context():
        from superset.extensions import db
        from superset.models.dashboard import Dashboard

        dashes = db.session.query(Dashboard).all()
        logger.info(f'Found {len(dashes)} dashboard(s)')

        for dash in dashes:
            pos = json.loads(dash.position_json or '{}')

            # Collect chart IDs from current position_json
            chart_ids = []
            for k, v in pos.items():
                if isinstance(v, dict) and v.get('type') == 'CHART':
                    cid = v.get('meta', {}).get('chartId')
                    if cid:
                        chart_ids.append(cid)

            # Fallback: get from slices relationship
            if not chart_ids:
                chart_ids = [s.id for s in dash.slices]

            if not chart_ids:
                logger.warning(f'[SKIP] Dashboard {dash.id} "{dash.dashboard_title}" — no charts found')
                continue

            new_pos = build_position(chart_ids)
            dash.position_json = json.dumps(new_pos)
            db.session.commit()
            logger.info(f'[OK] Dashboard {dash.id} "{dash.dashboard_title}" — '
                        f'{len(chart_ids)} chart(s): {chart_ids}')

        logger.info('=== All dashboards fixed! Refresh in Superset UI. ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
