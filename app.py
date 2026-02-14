import logging
import os
import sys
import time
import uuid
import traceback
from typing import Any, Dict, Optional

from flask import Flask, jsonify, request, g
from pythonjsonlogger import jsonlogger
from config import Settings


app = Flask(__name__)

SERVICE_NAME = Settings.SERVICE_NAME
ENVIRONMENT = Settings.ENVIRONMENT
VERSION = Settings.VERSION
POD_NAME = Settings.POD_NAME
POD_NAMESPACE = Settings.POD_NAMESPACE

LOG_LEVEL = Settings.LOG_LEVEL
LOG_STACKTRACE = Settings.LOG_STACKTRACE



def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)

    # Base JSON fields are emitted via `extra={...}` in logger calls
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers = []
    root.addHandler(handler)
    root.setLevel(LOG_LEVEL)

    # Reduce noisy Flask dev server logs when running locally (gunicorn handles prod)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


setup_logging()
logger = logging.getLogger(SERVICE_NAME)

def _get_request_id() -> str:
    # Common headers set by proxies/ingress/gateways
    return (
        request.headers.get("X-Request-ID")
        or request.headers.get("X-Correlation-ID")
        or request.headers.get("Traceparent")  # if present, still store it as an id-ish field
        or str(uuid.uuid4())
    )


def _base_log_fields() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "env": ENVIRONMENT,
        "version": VERSION,
        "pod_name": POD_NAME,
        "pod_namespace": POD_NAMESPACE,
    }

logger.info(
    "startup",
    extra={
        **_base_log_fields(),
        "type": "startup",
        "log_level": LOG_LEVEL,
        "pid": os.getpid(),
    },
)

@app.before_request
def _before_request() -> None:
    g.start_time = time.time()
    g.request_id = _get_request_id()


@app.after_request
def _after_request(response):
    duration_ms = int((time.time() - g.start_time) * 1000)

    # request context fields
    fields: Dict[str, Any] = {
        **_base_log_fields(),
        "type": "request",
        "request_id": g.request_id,
        "method": request.method,
        "path": request.path,
        "query_string": request.query_string.decode("utf-8", errors="ignore"),
        "status": response.status_code,
        "duration_ms": duration_ms,
        "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
    }

    logger.info("request", extra=fields)

    # echo back for client correlation
    response.headers["X-Request-ID"] = g.request_id
    return response


@app.errorhandler(Exception)
def _handle_exception(e: Exception):
    err_msg = str(e) or e.__class__.__name__

    fields = {
        **_base_log_fields(),
        "type": "error",
        "request_id": getattr(g, "request_id", None),
        "method": request.method,
        "path": request.path,
        "query_string": request.query_string.decode("utf-8", errors="ignore"),
        "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
        "exception_type": e.__class__.__name__,
        "error": err_msg,
    }

    if LOG_STACKTRACE:
        fields["stacktrace"] = traceback.format_exc()

    logger.error("unhandled_exception", extra=fields)

    return jsonify({"error": "Internal Server Error"}), 500



def _parse_int_param(name: str) -> tuple[Optional[int], Optional[str]]:
    values = request.args.getlist(name)
    if len(values) == 0:
        return None, f"Missing query param '{name}'"
    if len(values) > 1:
        return None, f"Query param '{name}' must appear only once"

    raw = values[0].strip()
    try:
        return int(raw), None
    except ValueError:
        return None, f"Query param '{name}' must be an integer"


@app.get("/add")
def add():
    left, err_left = _parse_int_param("left")
    if err_left:
        return jsonify({"error": err_left}), 400

    right, err_right = _parse_int_param("right")
    if err_right:
        return jsonify({"error": err_right}), 400

    return jsonify({"sum": left + right}), 200



@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
