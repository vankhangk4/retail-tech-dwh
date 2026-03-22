from models.master import Base, Tenant, User, ETLRun


def get_master_engine():
    from core.tenant import get_master_engine as _get
    return _get()


def init_master_db():
    from core.tenant import get_master_engine as _get
    engine = _get()
    Base.metadata.create_all(bind=engine)
