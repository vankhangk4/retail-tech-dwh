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
    "EMBEDDED_SUPERSET": True,  # Required for guest token embedding
    "EMBEDDABLE_CHARTS": True,
}

# ---- Guest Token (for iframe embedding) ----
GUEST_ROLE_NAME = "Public"
PUBLIC_ROLE_LIKE = "Gamma"
GUEST_TOKEN_JWT_SECRET = SECRET_KEY  # Must match for token validation
GUEST_TOKEN_JWT_ALGO = "HS256"
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"

# ---- HTTP headers: allow iframe embedding ----
HTTP_HEADERS = {"X-Frame-Options": "ALLOWALL"}

# Disable Talisman frame-ancestors so iframe works
TALISMAN_ENABLED = False

# ---- CORS ----
ENABLE_CORS = True
CORS_OPTIONS = {
    "supports_credentials": True,
    "allow_headers": ["*"],
    "resources": [r"/api/*", r"/superset/*"],
    "origins": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
}

# ---- Other ----
SUPERSET_WEBSERVER_TIMEOUT = 60
DATA_CACHE_TIMEOUT = 300
