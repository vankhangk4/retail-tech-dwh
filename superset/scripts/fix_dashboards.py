#!/usr/bin/env python3
"""Fix dashboards: attach charts to dashboards via programmatic DB access."""
from superset.app import create_app
app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.models.slice import Slice
    from superset.models.dashboard import Dashboard
    from sqlalchemy import insert

    DASH_CONFIGS = {
        'doanh-thu':   list(range(188, 195)),  # 7 charts: 188-194
        'san-pham':    list(range(195, 202)),  # 7 charts: 195-201
        'ton-kho':     list(range(202, 208)),  # 6 charts: 202-207
        'khach-hang':  list(range(208, 213)),  # 5 charts: 208-212
        'nhan-vien':   list(range(213, 218)),  # 5 charts: 213-217
    }

    # Get dashboard_slices table
    from superset.models.dashboard import dashboard_slices

    print(f"Total slices in DB: {db.session.query(Slice).count()}")
    print(f"Total dashboards: {db.session.query(Dashboard).count()}")

    for slug, chart_ids in DASH_CONFIGS.items():
        dash = db.session.query(Dashboard).filter_by(slug=slug).first()
        if not dash:
            print(f"  [SKIP] Dashboard '{slug}' not found")
            continue

        print(f"\nProcessing: {dash.dashboard_title} (id={dash.id}, slug={slug})")

        # Clear existing dashboard_slices
        db.session.query(dashboard_slices).filter_by(dashboard_id=dash.id).delete()
        db.session.commit()

        # Add all charts
        for cid in chart_ids:
            chart = db.session.query(Slice).filter_by(id=cid).first()
            if not chart:
                print(f"  [WARN] Chart id={cid} not found")
                continue
            stmt = insert(dashboard_slices).values(
                dashboard_id=dash.id,
                slice_id=cid
            )
            db.session.execute(stmt)
            print(f"  [OK] Added: {chart.slice_name} (id={cid})")

        db.session.commit()
        count = db.session.query(dashboard_slices).filter_by(dashboard_id=dash.id).count()
        print(f"  Total slices attached: {count}")

    print(f"\nDone!")
