# ============================================================
# superset_config.py - Superset configuration
# ============================================================
import os

# ---- Secret Key ----
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "datn_dev_secret_key_change_in_prod")

# ---- Database ----
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql+psycopg2://superset:superset@datn_postgres:5432/superset"
)

# ---- Redis ----
REDIS_HOST = os.environ.get("REDIS_HOST", "datn_redis")
REDIS_PORT = os.environ.get("REDIS_PORT", "6379")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_PASSWORD": REDIS_PASSWORD,
}

# ---- Feature Flags ----
FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "ALERT_REPORTS": True,
}

# ---- Other ----
SUPERSET_WEBSERVER_TIMEOUT = 60
DATA_CACHE_TIMEOUT = 300
