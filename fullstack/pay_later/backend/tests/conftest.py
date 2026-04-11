"""
Pytest configuration and fixtures for testing.
"""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import mongomock

from app.main import app
from app.core.database import database


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_database():
    """Create a test database with mock MongoDB."""
    # Use mongomock for testing
    mock_client = mongomock.AsyncMongoClient()
    mock_db = mock_client.test_pay_later_db
    
    # Store original database
    original_client = database.client
    original_database = database.database
    
    # Replace with mock database
    database.client = mock_client
    database.database = mock_db
    
    yield mock_db
    
    # Restore original database
    database.client = original_client
    database.database = original_database


@pytest.fixture
async def client(test_database):
    """Create a test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "date_of_birth": "1990-01-01T00:00:00Z",
        "address": {
            "street": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345",
            "country": "USA"
        },
        "role": "user"
    }


@pytest.fixture
def sample_merchant_data():
    """Sample merchant data for testing."""
    return {
        "name": "Test Merchant",
        "email": "merchant@example.com",
        "phone": "+1234567890",
        "address": {
            "street": "456 Merchant St",
            "city": "Merchant City",
            "state": "MC",
            "zip_code": "67890",
            "country": "USA"
        },
        "business_type": "Retail",
        "tax_id": "TAX123456789"
    }


@pytest.fixture
def sample_credit_limit_data():
    """Sample credit limit data for testing."""
    return {
        "limit_amount": "1000.00",
        "credit_score": 750,
        "approval_status": "approved"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for testing."""
    return {
        "transaction_type": "purchase",
        "amount": "100.00",
        "currency": "USD",
        "description": "Test purchase",
        "status": "pending"
    }
