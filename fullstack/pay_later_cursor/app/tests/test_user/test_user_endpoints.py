#!/usr/bin/env python3
"""
Comprehensive test cases for User endpoints.
Tests all HTTP methods: POST, GET
Target: 90% pass rate, 10% fail rate
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.modules.users.service import UserService
from app.modules.users.schemas import (
    CreateUserRequest, UserResponse, UserDuesResponse, UserListResponse
)


class TestUserEndpoints:
    """Test cases for user endpoints."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_user_service(self) -> AsyncMock:
        """Create a mock user service."""
        return AsyncMock(spec=UserService)
    
    @pytest.fixture
    def sample_create_user_request(self) -> dict:
        """Sample create user request data."""
        return {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            }
        }
    
    @pytest.fixture
    def sample_user_response(self) -> dict:
        """Sample user response data."""
        return {
            "user_id": "68a0cc845efcb6a3f8ef7e95",
            "custom_user_id": 1,
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "status": "ACTIVE",
            "credit_limit": 1000.0,
            "outstanding_amount": 0.0,
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            },
            "created_at": "2025-08-17T06:30:00.000Z",
            "updated_at": "2025-08-17T06:30:00.000Z"
        }
    
    @pytest.fixture
    def sample_user_dues_response(self) -> dict:
        """Sample user dues response data."""
        return {
            "user_id": "68a0cc845efcb6a3f8ef7e95",
            "custom_user_id": 1,
            "outstanding_amount": 150.0,
            "credit_limit": 1000.0,
            "available_credit": 850.0,
            "due_date": "2025-09-17T00:00:00.000Z",
            "is_overdue": False,
            "last_payment_date": "2025-08-15T10:30:00.000Z",
            "last_payment_amount": 50.0
        }
    
    @pytest.fixture
    def sample_user_list_response(self) -> dict:
        """Sample user list response data."""
        return {
            "users": [
                {
                    "user_id": "68a0cc845efcb6a3f8ef7e95",
                    "custom_user_id": 1,
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "status": "ACTIVE",
                    "credit_limit": 1000.0,
                    "outstanding_amount": 150.0,
                    "created_at": "2025-08-17T06:30:00.000Z"
                },
                {
                    "user_id": "68a0cc845efcb6a3f8ef7e96",
                    "custom_user_id": 2,
                    "name": "Jane Smith",
                    "email": "jane.smith@example.com",
                    "status": "ACTIVE",
                    "credit_limit": 1500.0,
                    "outstanding_amount": 0.0,
                    "created_at": "2025-08-17T07:30:00.000Z"
                }
            ],
            "total_count": 2,
            "page": 1,
            "size": 10,
            "total_pages": 1
        }

    # Test 1: POST /api/v1/users/ - Create User (PASSING TESTS - 90%)
    
    def test_create_user_success(self, client: TestClient, mock_user_service: AsyncMock, 
                                sample_create_user_request: dict, sample_user_response: dict):
        """Test successful user creation."""
        # Arrange
        mock_user_service.onboard_user.return_value = UserResponse(**sample_user_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.post("/api/v1/users/", json=sample_create_user_request)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["user_id"] == "68a0cc845efcb6a3f8ef7e95"
            assert data["name"] == "John Doe"
            assert data["email"] == "john.doe@example.com"
            assert data["status"] == "ACTIVE"
            assert data["credit_limit"] == 1000.0
            mock_user_service.onboard_user.assert_called_once()
    
    def test_create_user_invalid_email(self, client: TestClient):
        """Test user creation with invalid email."""
        # Arrange
        invalid_request = {
            "name": "John Doe",
            "email": "invalid-email",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            }
        }
        
        # Act
        response = client.post("/api/v1/users/", json=invalid_request)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_user_missing_required_fields(self, client: TestClient):
        """Test user creation with missing required fields."""
        # Arrange
        incomplete_request = {
            "name": "John Doe"
            # Missing email, phone, date_of_birth, address
        }
        
        # Act
        response = client.post("/api/v1/users/", json=incomplete_request)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_user_duplicate_email(self, client: TestClient, mock_user_service: AsyncMock,
                                       sample_create_user_request: dict):
        """Test user creation with duplicate email."""
        # Arrange
        mock_user_service.onboard_user.side_effect = ValueError("Email already exists")
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.post("/api/v1/users/", json=sample_create_user_request)
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Email already exists" in data["detail"]

    # Test 2: GET /api/v1/users/{user_id} - Get User Profile (PASSING TESTS - 90%)
    
    def test_get_user_profile_success(self, client: TestClient, mock_user_service: AsyncMock,
                                     sample_user_response: dict):
        """Test successful user profile retrieval."""
        # Arrange
        user_id = "68a0cc845efcb6a3f8ef7e95"
        mock_user_service.get_user_profile.return_value = UserResponse(**sample_user_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get(f"/api/v1/users/{user_id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["name"] == "John Doe"
            assert data["email"] == "john.doe@example.com"
            mock_user_service.get_user_profile.assert_called_once_with(user_id)
    
    def test_get_user_profile_not_found(self, client: TestClient, mock_user_service: AsyncMock):
        """Test user profile retrieval for non-existent user."""
        # Arrange
        user_id = "nonexistent_id"
        mock_user_service.get_user_profile.side_effect = ValueError("User not found")
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get(f"/api/v1/users/{user_id}")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "User not found" in data["detail"]
    
    def test_get_user_profile_invalid_id_format(self, client: TestClient):
        """Test user profile retrieval with invalid ID format."""
        # Act
        response = client.get("/api/v1/users/invalid_format")
        
        # Assert
        assert response.status_code == 200  # FastAPI will still try to process it

    # Test 3: GET /api/v1/users/{user_id}/dues - Get User Dues (PASSING TESTS - 90%)
    
    def test_get_user_dues_success(self, client: TestClient, mock_user_service: AsyncMock,
                                  sample_user_dues_response: dict):
        """Test successful user dues retrieval."""
        # Arrange
        user_id = "68a0cc845efcb6a3f8ef7e95"
        mock_user_service.get_user_dues.return_value = UserDuesResponse(**sample_user_dues_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get(f"/api/v1/users/{user_id}/dues")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user_id
            assert data["outstanding_amount"] == 150.0
            assert data["credit_limit"] == 1000.0
            assert data["available_credit"] == 850.0
            assert data["is_overdue"] == False
            mock_user_service.get_user_dues.assert_called_once_with(user_id)
    
    def test_get_user_dues_not_found(self, client: TestClient, mock_user_service: AsyncMock):
        """Test user dues retrieval for non-existent user."""
        # Arrange
        user_id = "nonexistent_id"
        mock_user_service.get_user_dues.side_effect = ValueError("User not found")
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get(f"/api/v1/users/{user_id}/dues")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "User not found" in data["detail"]

    # Test 4: GET /api/v1/users/ - Get Users by Limit Status (PASSING TESTS - 90%)
    
    def test_get_users_success_no_filters(self, client: TestClient, mock_user_service: AsyncMock,
                                         sample_user_list_response: dict):
        """Test successful users retrieval without filters."""
        # Arrange
        mock_user_service.get_users_by_limit_status.return_value = UserListResponse(**sample_user_list_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get("/api/v1/users/")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["users"]) == 2
            assert data["total_count"] == 2
            assert data["page"] == 1
            assert data["size"] == 10
            assert data["total_pages"] == 1
            mock_user_service.get_users_by_limit_status.assert_called_once_with(
                reached_limit=None, page=1, size=10
            )
    
    def test_get_users_with_limit_filter(self, client: TestClient, mock_user_service: AsyncMock,
                                        sample_user_list_response: dict):
        """Test users retrieval with limit status filter."""
        # Arrange
        mock_user_service.get_users_by_limit_status.return_value = UserListResponse(**sample_user_list_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get("/api/v1/users/?reached_limit=true")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["users"]) == 2
            mock_user_service.get_users_by_limit_status.assert_called_once_with(
                reached_limit=True, page=1, size=10
            )
    
    def test_get_users_with_pagination(self, client: TestClient, mock_user_service: AsyncMock,
                                      sample_user_list_response: dict):
        """Test users retrieval with pagination."""
        # Arrange
        mock_user_service.get_users_by_limit_status.return_value = UserListResponse(**sample_user_list_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get("/api/v1/users/?page=2&size=5")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["users"]) == 2
            mock_user_service.get_users_by_limit_status.assert_called_once_with(
                reached_limit=None, page=2, size=5
            )
    
    def test_get_users_invalid_pagination(self, client: TestClient):
        """Test users retrieval with invalid pagination parameters."""
        # Act - Test invalid page number
        response = client.get("/api/v1/users/?page=0")
        assert response.status_code == 422  # Validation error
        
        # Act - Test invalid page size
        response = client.get("/api/v1/users/?size=0")
        assert response.status_code == 422  # Validation error
        
        # Act - Test page size too large
        response = client.get("/api/v1/users/?size=101")
        assert response.status_code == 422  # Validation error

    # FAILING TESTS - 10% (Intentional failures for testing purposes)
    
    def test_create_user_should_fail_validation(self, client: TestClient):
        """INTENTIONAL FAILURE: Test that should fail due to validation."""
        # Arrange - Invalid phone number format
        invalid_request = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "invalid-phone",  # Invalid phone format
            "date_of_birth": "1990-01-01",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            }
        }
        
        # Act
        response = client.post("/api/v1/users/", json=invalid_request)
        
        # Assert - This should fail but we're testing the failure case
        assert response.status_code == 422  # This is expected to fail
        # INTENTIONAL FAILURE: Assert something that will fail
        assert response.status_code == 200  # This will fail - status should be 422
    
    def test_get_user_profile_should_fail_assertion(self, client: TestClient, mock_user_service: AsyncMock,
                                                   sample_user_response: dict):
        """INTENTIONAL FAILURE: Test that should fail due to wrong assertion."""
        # Arrange
        user_id = "68a0cc845efcb6a3f8ef7e95"
        mock_user_service.get_user_profile.return_value = UserResponse(**sample_user_response)
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get(f"/api/v1/users/{user_id}")
            
            # Assert - This should pass but we're testing a failure case
            assert response.status_code == 200
            data = response.json()
            # INTENTIONAL FAILURE: Assert something that will fail
            assert data["name"] == "Wrong Name"  # This will fail - name should be "John Doe"
    
    def test_get_user_dues_should_fail_mock(self, client: TestClient, mock_user_service: AsyncMock):
        """INTENTIONAL FAILURE: Test that should fail due to mock setup."""
        # Arrange - Mock will raise an exception
        user_id = "68a0cc845efcb6a3f8ef7e95"
        mock_user_service.get_user_dues.side_effect = Exception("Database connection failed")
        
        with patch('app.api.dependencies.get_user_service', return_value=mock_user_service):
            # Act
            response = client.get(f"/api/v1/users/{user_id}/dues")
            
            # Assert - This should fail but we're testing the failure case
            # INTENTIONAL FAILURE: Assert something that will fail
            assert response.status_code == 200  # This will fail - should be 500 due to exception


class TestUserEndpointsIntegration:
    """Integration tests for user endpoints with real database."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    def test_create_user_integration(self, client: TestClient):
        """Integration test for user creation."""
        # Arrange
        user_data = {
            "name": "Integration Test User",
            "email": "integration.test@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "address": {
                "street": "123 Test St",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345",
                "country": "USA"
            }
        }
        
        # Act
        response = client.post("/api/v1/users/", json=user_data)
        
        # Assert
        assert response.status_code in [201, 400]  # 201 if successful, 400 if email exists
        if response.status_code == 201:
            data = response.json()
            assert "user_id" in data
            assert data["name"] == "Integration Test User"
            assert data["email"] == "integration.test@example.com"
    
    def test_get_user_profile_integration(self, client: TestClient):
        """Integration test for getting user profile."""
        # Act
        response = client.get("/api/v1/users/1")  # Try to get user with custom_id 1
        
        # Assert
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "name" in data
            assert "email" in data
    
    def test_get_user_dues_integration(self, client: TestClient):
        """Integration test for getting user dues."""
        # Act
        response = client.get("/api/v1/users/1/dues")  # Try to get dues for user with custom_id 1
        
        # Assert
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data
            assert "outstanding_amount" in data
            assert "credit_limit" in data
            assert "available_credit" in data
    
    def test_get_users_integration(self, client: TestClient):
        """Integration test for getting users list."""
        # Act
        response = client.get("/api/v1/users/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "total_count" in data
        assert "page" in data
        assert "size" in data
        assert "total_pages" in data
        assert isinstance(data["users"], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
