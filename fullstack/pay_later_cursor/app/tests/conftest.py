"""
Test configuration and fixtures for the LazyPay application.
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import app
from app.db.mongo import MongoDB
from app.modules.users.service import UserService
from app.modules.merchants.service import MerchantService
from app.modules.transactions.service import TransactionService


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI application."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB connection for tests."""
    with patch('app.db.mongo.MongoDB') as mock_db:
        # Mock the database instance
        mock_db_instance = AsyncMock()
        mock_db_instance.get_database.return_value = AsyncMock()
        mock_db_instance.get_session.return_value = AsyncMock()
        mock_db.return_value = mock_db_instance
        yield mock_db_instance


@pytest.fixture
def mock_user_service():
    """Mock UserService for tests."""
    with patch('app.modules.users.service.UserService') as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_merchant_service():
    """Mock MerchantService for tests."""
    with patch('app.modules.merchants.service.MerchantService') as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_transaction_service():
    """Mock TransactionService for tests."""
    with patch('app.modules.transactions.service.TransactionService') as mock_service:
        mock_instance = AsyncMock()
        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_user_data():
    """Sample user data for tests."""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "credit_limit": 1000.0
    }


@pytest.fixture
def sample_user_response():
    """Sample user response data for tests."""
    return {
        "id": "68a0cc845efcb6a3f8ef7e95",
        "user_id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "credit_limit": 1000.0,
        "status": "ACTIVE",
        "created_at": "2025-08-17T06:30:00.000Z",
        "updated_at": "2025-08-17T06:30:00.000Z"
    }


@pytest.fixture
def sample_user_dues_response():
    """Sample user dues response data for tests."""
    return {
        "user_id": 1,
        "total_due": 150.0,
        "due_date": "2025-09-17T00:00:00.000Z",
        "transactions": [
            {
                "id": "68a0cc845efcb6a3f8ef7e97",
                "amount": 150.0,
                "due_date": "2025-09-17T00:00:00.000Z"
            }
        ]
    }


@pytest.fixture
def sample_user_list_response():
    """Sample user list response data for tests."""
    return {
        "users": [
            {
                "id": "68a0cc845efcb6a3f8ef7e95",
                "user_id": 1,
                "name": "Test User 1",
                "email": "test1@example.com",
                "credit_limit": 1000.0,
                "status": "ACTIVE",
                "created_at": "2025-08-17T06:30:00.000Z",
                "updated_at": "2025-08-17T06:30:00.000Z"
            },
            {
                "id": "68a0cc845efcb6a3f8ef7e96",
                "user_id": 2,
                "name": "Test User 2",
                "email": "test2@example.com",
                "credit_limit": 2000.0,
                "status": "ACTIVE",
                "created_at": "2025-08-17T07:30:00.000Z",
                "updated_at": "2025-08-17T07:30:00.000Z"
            }
        ],
        "page": 1,
        "size": 10,
        "total_count": 2,
        "total_pages": 1,
        "has_next": False,
        "has_prev": False
    }


@pytest.fixture
def sample_merchant_data():
    """Sample merchant data for tests."""
    return {
        "name": "Test Merchant",
        "current_fee_pct": 2.5
    }


@pytest.fixture
def sample_merchant_response():
    """Sample merchant response data for tests."""
    return {
        "id": "68a0cc845efcb6a3f8ef7e98",
        "merchant_id": 1,
        "name": "Test Merchant",
        "current_fee_pct": 2.5,
        "created_at": "2025-08-17T06:30:00.000Z",
        "updated_at": "2025-08-17T06:30:00.000Z"
    }


@pytest.fixture
def sample_transaction_data():
    """Sample transaction data for tests."""
    return {
        "user_id": 1,
        "merchant_id": 1,
        "amount": 150.0,
        "description": "Test purchase"
    }


@pytest.fixture
def sample_transaction_response():
    """Sample transaction response data for tests."""
    return {
        "id": "68a0cc845efcb6a3f8ef7e99",
        "user_id": 1,
        "merchant_id": 1,
        "type": "PURCHASE",
        "amount": 150.0,
        "description": "Test purchase",
        "status": "COMPLETED",
        "created_at": "2025-08-17T06:30:00.000Z"
    }


@pytest.fixture
def sample_transaction_list_response():
    """Sample transaction list response data for tests."""
    return {
        "transactions": [
            {
                "id": "68a0cc845efcb6a3f8ef7e99",
                "user_id": 1,
                "merchant_id": 1,
                "type": "PURCHASE",
                "amount": 150.0,
                "description": "Test purchase",
                "status": "COMPLETED",
                "created_at": "2025-08-17T06:30:00.000Z"
            }
        ],
        "page": 1,
        "size": 10,
        "total_count": 1,
        "total_pages": 1,
        "has_next": False,
        "has_prev": False
    }


@pytest.fixture
def sample_transaction_summary_response():
    """Sample transaction summary response data for tests."""
    return {
        "total_transactions": 10,
        "total_purchase_amount": 1500.0,
        "total_payment_amount": 500.0,
        "total_fees_collected": 37.5,
        "average_transaction_amount": 150.0
    }


# Override dependencies for testing
@pytest.fixture(autouse=True)
def override_dependencies():
    """Override FastAPI dependencies for testing."""
    from app.api.dependencies import get_user_service, get_merchant_service, get_transaction_service
    
    # Create mock services
    mock_user_svc = AsyncMock()
    mock_merchant_svc = AsyncMock()
    mock_transaction_svc = AsyncMock()
    
    # Override the dependency functions
    app.dependency_overrides[get_user_service] = lambda: mock_user_svc
    app.dependency_overrides[get_merchant_service] = lambda: mock_merchant_svc
    app.dependency_overrides[get_transaction_service] = lambda: mock_transaction_svc
    
    yield {
        'user_service': mock_user_svc,
        'merchant_service': mock_merchant_svc,
        'transaction_service': mock_transaction_svc
    }
    
    # Clean up
    app.dependency_overrides.clear()
