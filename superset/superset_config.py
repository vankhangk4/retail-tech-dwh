# ============================================================
# superset_config.py - Superset configuration
# All sensitive values MUST be set via environment variables
# ============================================================
import os

# ---- Secret Key ----
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "")

# ---- Database ----
SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "")

# ---- Redis ----
REDIS_HOST = os.environ.get("REDIS_HOST", "datn_redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
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
