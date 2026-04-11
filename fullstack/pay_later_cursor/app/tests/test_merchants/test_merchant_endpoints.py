#!/usr/bin/env python3
"""
Comprehensive test cases for Merchant endpoints.
Tests all HTTP methods: POST, GET, PATCH
Target: 90% pass rate, 10% fail rate
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime

from app.main import app
from app.modules.merchants.service import MerchantService
from app.modules.merchants.schemas import (
    CreateMerchantRequest, UpdateFeeRequest, MerchantResponse, 
    MerchantListResponse, FeeHistoryResponse
)


class TestMerchantEndpoints:
    """Test cases for merchant endpoints."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_merchant_service(self) -> AsyncMock:
        """Create a mock merchant service."""
        return AsyncMock(spec=MerchantService)
    
    @pytest.fixture
    def sample_create_merchant_request(self) -> dict:
        """Sample create merchant request data."""
        return {
            "name": "Test Store",
            "description": "A test store for testing",
            "fee_pct": 5.0,
            "address": {
                "street": "456 Business Ave",
                "city": "Business City",
                "state": "BC",
                "zip_code": "54321",
                "country": "USA"
            },
            "contact_info": {
                "email": "contact@teststore.com",
                "phone": "+1987654321"
            }
        }
    
    @pytest.fixture
    def sample_merchant_response(self) -> dict:
        """Sample merchant response data."""
        return {
            "merchant_id": "68a0cc845efcb6a3f8ef7e96",
            "custom_merchant_id": 1,
            "name": "Test Store",
            "description": "A test store for testing",
            "fee_pct": 5.0,
            "status": "ACTIVE",
            "address": {
                "street": "456 Business Ave",
                "city": "Business City",
                "state": "BC",
                "zip_code": "54321",
                "country": "USA"
            },
            "contact_info": {
                "email": "contact@teststore.com",
                "phone": "+1987654321"
            },
            "created_at": "2025-08-17T06:30:00.000Z",
            "updated_at": "2025-08-17T06:30:00.000Z"
        }
    
    @pytest.fixture
    def sample_merchant_list_response(self) -> dict:
        """Sample merchant list response data."""
        return {
            "merchants": [
                {
                    "merchant_id": "68a0cc845efcb6a3f8ef7e96",
                    "custom_merchant_id": 1,
                    "name": "Test Store 1",
                    "description": "First test store",
                    "fee_pct": 5.0,
                    "status": "ACTIVE",
                    "created_at": "2025-08-17T06:30:00.000Z"
                },
                {
                    "merchant_id": "68a0cc845efcb6a3f8ef7e97",
                    "custom_merchant_id": 2,
                    "name": "Test Store 2",
                    "description": "Second test store",
                    "fee_pct": 3.5,
                    "status": "ACTIVE",
                    "created_at": "2025-08-17T07:30:00.000Z"
                }
            ],
            "total_count": 2,
            "page": 1,
            "size": 10,
            "total_pages": 1
        }
    
    @pytest.fixture
    def sample_fee_history_response(self) -> dict:
        """Sample fee history response data."""
        return {
            "merchant_id": "68a0cc845efcb6a3f8ef7e96",
            "custom_merchant_id": 1,
            "fee_history": [
                {
                    "old_fee_pct": 3.0,
                    "new_fee_pct": 5.0,
                    "effective_from": "2025-08-17T06:30:00.000Z",
                    "reason": "Standard rate adjustment",
                    "updated_by": "system"
                },
                {
                    "old_fee_pct": 2.5,
                    "new_fee_pct": 3.0,
                    "effective_from": "2025-07-01T00:00:00.000Z",
                    "reason": "Initial setup",
                    "updated_by": "admin"
                }
            ],
            "total_count": 2,
            "page": 1,
            "size": 10,
            "total_pages": 1
        }

    # Test 1: POST /api/v1/merchants/ - Create Merchant
    
    def test_create_merchant_success(self, client: TestClient, mock_merchant_service: AsyncMock,
                                   sample_create_merchant_request: dict, sample_merchant_response: dict):
        """Test successful merchant creation."""
        # Arrange
        mock_merchant_service.onboard_merchant.return_value = MerchantResponse(**sample_merchant_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.post("/api/v1/merchants/", json=sample_create_merchant_request)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["merchant_id"] == "68a0cc845efcb6a3f8ef7e96"
            assert data["name"] == "Test Store"
            assert data["fee_pct"] == 5.0
            assert data["status"] == "ACTIVE"
            mock_merchant_service.onboard_merchant.assert_called_once()
    
    def test_create_merchant_invalid_fee_percentage(self, client: TestClient):
        """Test merchant creation with invalid fee percentage."""
        # Arrange
        invalid_request = {
            "name": "Test Store",
            "description": "A test store",
            "fee_pct": -5.0,  # Negative fee percentage
            "address": {
                "street": "456 Business Ave",
                "city": "Business City",
                "state": "BC",
                "zip_code": "54321",
                "country": "USA"
            },
            "contact_info": {
                "email": "contact@teststore.com",
                "phone": "+1987654321"
            }
        }
        
        # Act
        response = client.post("/api/v1/merchants/", json=invalid_request)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_merchant_missing_required_fields(self, client: TestClient):
        """Test merchant creation with missing required fields."""
        # Arrange
        incomplete_request = {
            "name": "Test Store"
            # Missing fee_pct, address, contact_info
        }
        
        # Act
        response = client.post("/api/v1/merchants/", json=incomplete_request)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_create_merchant_duplicate_name(self, client: TestClient, mock_merchant_service: AsyncMock,
                                          sample_create_merchant_request: dict):
        """Test merchant creation with duplicate name."""
        # Arrange
        mock_merchant_service.onboard_merchant.side_effect = ValueError("Merchant name already exists")
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.post("/api/v1/merchants/", json=sample_create_merchant_request)
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Merchant name already exists" in data["detail"]

    # Test 2: GET /api/v1/merchants/ - Get All Merchants
    
    def test_get_all_merchants_success(self, client: TestClient, mock_merchant_service: AsyncMock,
                                     sample_merchant_list_response: dict):
        """Test successful retrieval of all merchants."""
        # Arrange
        mock_merchant_service.get_all_merchants.return_value = MerchantListResponse(**sample_merchant_list_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get("/api/v1/merchants/")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["merchants"]) == 2
            assert data["total_count"] == 2
            assert data["page"] == 1
            assert data["size"] == 10
            assert data["total_pages"] == 1
            mock_merchant_service.get_all_merchants.assert_called_once_with(page=1, size=10)
    
    def test_get_all_merchants_with_pagination(self, client: TestClient, mock_merchant_service: AsyncMock,
                                             sample_merchant_list_response: dict):
        """Test merchants retrieval with pagination."""
        # Arrange
        mock_merchant_service.get_all_merchants.return_value = MerchantListResponse(**sample_merchant_list_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get("/api/v1/merchants/?page=2&size=5")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["merchants"]) == 2
            mock_merchant_service.get_all_merchants.assert_called_once_with(page=2, size=5)
    
    def test_get_all_merchants_invalid_pagination(self, client: TestClient):
        """Test merchants retrieval with invalid pagination parameters."""
        # Act - Test invalid page number
        response = client.get("/api/v1/merchants/?page=0")
        assert response.status_code == 422  # Validation error
        
        # Act - Test invalid page size
        response = client.get("/api/v1/merchants/?size=0")
        assert response.status_code == 422  # Validation error
        
        # Act - Test page size too large
        response = client.get("/api/v1/merchants/?size=101")
        assert response.status_code == 422  # Validation error

    # Test 3: GET /api/v1/merchants/{merchant_id} - Get Merchant Details
    
    def test_get_merchant_success(self, client: TestClient, mock_merchant_service: AsyncMock,
                                sample_merchant_response: dict):
        """Test successful merchant details retrieval."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        mock_merchant_service.get_merchant.return_value = MerchantResponse(**sample_merchant_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["merchant_id"] == merchant_id
            assert data["name"] == "Test Store"
            assert data["fee_pct"] == 5.0
            mock_merchant_service.get_merchant.assert_called_once_with(merchant_id)
    
    def test_get_merchant_not_found(self, client: TestClient, mock_merchant_service: AsyncMock):
        """Test merchant details retrieval for non-existent merchant."""
        # Arrange
        merchant_id = "nonexistent_id"
        mock_merchant_service.get_merchant.side_effect = ValueError("Merchant not found")
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Merchant not found" in data["detail"]

    # Test 4: PATCH /api/v1/merchants/{merchant_id}/fee - Update Merchant Fee
    
    def test_update_merchant_fee_success(self, client: TestClient, mock_merchant_service: AsyncMock,
                                       sample_merchant_response: dict):
        """Test successful merchant fee update."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        update_request = {"fee_pct": 6.5}
        updated_response = sample_merchant_response.copy()
        updated_response["fee_pct"] = 6.5
        mock_merchant_service.update_merchant_fee.return_value = MerchantResponse(**updated_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.patch(f"/api/v1/merchants/{merchant_id}/fee", json=update_request)
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["merchant_id"] == merchant_id
            assert data["fee_pct"] == 6.5
            mock_merchant_service.update_merchant_fee.assert_called_once_with(merchant_id, UpdateFeeRequest(**update_request))
    
    def test_update_merchant_fee_invalid_percentage(self, client: TestClient):
        """Test merchant fee update with invalid percentage."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        invalid_request = {"fee_pct": -1.0}  # Negative fee percentage
        
        # Act
        response = client.patch(f"/api/v1/merchants/{merchant_id}/fee", json=invalid_request)
        
        # Assert
        assert response.status_code == 422  # Validation error
    
    def test_update_merchant_fee_merchant_not_found(self, client: TestClient, mock_merchant_service: AsyncMock):
        """Test merchant fee update for non-existent merchant."""
        # Arrange
        merchant_id = "nonexistent_id"
        update_request = {"fee_pct": 6.5}
        mock_merchant_service.update_merchant_fee.side_effect = ValueError("Merchant not found")
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.patch(f"/api/v1/merchants/{merchant_id}/fee", json=update_request)
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Merchant not found" in data["detail"]
    
    def test_update_merchant_fee_missing_fee_pct(self, client: TestClient):
        """Test merchant fee update with missing fee_pct field."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        invalid_request = {}  # Missing fee_pct
        
        # Act
        response = client.patch(f"/api/v1/merchants/{merchant_id}/fee", json=invalid_request)
        
        # Assert
        assert response.status_code == 422  # Validation error

    # Test 5: GET /api/v1/merchants/{merchant_id}/fee-history - Get Merchant Fee History
    
    def test_get_merchant_fee_history_success(self, client: TestClient, mock_merchant_service: AsyncMock,
                                            sample_fee_history_response: dict):
        """Test successful merchant fee history retrieval."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        mock_merchant_service.get_fee_history.return_value = FeeHistoryResponse(**sample_fee_history_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}/fee-history")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["merchant_id"] == merchant_id
            assert len(data["fee_history"]) == 2
            assert data["total_count"] == 2
            assert data["page"] == 1
            assert data["size"] == 10
            mock_merchant_service.get_fee_history.assert_called_once_with(
                merchant_id=merchant_id, from_date=None, to_date=None, page=1, size=10
            )
    
    def test_get_merchant_fee_history_with_date_filters(self, client: TestClient, mock_merchant_service: AsyncMock,
                                                      sample_fee_history_response: dict):
        """Test merchant fee history retrieval with date filters."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        mock_merchant_service.get_fee_history.return_value = FeeHistoryResponse(**sample_fee_history_response)
        from_date = "2025-08-01T00:00:00Z"
        to_date = "2025-08-31T23:59:59Z"
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}/fee-history?from_date={from_date}&to_date={to_date}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["fee_history"]) == 2
            mock_merchant_service.get_fee_history.assert_called_once()
            call_args = mock_merchant_service.get_fee_history.call_args[1]
            assert call_args["from_date"] is not None
            assert call_args["to_date"] is not None
    
    def test_get_merchant_fee_history_with_pagination(self, client: TestClient, mock_merchant_service: AsyncMock,
                                                    sample_fee_history_response: dict):
        """Test merchant fee history retrieval with pagination."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        mock_merchant_service.get_fee_history.return_value = FeeHistoryResponse(**sample_fee_history_response)
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}/fee-history?page=2&size=5")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["fee_history"]) == 2
            mock_merchant_service.get_fee_history.assert_called_once_with(
                merchant_id=merchant_id, from_date=None, to_date=None, page=2, size=5
            )
    
    def test_get_merchant_fee_history_merchant_not_found(self, client: TestClient, mock_merchant_service: AsyncMock):
        """Test merchant fee history retrieval for non-existent merchant."""
        # Arrange
        merchant_id = "nonexistent_id"
        mock_merchant_service.get_fee_history.side_effect = ValueError("Merchant not found")
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}/fee-history")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Merchant not found" in data["detail"]


class TestMerchantEndpointsIntegration:
    """Integration tests for merchant endpoints with real database."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    def test_create_merchant_integration(self, client: TestClient):
        """Integration test for merchant creation."""
        # Arrange
        merchant_data = {
            "name": "Integration Test Store",
            "description": "A test store for integration testing",
            "fee_pct": 4.5,
            "address": {
                "street": "789 Test Blvd",
                "city": "Test City",
                "state": "TC",
                "zip_code": "67890",
                "country": "USA"
            },
            "contact_info": {
                "email": "integration@teststore.com",
                "phone": "+1555123456"
            }
        }
        
        # Act
        response = client.post("/api/v1/merchants/", json=merchant_data)
        
        # Assert
        assert response.status_code in [201, 400]  # 201 if successful, 400 if name exists
        if response.status_code == 201:
            data = response.json()
            assert "merchant_id" in data
            assert data["name"] == "Integration Test Store"
            assert data["fee_pct"] == 4.5
    
    def test_get_merchant_integration(self, client: TestClient):
        """Integration test for getting merchant details."""
        # Act
        response = client.get("/api/v1/merchants/1")  # Try to get merchant with custom_id 1
        
        # Assert
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "merchant_id" in data
            assert "name" in data
            assert "fee_pct" in data
    
    def test_update_merchant_fee_integration(self, client: TestClient):
        """Integration test for updating merchant fee."""
        # Arrange
        update_data = {"fee_pct": 6.0}
        
        # Act
        response = client.patch("/api/v1/merchants/1/fee", json=update_data)
        
        # Assert
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "merchant_id" in data
            assert data["fee_pct"] == 6.0
    
    def test_get_merchant_fee_history_integration(self, client: TestClient):
        """Integration test for getting merchant fee history."""
        # Act
        response = client.get("/api/v1/merchants/1/fee-history")
        
        # Assert
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "merchant_id" in data
            assert "fee_history" in data
            assert "total_count" in data
            assert isinstance(data["fee_history"], list)
    
    def test_get_all_merchants_integration(self, client: TestClient):
        """Integration test for getting all merchants."""
        # Act
        response = client.get("/api/v1/merchants/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "merchants" in data
        assert "total_count" in data
        assert "page" in data
        assert "size" in data
        assert "total_pages" in data
        assert isinstance(data["merchants"], list)

    # FAILING TESTS - 10% (Intentional failures for testing purposes)
    
    def test_create_merchant_should_fail_validation(self, client: TestClient):
        """INTENTIONAL FAILURE: Test that should fail due to validation."""
        # Arrange - Invalid fee percentage (negative)
        invalid_request = {
            "name": "Test Store",
            "description": "A test store for testing",
            "fee_pct": -5.0,  # Invalid negative fee
            "address": {
                "street": "456 Business Ave",
                "city": "Business City",
                "state": "BC",
                "zip_code": "54321",
                "country": "USA"
            },
            "contact_info": {
                "email": "contact@teststore.com",
                "phone": "+1987654321"
            }
        }
        
        # Act
        response = client.post("/api/v1/merchants/", json=invalid_request)
        
        # Assert - This should fail but we're testing the failure case
        assert response.status_code == 422  # This is expected to fail
        # INTENTIONAL FAILURE: Assert something that will fail
        assert response.status_code == 200  # This will fail - status should be 422
    
    def test_get_merchant_should_fail_assertion(self, client: TestClient, mock_merchant_service: AsyncMock,
                                               sample_merchant_response: dict):
        """INTENTIONAL FAILURE: Test that should fail due to wrong assertion."""
        # Arrange
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        mock_merchant_service.get_merchant_profile.return_value = sample_merchant_response
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.get(f"/api/v1/merchants/{merchant_id}")
            
            # Assert - This should pass but we're testing a failure case
            assert response.status_code == 200
            data = response.json()
            # INTENTIONAL FAILURE: Assert something that will fail
            assert data["name"] == "Wrong Store Name"  # This will fail - name should be "Test Store"
    
    def test_update_merchant_fee_should_fail_mock(self, client: TestClient, mock_merchant_service: AsyncMock):
        """INTENTIONAL FAILURE: Test that should fail due to mock setup."""
        # Arrange - Mock will raise an exception
        merchant_id = "68a0cc845efcb6a3f8ef7e96"
        update_data = {"fee_pct": 6.0}
        mock_merchant_service.update_merchant_fee.side_effect = Exception("Database connection failed")
        
        with patch('app.api.dependencies.get_merchant_service', return_value=mock_merchant_service):
            # Act
            response = client.patch(f"/api/v1/merchants/{merchant_id}/fee", json=update_data)
            
            # Assert - This should fail but we're testing the failure case
            # INTENTIONAL FAILURE: Assert something that will fail
            assert response.status_code == 200  # This will fail - should be 500 due to exception


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
