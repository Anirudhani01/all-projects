#!/usr/bin/env python3
"""
Comprehensive test cases for transaction endpoints.
Tests the three main GET endpoints:
1. GET /api/v1/transactions/{transaction_id}
2. GET /api/v1/transactions/
3. GET /api/v1/transactions/summary
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

# Import the application and dependencies
from app.main import app
from app.modules.transactions.service import TransactionService
from app.modules.transactions.schemas import (
    TransactionResponse, TransactionListResponse, TransactionSummary,
    TransactionFilter
)
from app.common.types import TransactionType, TransactionStatus, Currency
from app.modules.transactions.models import Transaction


class TestTransactionEndpoints:
    """Test cases for transaction endpoints."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_transaction_service(self) -> AsyncMock:
        """Create a mock transaction service."""
        return AsyncMock(spec=TransactionService)
    
    @pytest.fixture
    def sample_transaction_response(self) -> dict:
        """Sample transaction response data."""
        return {
            "transaction_id": "68a17a4f7d6c3fdb0144a013",
            "user_id": 3,
            "merchant_id": 2,
            "type": "PURCHASE",
            "status": "APPROVED",
            "amount": 100.0,
            "currency": "INR",
            "fee_amount": 5.0,
            "merchant_payout": 95.0,
            "created_at": "2025-08-17T06:44:31.687302Z",
            "updated_at": "2025-08-17T06:44:31.687302Z"
        }
    
    @pytest.fixture
    def sample_transaction_list_response(self) -> dict:
        """Sample transaction list response data."""
        return {
            "transactions": [
                {
                    "transaction_id": "68a17a4f7d6c3fdb0144a013",
                    "user_id": 3,
                    "merchant_id": 2,
                    "type": "PURCHASE",
                    "status": "APPROVED",
                    "amount": 100.0,
                    "currency": "INR",
                    "fee_amount": 5.0,
                    "merchant_payout": 95.0,
                    "created_at": "2025-08-17T06:44:31.687302Z",
                    "updated_at": "2025-08-17T06:44:31.687302Z"
                },
                {
                    "transaction_id": "68a17a4f7d6c3fdb0144a014",
                    "user_id": 3,
                    "merchant_id": 2,
                    "type": "PAYMENT",
                    "status": "APPROVED",
                    "amount": 50.0,
                    "currency": "INR",
                    "fee_amount": 0.0,
                    "merchant_payout": 0.0,
                    "created_at": "2025-08-17T06:45:31.687302Z",
                    "updated_at": "2025-08-17T06:45:31.687302Z"
                }
            ],
            "total_count": 2,
            "page": 1,
            "size": 10,
            "total_pages": 1
        }
    
    @pytest.fixture
    def sample_transaction_summary_response(self) -> dict:
        """Sample transaction summary response data."""
        return {
            "total_transactions": 10,
            "total_amount": 1500.0,
            "total_fees": 75.0,
            "total_merchant_payout": 1425.0,
            "purchase_count": 6,
            "payment_count": 4,
            "approved_count": 9,
            "rejected_count": 1,
            "average_transaction_amount": 150.0
        }

    # Test 1: GET /api/v1/transactions/{transaction_id}
    
    def test_get_transaction_by_id_success(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_response: dict):
        """Test successful retrieval of transaction by ID."""
        # Arrange
        transaction_id = "68a17a4f7d6c3fdb0144a013"
        mock_transaction_service.get_transaction.return_value = TransactionResponse(**sample_transaction_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get(f"/api/v1/transactions/{transaction_id}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["transaction_id"] == transaction_id
            assert data["user_id"] == 3
            assert data["type"] == "PURCHASE"
            assert data["status"] == "APPROVED"
            assert data["amount"] == 100.0
            mock_transaction_service.get_transaction.assert_called_once_with(transaction_id)
    
    def test_get_transaction_by_id_not_found(self, client: TestClient, mock_transaction_service: AsyncMock):
        """Test transaction not found scenario."""
        # Arrange
        transaction_id = "nonexistent_id"
        mock_transaction_service.get_transaction.side_effect = ValueError("Transaction not found")
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get(f"/api/v1/transactions/{transaction_id}")
            
            # Assert
            assert response.status_code == 404
            data = response.json()
            assert "detail" in data
            assert "Transaction not found" in data["detail"]
    
    def test_get_transaction_by_id_invalid_format(self, client: TestClient):
        """Test invalid transaction ID format."""
        # Act
        response = client.get("/api/v1/transactions/invalid_format")
        
        # Assert
        assert response.status_code == 200  # FastAPI will still try to process it
    
    # Test 2: GET /api/v1/transactions/
    
    def test_get_transactions_success_no_filters(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test successful retrieval of transactions without filters."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            assert data["total_count"] == 2
            assert data["page"] == 1
            assert data["size"] == 10
            assert data["total_pages"] == 1
    
    def test_get_transactions_with_user_filter(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test transactions retrieval with user ID filter."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/?user_id=3")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            # Verify the service was called with correct filter
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
            call_args = mock_transaction_service.get_transactions_with_filters.call_args[0][0]
            assert call_args.user_id == 3
    
    def test_get_transactions_with_merchant_filter(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test transactions retrieval with merchant ID filter."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/?merchant_id=2")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            # Verify the service was called with correct filter
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
            call_args = mock_transaction_service.get_transactions_with_filters.call_args[0][0]
            assert call_args.merchant_id == 2
    
    def test_get_transactions_with_type_filter(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test transactions retrieval with transaction type filter."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/?type=purchase")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            # Verify the service was called with correct filter
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
            call_args = mock_transaction_service.get_transactions_with_filters.call_args[0][0]
            assert call_args.type == TransactionType.PURCHASE
    
    def test_get_transactions_with_status_filter(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test transactions retrieval with transaction status filter."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/?status=approved")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            # Verify the service was called with correct filter
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
            call_args = mock_transaction_service.get_transactions_with_filters.call_args[0][0]
            assert call_args.status == TransactionStatus.APPROVED
    
    def test_get_transactions_with_date_filters(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test transactions retrieval with date filters."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        from_date = "2025-08-01T00:00:00Z"
        to_date = "2025-08-31T23:59:59Z"
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get(f"/api/v1/transactions/?from_date={from_date}&to_date={to_date}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            # Verify the service was called with correct filter
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
            call_args = mock_transaction_service.get_transactions_with_filters.call_args[0][0]
            assert call_args.from_date is not None
            assert call_args.to_date is not None
    
    def test_get_transactions_with_pagination(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_list_response: dict):
        """Test transactions retrieval with pagination."""
        # Arrange
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_transaction_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/?page=2&size=5")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 2
            # Verify the service was called with correct pagination
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
            call_args = mock_transaction_service.get_transactions_with_filters.call_args[0][0]
            assert call_args.page == 2
            assert call_args.size == 5
    
    def test_get_transactions_invalid_type(self, client: TestClient):
        """Test transactions retrieval with invalid transaction type."""
        # Act
        response = client.get("/api/v1/transactions/?type=invalid_type")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid transaction type" in data["detail"]
    
    def test_get_transactions_invalid_status(self, client: TestClient):
        """Test transactions retrieval with invalid transaction status."""
        # Act
        response = client.get("/api/v1/transactions/?status=invalid_status")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid transaction status" in data["detail"]
    
    def test_get_transactions_invalid_pagination(self, client: TestClient):
        """Test transactions retrieval with invalid pagination parameters."""
        # Act - Test invalid page number
        response = client.get("/api/v1/transactions/?page=0")
        assert response.status_code == 422  # Validation error
        
        # Act - Test invalid page size
        response = client.get("/api/v1/transactions/?size=0")
        assert response.status_code == 422  # Validation error
        
        # Act - Test page size too large
        response = client.get("/api/v1/transactions/?size=101")
        assert response.status_code == 422  # Validation error
    
    # Test 3: GET /api/v1/transactions/summary
    
    def test_get_transaction_summary_success_no_filters(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_summary_response: dict):
        """Test successful retrieval of transaction summary without filters."""
        # Arrange
        mock_transaction_service.get_transaction_summary.return_value = TransactionSummary(**sample_transaction_summary_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/summary")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_transactions"] == 10
            assert data["total_amount"] == 1500.0
            assert data["total_fees"] == 75.0
            assert data["total_merchant_payout"] == 1425.0
            assert data["purchase_count"] == 6
            assert data["payment_count"] == 4
            assert data["approved_count"] == 9
            assert data["rejected_count"] == 1
            assert data["average_transaction_amount"] == 150.0
    
    def test_get_transaction_summary_with_user_filter(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_summary_response: dict):
        """Test transaction summary with user ID filter."""
        # Arrange
        mock_transaction_service.get_transaction_summary.return_value = TransactionSummary(**sample_transaction_summary_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/summary?user_id=3")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_transactions"] == 10
            # Verify the service was called with correct parameters
            mock_transaction_service.get_transaction_summary.assert_called_once_with(
                user_id=3, merchant_id=None, from_date=None, to_date=None
            )
    
    def test_get_transaction_summary_with_merchant_filter(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_summary_response: dict):
        """Test transaction summary with merchant ID filter."""
        # Arrange
        mock_transaction_service.get_transaction_summary.return_value = TransactionSummary(**sample_transaction_summary_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/summary?merchant_id=2")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_transactions"] == 10
            # Verify the service was called with correct parameters
            mock_transaction_service.get_transaction_summary.assert_called_once_with(
                user_id=None, merchant_id=2, from_date=None, to_date=None
            )
    
    def test_get_transaction_summary_with_date_filters(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_summary_response: dict):
        """Test transaction summary with date filters."""
        # Arrange
        mock_transaction_service.get_transaction_summary.return_value = TransactionSummary(**sample_transaction_summary_response)
        from_date = "2025-08-01T00:00:00Z"
        to_date = "2025-08-31T23:59:59Z"
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get(f"/api/v1/transactions/summary?from_date={from_date}&to_date={to_date}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_transactions"] == 10
            # Verify the service was called with correct parameters
            mock_transaction_service.get_transaction_summary.assert_called_once()
            call_args = mock_transaction_service.get_transaction_summary.call_args[1]
            assert call_args["from_date"] is not None
            assert call_args["to_date"] is not None
    
    def test_get_transaction_summary_with_all_filters(self, client: TestClient, mock_transaction_service: AsyncMock, sample_transaction_summary_response: dict):
        """Test transaction summary with all filters combined."""
        # Arrange
        mock_transaction_service.get_transaction_summary.return_value = TransactionSummary(**sample_transaction_summary_response)
        from_date = "2025-08-01T00:00:00Z"
        to_date = "2025-08-31T23:59:59Z"
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get(f"/api/v1/transactions/summary?user_id=3&merchant_id=2&from_date={from_date}&to_date={to_date}")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_transactions"] == 10
            # Verify the service was called with correct parameters
            mock_transaction_service.get_transaction_summary.assert_called_once_with(
                user_id=3, merchant_id=2, from_date=call_args["from_date"], to_date=call_args["to_date"]
            )
    
    def test_get_transaction_summary_service_error(self, client: TestClient, mock_transaction_service: AsyncMock):
        """Test transaction summary when service raises an error."""
        # Arrange
        mock_transaction_service.get_transaction_summary.side_effect = ValueError("Invalid date range")
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/summary")
            
            # Assert
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            assert "Invalid date range" in data["detail"]


class TestTransactionEndpointsIntegration:
    """Integration tests for transaction endpoints with real database."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    def test_get_transaction_by_id_integration(self, client: TestClient):
        """Integration test for getting transaction by ID."""
        # This test requires a running application with MongoDB
        # You would need to create a test transaction first
        
        # Act
        response = client.get("/api/v1/transactions/68a17a4f7d6c3fdb0144a013")
        
        # Assert
        # This will either return 200 with data or 404 if transaction doesn't exist
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "transaction_id" in data
            assert "user_id" in data
            assert "amount" in data
    
    def test_get_transactions_integration(self, client: TestClient):
        """Integration test for getting transactions list."""
        # Act
        response = client.get("/api/v1/transactions/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total_count" in data
        assert "page" in data
        assert "size" in data
        assert "total_pages" in data
        assert isinstance(data["transactions"], list)
    
    def test_get_transaction_summary_integration(self, client: TestClient):
        """Integration test for getting transaction summary."""
        # Act
        response = client.get("/api/v1/transactions/summary")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "total_transactions" in data
        assert "total_amount" in data
        assert "total_fees" in data
        assert "total_merchant_payout" in data
        assert "purchase_count" in data
        assert "payment_count" in data
        assert "approved_count" in data
        assert "rejected_count" in data
        assert "average_transaction_amount" in data


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
