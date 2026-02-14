import os

class Settings:
    SERVICE_NAME = os.getenv("SERVICE_NAME", "add-service")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
    VERSION = os.getenv("VERSION", os.getenv("GITHUB_SHA", "unknown"))
    TESTING = os.getenv("TESTING", "0") == "1"

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_STACKTRACE = os.getenv("LOG_STACKTRACE", "0") == "1"

    POD_NAME = os.getenv("POD_NAME")
    POD_NAMESPACE = os.getenv("POD_NAMESPACE")

    # Gunicorn-related (used by gunicorn.conf.py, but ok to keep here too)
    GUNICORN_WORKERS = int(os.getenv("GUNICORN_WORKERS", "2"))
    GUNICORN_THREADS = int(os.getenv("GUNICORN_THREADS", "4"))
    GUNICORN_TIMEOUT = int(os.getenv("GUNICORN_TIMEOUT", "30"))
