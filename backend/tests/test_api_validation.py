import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "The Lenny Growth Assistant" in data["service"]

def test_api_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "local_provider" in data
    assert "cloud_provider" in data
    assert data["database"]["connected"] is True

def test_models_endpoint():
    response = client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) > 0
    assert any(m["provider"] == "local" for m in data["models"])

def test_session_creation_and_isolation():
    # Create Session A
    res_a = client.post("/api/v1/sessions", json={"title": "Session A"})
    assert res_a.status_code == 200
    session_a_id = res_a.json()["id"]

    # Create Session B
    res_b = client.post("/api/v1/sessions", json={"title": "Session B"})
    assert res_b.status_code == 200
    session_b_id = res_b.json()["id"]

    assert session_a_id != session_b_id

    # Check session A detail
    detail_a = client.get(f"/api/v1/sessions/{session_a_id}")
    assert detail_a.status_code == 200
    assert detail_a.json()["title"] == "Session A"
    assert len(detail_a.json()["messages"]) == 0

    # Delete session B
    del_b = client.delete(f"/api/v1/sessions/{session_b_id}")
    assert del_b.status_code == 200

    # Confirm session B is gone, session A remains
    get_b = client.get(f"/api/v1/sessions/{session_b_id}")
    assert get_b.status_code == 404

    get_a = client.get(f"/api/v1/sessions/{session_a_id}")
    assert get_a.status_code == 200
