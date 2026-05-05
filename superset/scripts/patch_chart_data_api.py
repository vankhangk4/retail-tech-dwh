#!/usr/bin/env python3
"""
Monkey-patch ChartDataQueryContextSchema để hỗ trợ form_data.
Fix lỗi: create() missing 'datasource' and 'queries'.
Chạy TRONG container: docker exec dwh_superset python3 /superset_scripts/patch_chart_data_api.py
"""
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def patch_schema():
    """Monkey-patch ChartDataQueryContextSchema.make_query_context."""
    from superset.app import create_app
    app = create_app()

    with app.app_context():
        from superset.charts.schemas import ChartDataQueryContextSchema
        from superset.common.query_context_factory import QueryContextFactory
        from superset.common.query_context import QueryContext

        # Lưu original method
        original_make = ChartDataQueryContextSchema.make_query_context

        def patched_make(self, data, **kwargs):
            # Nếu có form_data nhưng thiếu datasource/queries -> extract từ form_data
            if data.get('form_data') and not data.get('datasource'):
                form_data = data['form_data']
                logger.info('Extracting datasource from form_data...')

                # Extract ds_id từ '9__table'
                ds_str = form_data.get('datasource', '')
                if '__' in ds_str:
                    ds_id = int(ds_str.split('__')[0])
                else:
                    ds_id = form_data.get('datasource_id', 0)

                # Build metrics
                metrics = form_data.get('metrics', [])

                # Build query object
                query_obj = {
                    'groupby': form_data.get('groupby', []),
                    'metrics': metrics,
                    'row_limit': form_data.get('row_limit', 100),
                    'order_desc': form_data.get('order_desc', True),
                    'filters': [],
                    'extras': {},
                }

                data['datasource'] = {'id': ds_id, 'type': 'table'}
                data['queries'] = [query_obj]
                logger.info(f'  Built context: ds_id={ds_id}, groupby={query_obj["groupby"]}, metrics={len(metrics)}')

            return original_make(self, data, **kwargs)

        # Apply patch
        ChartDataQueryContextSchema.make_query_context = patched_make
        logger.info('ChartDataQueryContextSchema patched successfully')

        # Test with chart 413
        from superset.extensions import db
        from superset.models.slice import Slice
        import json

        schema = ChartDataQueryContextSchema()
        chart = db.session.query(Slice).filter_by(id=413).first()

        if chart:
            params = json.loads(chart.params)
            test_ctx = {'form_data': params}
            try:
                result = schema.load(test_ctx)
                logger.info(f'Test OK: {type(result).__name__}, datasource={result.datasource.table_name}')
            except Exception as e:
                logger.error(f'Test FAILED: {e}')
        else:
            logger.warning('Chart with id=413 not found - skipping test')


def apply_permanent_patch():
    """Apply patch at module level để nó tồn tại khi gunicorn worker start."""
    import importlib

    # Patch trong file schemas.py bằng cách đọc và ghi lại
    schemas_path = '/app/superset/charts/schemas.py'
    with open(schemas_path, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'def make_query_context' not in content:
        logger.info('Patching schemas.py...')

        # Tìm và thay thế make_query_context method
        old_method = '''    # pylint: disable=unused-argument
    @post_load
    def make_query_context(self, data: dict[str, Any], **kwargs: Any) -> QueryContext:
        query_context = self.get_query_context_factory().create(**data)
        return query_context'''

        new_method = '''    # pylint: disable=unused-argument
    @post_load
    def make_query_context(self, data: dict[str, Any], **kwargs: Any) -> QueryContext:
        # FIX: hỗ trợ form_data-only request (Superset 3.x backward compat)
        if data.get('form_data') and not data.get('datasource'):
            form_data = data['form_data']
            ds_str = form_data.get('datasource', '')
            if '__' in ds_str:
                ds_id = int(ds_str.split('__')[0])
            else:
                ds_id = form_data.get('datasource_id', 0)
            data['datasource'] = {'id': ds_id, 'type': 'table'}
            data['queries'] = [{
                'groupby': form_data.get('groupby', []),
                'metrics': form_data.get('metrics', []),
                'row_limit': form_data.get('row_limit', 100),
                'order_desc': form_data.get('order_desc', True),
                'filters': [],
                'extras': {},
            }]
        query_context = self.get_query_context_factory().create(**data)
        return query_context'''

        if old_method in content:
            content = content.replace(old_method, new_method)
            with open(schemas_path, 'w') as f:
                f.write(content)
            logger.info('schemas.py patched successfully')
            # Reload module
            importlib.reload(importlib.import_module('superset.charts.schemas'))
        else:
            logger.warning('Could not find target method in schemas.py')

            # Fallback: inject at the end of the file
            patch_code = '''

# ============================================================
# PATCH: Fix form_data-only chart data requests (Superset 3.x)
# ============================================================
import logging
logger = logging.getLogger(__name__)

_original_make = ChartDataQueryContextSchema.make_query_context

def _patched_make(self, data: dict[str, Any], **kwargs: Any) -> QueryContext:
    if data.get('form_data') and not data.get('datasource'):
        form_data = data['form_data']
        ds_str = form_data.get('datasource', '')
        if '__' in ds_str:
            ds_id = int(ds_str.split('__')[0])
        else:
            ds_id = form_data.get('datasource_id', 0)
        data['datasource'] = {'id': ds_id, 'type': 'table'}
        data['queries'] = [{
            'groupby': form_data.get('groupby', []),
            'metrics': form_data.get('metrics', []),
            'row_limit': form_data.get('row_limit', 100),
            'order_desc': form_data.get('order_desc', True),
            'filters': [],
            'extras': {},
        }]
        logger.info(f'form_data patched: ds_id={ds_id}')
    return _original_make(self, data, **kwargs)

ChartDataQueryContextSchema.make_query_context = _patched_make
logger.info('ChartDataQueryContextSchema patched (fallback method)')
'''

            with open(schemas_path, 'a') as f:
                f.write(patch_code)
            importlib.reload(importlib.import_module('superset.charts.schemas'))
            logger.info('schemas.py patched (fallback injection)')


def main():
    logger.info('=' * 60)
    logger.info('Patching ChartDataQueryContextSchema')
    logger.info('=' * 60)

    # Method 1: Permanent patch in file
    apply_permanent_patch()

    # Method 2: Runtime patch via app context
    patch_schema()

    logger.info('=' * 60)
    logger.info('Patch complete! Chart data API should now work.')
    logger.info('=' * 60)
    return 0


if __name__ == '__main__':
    sys.exit(main())
