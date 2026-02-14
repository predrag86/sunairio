import os
import shutil

bind = "0.0.0.0:8080"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "30"))

# Send logs to container stdout/stderr
# accesslog = "-"
errorlog = "-"

# JSON access log line (one line per request)
# NOTE: this is a JSON string template. Most values are safe; user-agent can contain quotes.
# Your app-level JSON logs remain the canonical structured logs.
access_log_format = (
    "{"
    '"type":"access",'
    '"remote_addr":"%(h)s",'
    '"request":"%(r)s",'
    '"method":"%(m)s",'
    '"path":"%(U)s",'
    '"query":"%(q)s",'
    '"status":%(s)s,'
    '"bytes":%(b)s,'
    '"duration_seconds":%(D)s,'
    '"referrer":"%(f)s",'
    '"user_agent":"%(a)s"'
    "}"
)


def on_starting(server):
    d = os.getenv("PROMETHEUS_MULTIPROC_DIR")
    if d:
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)
