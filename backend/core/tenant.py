from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from config import get_settings
import threading

settings = get_settings()

# Connection pools keyed by db_name, guarded by a lock
_engine_cache: dict = {}
_engine_lock = threading.Lock()

_tenant_engine_cache: dict = {}
_tenant_engine_lock = threading.Lock()

# Cached SessionLocal factory
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


@contextmanager
def get_master_session() -> Generator[Session, None, None]:
    SessionLocal = _get_master_sessionlocal()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_tenant_db_engine(db_name: str):
    with _tenant_engine_lock:
        if db_name not in _tenant_engine_cache:
            conn_str = (
                f"mssql+pyodbc://{settings.MSSQL_USER}:{settings.MSSQL_PASSWORD}"
                f"@{settings.MSSQL_HOST}:{settings.MSSQL_PORT}/{db_name}"
                f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
            )
            _tenant_engine_cache[db_name] = create_engine(
                conn_str,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=300,
            )
        return _tenant_engine_cache[db_name]


_tenant_sessionlocal_cache: dict = {}
_tenant_sessionlocal_lock = threading.Lock()


def _get_tenant_sessionlocal(db_name: str):
    if db_name not in _tenant_sessionlocal_cache:
        with _tenant_sessionlocal_lock:
            if db_name not in _tenant_sessionlocal_cache:
                engine = get_tenant_db_engine(db_name)
                _tenant_sessionlocal_cache[db_name] = sessionmaker(bind=engine)
    return _tenant_sessionlocal_cache[db_name]


@contextmanager
def get_tenant_session(db_name: str) -> Generator[Session, None, None]:
    SessionLocal = _get_tenant_sessionlocal(db_name)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_tenant_database(db_name: str) -> bool:
    """Tạo database mới trong SQL Server."""
    import pyodbc
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={settings.MSSQL_HOST},{settings.MSSQL_PORT};"
        f"UID={settings.MSSQL_USER};PWD={settings.MSSQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str, timeout=30)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE [{db_name}]")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database {db_name}: {e}")
        return False


def delete_tenant_database(db_name: str) -> bool:
    """Xóa database trong SQL Server."""
    import pyodbc
    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={settings.MSSQL_HOST},{settings.MSSQL_PORT};"
        f"UID={settings.MSSQL_USER};PWD={settings.MSSQL_PASSWORD};"
        f"TrustServerCertificate=yes;"
    )
    try:
        conn = pyodbc.connect(conn_str, timeout=30)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        cursor.execute(f"DROP DATABASE [{db_name}]")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting database {db_name}: {e}")
        return False
