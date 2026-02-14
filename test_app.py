import pytest
from app import app

@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_add_ok(client):
    resp = client.get("/add?left=5&right=2")
    assert resp.status_code == 200
    assert resp.get_json() == {"sum": 7}
    assert resp.headers.get("X-Request-ID")

def test_add_negative(client):
    resp = client.get("/add?left=-10&right=3")
    assert resp.status_code == 200
    assert resp.get_json() == {"sum": -7}

def test_add_missing_param(client):
    resp = client.get("/add?left=5")
    assert resp.status_code == 400
    body = resp.get_json()
    assert "error" in body

def test_add_invalid_param(client):
    resp = client.get("/add?left=abc&right=2")
    assert resp.status_code == 400
    body = resp.get_json()
    assert "error" in body

def test_add_whitespace_ok(client):
    resp = client.get("/add?left= 5&right=2")
    assert resp.status_code == 200
    assert resp.get_json() == {"sum": 7}

def test_add_repeated_param(client):
    resp = client.get("/add?left=1&left=2&right=3")
    assert resp.status_code == 400
    assert resp.get_json()["error"].startswith("Query param 'left'")

def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ok"}
    assert resp.headers.get("X-Request-ID")


def test_readyz(client):
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.get_json() == {"status": "ready"}
    assert resp.headers.get("X-Request-ID")


def test_request_id_header_present(client):
    resp = client.get("/add?left=5&right=2")
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID")

def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("Content-Type", "")
    assert resp.data  # Should return some metrics data