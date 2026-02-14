# ---------- base: shared setup ----------
FROM python:3.12-slim AS base

WORKDIR /app

# ---------- test: install dev deps + run tests ----------
FROM base AS test

COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY app.py .
COPY test_app.py .

# Run tests as part of this stage (useful in CI)
RUN pytest -q


# ---------- runtime: minimal image ----------
FROM python:3.12-slim AS runtime

# curl only for HEALTHCHECK
RUN apt-get update \
  && rm -rf /var/lib/apt/lists/*

# non-root user
RUN useradd --create-home --shell /usr/sbin/nologin appuser

WORKDIR /app

# Install only runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only app code (no tests in runtime)
COPY app.py .

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)" || exit 1

CMD ["gunicorn", "-b", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "--timeout", "30", "app:app"]
