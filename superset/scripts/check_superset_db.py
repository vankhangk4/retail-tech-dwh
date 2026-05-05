#!/usr/bin/env python3
from superset.app import create_app
app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.models.slice import Slice
    from superset.models.dashboard import Dashboard
    charts = db.session.query(Slice).all()
    dashes = db.session.query(Dashboard).all()
    print(f"Charts in DB: {len(charts)}")
    for c in charts[:10]:
        print(f"  id={c.id} slice_name={c.slice_name} viz_type={c.viz_type_name}")
    print(f"Dashboards in DB: {len(dashes)}")
    for d in dashes:
        print(f"  id={d.id} title={d.dashboard_title} slug={d.slug}")
