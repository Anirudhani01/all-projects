import pytest
import asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import Mock, patch

from ..main import app
from ..config.database import Database


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def mock_database():
    """Mock database for testing."""
    with patch('app.config.database.Database') as mock_db:
        mock_db.database = Mock()
        mock_db.client = Mock()
        yield mock_db


@pytest.fixture
def sample_product_data():
    """Sample product data for testing."""
    return {
        "name": "Test Product",
        "description": "A test product for testing purposes",
        "price": 99.99,
        "material": "Cotton",
        "category": "Clothing",
        "images": ["https://example.com/image1.jpg"],
        "colors": [
            {
                "name": "Blue",
                "hex": "#0000FF",
                "image": "https://example.com/blue.jpg"
            }
        ],
        "sizes": ["S", "M", "L"],
        "isFeatured": False
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "rating": 5,
        "comment": "Great product! Highly recommended.",
        "userName": "Test User"
    }


@pytest.fixture
def sample_wishlist_data():
    """Sample wishlist data for testing."""
    return {
        "productId": "507f1f77bcf86cd799439011"
    }


@pytest.fixture
def mock_jwt_token():
    """Mock JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MDdmMWY3N2JjZjg2Y2Q3OTk0MzkwMTEiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJpc19hZG1pbiI6ZmFsc2UsImV4cCI6MTczNDU2NzgwMCwiaWF0IjoxNzM0NTY0MjAwfQ.test_signature"


@pytest.fixture
def mock_admin_jwt_token():
    """Mock admin JWT token for testing."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1MDdmMWY3N2JjZjg2Y2Q3OTk0MzkwMTIiLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiaXNfYWRtaW4iOnRydWUsImV4cCI6MTczNDU2NzgwMCwiaWF0IjoxNzM0NTY0MjAwfQ.test_admin_signature"
