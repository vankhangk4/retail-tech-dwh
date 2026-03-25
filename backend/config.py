from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Master DB (PostgreSQL - metadata)
    MASTER_DB_HOST: str = "datn_postgres_master"
    MASTER_DB_PORT: int = 5432
    MASTER_DB_USER: str = "postgres"
    MASTER_DB_PASSWORD: str = ""  # required from env
    MASTER_DB_NAME: str = "DWH_Master"

    # SQL Server (DWH per tenant)
    MSSQL_HOST: str = "datn_mssql"
    MSSQL_PORT: int = 1433
    MSSQL_USER: str = "sa"
    MSSQL_PASSWORD: str = ""  # required from env

    # JWT
    JWT_SECRET_KEY: str = ""  # required from env
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Upload
    UPLOAD_DIR: str = "/app/uploads"

    # Superset
    SUPERSET_URL: str = "http://datn_superset:8088"
    SUPERSET_ADMIN_USER: str = "admin"
    SUPERSET_ADMIN_PASSWORD: str = ""  # required from env

    # Default SuperAdmin (set via env for init)
    DEFAULT_ADMIN_PASSWORD: str = ""  # required from env

    # Shared Data Warehouse DB (single DB for all tenants)
    SHARED_DWH_DB: str = "DWH_RetailTech"

    # Superset shared dashboard
    SUPERSET_SHARED_DASHBOARD_ID: int = 1

    @property
    def master_db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.MASTER_DB_USER}:{self.MASTER_DB_PASSWORD}"
            f"@{self.MASTER_DB_HOST}:{self.MASTER_DB_PORT}/{self.MASTER_DB_NAME}"
        )

    @property
    def mssql_conn_str(self) -> str:
        return (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={self.MSSQL_HOST},{self.MSSQL_PORT};"
            f"UID={self.MSSQL_USER};PWD={self.MSSQL_PASSWORD};"
            f"TrustServerCertificate=yes;Connection Timeout=30;"
        )

    @property
    def shared_dwh_conn_str(self) -> str:
        """Connection string for the shared DWH database (all tenants)."""
        return (
            f"mssql+pyodbc://{self.MSSQL_USER}:{self.MSSQL_PASSWORD}"
            f"@{self.MSSQL_HOST}:{self.MSSQL_PORT}/{self.SHARED_DWH_DB}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
