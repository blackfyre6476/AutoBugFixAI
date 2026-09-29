import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(test_client: TestClient):
    """Test root endpoint returns 200 OK and welcome metadata."""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "AutoFix AI" in data["message"]
    assert data["health"] == "/api/v1/health"
    assert "version" in data


def test_health_endpoint(test_client: TestClient):
    """Test /api/v1/health endpoint returns 200 OK and HealthResponse schema."""
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    # Validate HealthResponse fields
    assert data["status"] == "healthy"
    assert data["service"] == "autofix-ai-backend"
    assert "version" in data
    assert "timestamp" in data
    assert "environment" in data

    # Validate modular components schema presence
    components = data.get("components", {})
    assert "python_version" in components
    assert "orchestrator" in components
    assert "sandbox" in components
    assert "repository" in components
    assert "agents" in components

    agents = components.get("agents", {})
    assert "repository_analyst" in agents
    assert "bug_investigator" in agents
    assert "fix_generator" in agents
    assert "validation_agent" in agents
    assert "regression_agent" in agents


def test_legacy_health_alias(test_client: TestClient):
    """Test legacy /health route alias."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
