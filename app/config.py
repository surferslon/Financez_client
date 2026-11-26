import os
from datetime import timedelta

REQUIRED = ("SYNC_TOKEN", "SECRET_KEY")


def load_config(overrides=None):
    config = {
        "SYNC_TOKEN": os.environ.get("SYNC_TOKEN"),
        "SECRET_KEY": os.environ.get("SECRET_KEY"),
        "DATABASE": os.environ.get("DATABASE", "data/client.sqlite3"),
        "SESSION_COOKIE_SECURE": os.environ.get("COOKIE_SECURE", "True") == "True",
        "SESSION_COOKIE_SAMESITE": "Lax",
        "PERMANENT_SESSION_LIFETIME": timedelta(days=90),
        "MAX_CONTENT_LENGTH": 1024 * 1024,
        "LOGIN_DELAY": 1.0,
        **(overrides or {}),
    }
    missing = [key for key in REQUIRED if not config[key]]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
    return config
