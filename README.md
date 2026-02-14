# 🚀 Add Service

Production-ready Python (Flask) web service demonstrating:

-   ✅ REST API
-   ✅ Structured JSON logging
-   ✅ Health & readiness probes
-   ✅ Prometheus metrics
-   ✅ Docker multi-stage build
-   ✅ GitHub Actions CI
-   ✅ Trivy vulnerability scanning
-   ✅ SBOM generation (CycloneDX)
-   ✅ Cosign image signing (keyless)
-   ✅ Dependabot with auto-merge (patch updates)

------------------------------------------------------------------------

# 🏗 Architecture Overview

``` mermaid
flowchart LR
    Dev[Developer Push]
    GH[GitHub Repository]
    CI[GitHub Actions CI]
    Tests[Python Checks<br/>Ruff / MyPy / Pytest]
    DockerBuild[Docker Build<br/>Multi-stage]
    Smoke[Container Smoke Test]
    Security[Trivy Scan + SBOM]
    Publish[Push to GHCR]
    Sign[Cosign Signing<br/>OIDC Keyless]
    Registry[(GHCR)]
    Runtime[Container Runtime<br/>Kubernetes-ready]
    Metrics[Prometheus]
    Logs[Structured JSON Logs]

    Dev --> GH
    GH --> CI
    CI --> Tests
    Tests --> DockerBuild
    DockerBuild --> Smoke
    Smoke --> Security
    Security --> Publish
    Publish --> Registry
    Registry --> Sign
    Registry --> Runtime
    Runtime --> Metrics
    Runtime --> Logs
```

------------------------------------------------------------------------

# 📦 API

### `GET /add?left=5&right=2`

Returns:

``` json
{
  "sum": 7
}
```

-   `left` and `right` must be integers
-   Returns `400` on invalid input
-   Includes `X-Request-ID` header

------------------------------------------------------------------------

# 🩺 Health Endpoints

  Endpoint     Purpose
  ------------ --------------------
  `/healthz`   Liveness probe
  `/readyz`    Readiness probe
  `/metrics`   Prometheus metrics

------------------------------------------------------------------------

# 📊 Prometheus Metrics

Exposes:

-   `http_requests_total`
-   `http_request_duration_seconds`

Example:

``` bash
curl http://localhost:8080/metrics
```

------------------------------------------------------------------------

# 🧾 Structured Logging

-   JSON logs to stdout
-   Includes request_id, service, version, environment
-   Startup & shutdown events logged
-   Kubernetes-ready logging model

------------------------------------------------------------------------

# 🐳 Docker

Multi-stage build:

-   `builder` → build wheels
-   `test` → run pytest
-   `runtime` → minimal production image

Build locally:

``` bash
docker build --target runtime -t add-service:local .
```

Run:

``` bash
docker run -p 8080:8080 add-service:local
```

------------------------------------------------------------------------

# 🔐 Security

## Trivy Image Scanning

-   Fails CI on HIGH/CRITICAL vulnerabilities
-   Scans OS + Python dependencies

## SBOM (CycloneDX)

Generated automatically in CI.

## Cosign Signing (Keyless OIDC)

Images pushed to GHCR are signed using GitHub OIDC identity.

Verify:

``` bash
cosign verify ghcr.io/predrag86/sunairio:latest \
  --certificate-identity-regexp "https://github.com/predrag86/sunairio/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com"
```

------------------------------------------------------------------------

# 🔄 CI Pipeline Jobs

1.  **python-checks**
    -   Ruff
    -   MyPy
    -   Pytest
2.  **docker**
    -   Build test stage
    -   Build runtime image
    -   Smoke test
3.  **security**
    -   Trivy scan
    -   SARIF upload
    -   SBOM generation
4.  **publish** (main/tags only)
    -   Push to GHCR
    -   Cosign sign by digest

------------------------------------------------------------------------

# 🤖 Dependabot

-   Weekly dependency updates
-   Grouped runtime/dev updates
-   Patch updates auto-merge after CI passes
-   Minor/major require review

------------------------------------------------------------------------

# 🛠 Local Development

Install:

``` bash
pip install -r requirements.txt -r requirements-dev.txt
```

Run:

``` bash
python app.py
```

Lint & type check:

``` bash
ruff check .
ruff format .
mypy .
```

Tests:

``` bash
pytest -q
```

------------------------------------------------------------------------

# 🏁 Production Goals

This repository demonstrates:

-   Secure container build pipeline
-   Supply-chain best practices
-   Kubernetes-ready service patterns
-   Modern CI/CD security posture

------------------------------------------------------------------------

# 📜 License

MIT