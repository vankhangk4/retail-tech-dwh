from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
from config import get_settings

settings = get_settings()


def get_master_engine():
    return create_engine(settings.master_db_url, pool_pre_ping=True)


@contextmanager
def get_master_session() -> Generator[Session, None, None]:
    engine = get_master_engine()
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_tenant_db_engine(db_name: str):
    conn_str = (
        f"mssql+pyodbc://{settings.MSSQL_USER}:{settings.MSSQL_PASSWORD}"
        f"@{settings.MSSQL_HOST}:{settings.MSSQL_PORT}/{db_name}"
        f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
    )
    return create_engine(conn_str, pool_pre_ping=True)


@contextmanager
def get_tenant_session(db_name: str) -> Generator[Session, None, None]:
    engine = get_tenant_db_engine(db_name)
    SessionLocal = sessionmaker(bind=engine)
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
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE [{db_name}]")
        conn.commit()
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
        cursor = conn.cursor()
        cursor.execute(f"""
            USE master;
            ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            DROP DATABASE [{db_name}];
        """)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting database {db_name}: {e}")
        return False
