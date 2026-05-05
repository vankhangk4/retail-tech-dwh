#!/usr/bin/env python3
import sys
sys.stdout = sys.stderr

from superset.app import create_app
app = create_app()
with app.app_context():
    from superset.extensions import db
    from superset.models.slice import Slice
    from sqlalchemy import inspect

    all_slices = db.session.query(Slice).all()
    print("INFO: Total slices: " + str(len(all_slices)))

    s79 = db.session.query(Slice).filter_by(id=79).first()
    print("INFO: Slice 79: " + str(s79.slice_name if s79 else None))

    mapper = inspect(Slice)
    print("INFO: Slice columns: " + str([c.key for c in mapper.columns]))
