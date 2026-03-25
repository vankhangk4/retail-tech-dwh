from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from config import get_settings
import threading

settings = get_settings()

# Shared engines/session factories
_engine_cache: dict = {}
_engine_lock = threading.Lock()

_SharedSessionLocal = None
_SharedSessionLocal_lock = threading.Lock()

_MasterSessionLocal = None
_MasterSessionLocal_lock = threading.Lock()


def _get_master_sessionlocal():
    global _MasterSessionLocal
    if _MasterSessionLocal is None:
        with _MasterSessionLocal_lock:
            if _MasterSessionLocal is None:
                engine = get_master_engine()
                _MasterSessionLocal = sessionmaker(bind=engine)
    return _MasterSessionLocal


def _get_shared_sessionlocal():
    global _SharedSessionLocal
    if _SharedSessionLocal is None:
        with _SharedSessionLocal_lock:
            if _SharedSessionLocal is None:
                engine = get_shared_dwh_engine()
                _SharedSessionLocal = sessionmaker(bind=engine)
    return _SharedSessionLocal


def get_master_engine():
    with _engine_lock:
        if "master" not in _engine_cache:
            _engine_cache["master"] = create_engine(
                settings.master_db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
        return _engine_cache["master"]


def get_shared_dwh_engine():
    with _engine_lock:
        if "shared_dwh" not in _engine_cache:
            _engine_cache["shared_dwh"] = create_engine(
                settings.shared_dwh_conn_str,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=300,
            )
        return _engine_cache["shared_dwh"]


@contextmanager
def get_master_session() -> Generator[Session, None, None]:
    SessionLocal = _get_master_sessionlocal()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def get_tenant_session(db_name: str | None = None) -> Generator[Session, None, None]:
    """
    Backward-compatible helper.
    The system now uses one shared DWH DB for all tenants; db_name is ignored.
    """
    SessionLocal = _get_shared_sessionlocal()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
