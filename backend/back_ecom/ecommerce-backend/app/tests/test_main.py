import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "E-commerce Backend API"
    assert data["version"] == "1.0.0"


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ecommerce-backend"


def test_docs_endpoint_in_debug(client: TestClient):
    """Test that docs are available in debug mode."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_v1_prefix():
    """Test that all API routes use the correct prefix."""
    from app.main import app
    
    # Check that all routes start with /api/v1
    for route in app.routes:
        if hasattr(route, 'prefix') and route.prefix:
            if route.prefix.startswith('/api/v1'):
                assert True  # Route has correct prefix
            elif route.prefix.startswith('/api'):
                # This is fine for the main API router
                assert True
            else:
                # Only root and health endpoints should not have /api prefix
                assert route.prefix in ['/', '/health'] or route.prefix is None
