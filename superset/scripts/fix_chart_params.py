#!/usr/bin/env python3
"""
Normalize chart params for Superset 3.x.

This runs on every Superset startup and fixes charts already linked to
dashboards, including old charts created before provision_v2.py was corrected.
"""
import json
import logging
import re
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


VALID_PARAM_KEYS = [
    'viz_type', 'datasource', 'datasource_id', 'datasource_name',
    'groupby', 'columns', 'metrics', 'row_limit', 'order_desc', 'orderby',
    'show_legend', 'color_scheme', 'x_axis_show', 'show_values',
    'page_length', 'color', 'mapping',
    'all_columns_x', 'histogram',
    'granularity', 'granularity_sqla', 'time_grain_sqla', 'time_range',
    'frequency', 'extra_filters', 'adhoc_filters',
]

TIME_COLUMNS = {
    'FactSales': 'SaleDate',
    'FactInventory': 'CheckDate',
    'FactPurchase': 'PurchaseDate',
    'DM_SalesSummary': 'LastRefreshed',
    'DM_CustomerRFM': 'UpdatedAt',
    'DM_InventoryAlert': 'CheckDate',
    'V_SalesEnriched': 'SaleDate',
}


def get_column_obj(db, table_id: int, column_name: str) -> dict:
    from superset.connectors.sqla.models import TableColumn

    col = db.session.query(TableColumn).filter_by(
        table_id=table_id,
        column_name=column_name,
    ).first()
    if not col:
        return {'column_name': column_name, 'type': 'NUMERIC'}
    return {
        'id': col.id,
        'column_name': col.column_name,
        'type': col.type or 'NUMERIC',
        'type_generic': getattr(col, 'type_generic', None),
    }


def infer_metric_column(metric: dict, fallback_columns: list[str]) -> Optional[str]:
    label = metric.get('label') or ''
    sql_expr = metric.get('sqlExpression') or ''
    match = re.search(r'(?:SUM|AVG|COUNT|MIN|MAX|STDDEV)\((\w+)\)', sql_expr or label)
    if match:
        return match.group(1)

    col = metric.get('column')
    if isinstance(col, dict) and col.get('column_name'):
        return col['column_name']

    return fallback_columns[0] if fallback_columns else None


def normalize_metric(db, table_id: int, metric: dict, fallback_columns: list[str]) -> dict:
    label = metric.get('label') or metric.get('sqlExpression') or ''
    aggregate = metric.get('aggregate') or metric.get('agg') or 'SUM'

    if label == 'COUNT(*)':
        aggregate = 'COUNT'

    column_name = infer_metric_column(metric, fallback_columns)
    if column_name:
        if label == 'COUNT(*)':
            label = f'COUNT({column_name})'
        return {
            'expressionType': 'SIMPLE',
            'column': get_column_obj(db, table_id, column_name),
            'aggregate': aggregate,
            'label': label or f'{aggregate}({column_name})',
            'optionName': f'metric_{aggregate.lower()}_{column_name.lower()}',
        }

    return {
        'expressionType': 'SQL',
        'sqlExpression': label or 'COUNT(*)',
        'label': label or 'COUNT(*)',
        'optionName': 'metric_sql',
    }


def normalize_chart(db, chart) -> bool:
    from superset.connectors.sqla.models import SqlaTable

    try:
        params = json.loads(chart.params or '{}')
    except Exception:
        params = {}

    dataset = db.session.query(SqlaTable).filter_by(id=chart.datasource_id).first()
    if not dataset:
        return False

    original = json.dumps(params, sort_keys=True)
    original_viz = chart.viz_type

    params = {k: params[k] for k in VALID_PARAM_KEYS if k in params}
    params['viz_type'] = chart.viz_type
    params['datasource'] = f'{chart.datasource_id}__table'
    params.setdefault('row_limit', 100)
    params.setdefault('show_legend', True)
    params.setdefault('color_scheme', 'supersetColors')
    params.setdefault('time_range', 'No filter')
    params.setdefault('adhoc_filters', [])

    groupby = params.get('groupby') or params.get('columns') or []
    if not isinstance(groupby, list):
        groupby = [groupby]
    fallback_columns = [c for c in groupby if isinstance(c, str)]

    metrics = params.get('metrics') or []
    if isinstance(metrics, dict):
        metrics = [metrics]
    normalized_metrics = [
        normalize_metric(db, dataset.id, metric, fallback_columns)
        for metric in metrics
        if isinstance(metric, dict)
    ]
    if normalized_metrics:
        params['metrics'] = normalized_metrics

    time_col = TIME_COLUMNS.get(dataset.table_name) or dataset.main_dttm_col
    if time_col:
        dataset.main_dttm_col = time_col
        params['granularity_sqla'] = time_col
        params['granularity'] = time_col

    if chart.viz_type == 'line':
        params['groupby'] = []
        params['time_grain_sqla'] = 'P1M'
        params.pop('orderby', None)
        params.pop('order_desc', None)
    elif chart.viz_type in ('big_number', 'single_metric'):
        params.pop('groupby', None)
        params.pop('columns', None)
        params.pop('orderby', None)
        params.pop('order_desc', None)
    elif normalized_metrics:
        params['orderby'] = [[normalized_metrics[0], False]]
        params['order_desc'] = True

    chart.params = json.dumps(params)
    chart.query_context = build_query_context(dataset.id, chart.id, params)
    return (
        original != json.dumps(params, sort_keys=True)
        or original_viz != chart.viz_type
        or not chart.query_context
    )


def build_query_context(ds_id: int, chart_id: int, params: dict) -> str:
    metrics = params.get('metrics') or []
    groupby = params.get('groupby') or params.get('columns') or []
    if not isinstance(groupby, list):
        groupby = [groupby]

    query = {
        'filters': [],
        'extras': {'having': '', 'where': ''},
        'applied_time_extras': {},
        'columns': groupby,
        'metrics': metrics,
        'annotation_layers': [],
        'row_limit': params.get('row_limit', 100),
        'series_limit': 0,
        'url_params': {},
        'custom_params': {},
        'custom_form_data': {},
        'time_range': params.get('time_range', 'No filter'),
    }

    if params.get('granularity'):
        query['granularity'] = params['granularity']
    if params.get('time_grain_sqla'):
        query['time_grain'] = params['time_grain_sqla']
    if params.get('orderby'):
        query['orderby'] = params['orderby']
    if params.get('order_desc') is not None:
        query['order_desc'] = params['order_desc']

    form_data = {
        **params,
        'slice_id': chart_id,
        'force': False,
        'result_format': 'json',
        'result_type': 'full',
    }
    return json.dumps({
        'datasource': {'id': ds_id, 'type': 'table'},
        'force': False,
        'queries': [query],
        'form_data': form_data,
        'result_format': 'json',
        'result_type': 'full',
    })


def main():
    logger.info('Fixing chart params for Superset 3.x...')

    from superset.app import create_app
    app = create_app()

    with app.app_context():
        from superset.extensions import db
        from superset.models.slice import Slice

        fixed = 0
        for chart in db.session.query(Slice).all():
            try:
                if normalize_chart(db, chart):
                    fixed += 1
            except Exception as exc:
                logger.warning(f'[SKIP] Chart {chart.id}: {exc}')
                db.session.rollback()
                continue

        db.session.commit()
        logger.info(f'Fixed {fixed} charts')

    logger.info('Chart params fix complete')
    return 0


if __name__ == '__main__':
    sys.exit(main())
