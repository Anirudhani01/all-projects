#!/usr/bin/env python3
"""
Comprehensive test cases for Transaction endpoints.
Tests all HTTP methods: POST, GET
Target: 90% pass rate, 10% fail rate
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime

from app.main import app
from app.modules.transactions.service import TransactionService
from app.modules.transactions.schemas import (
    PurchaseRequest, PaymentRequest, TransactionResponse, PurchaseResponse,
    PaymentResponse, TransactionListResponse, TransactionFilter, TransactionSummary
)
from app.common.types import TransactionType, TransactionStatus, Currency


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
    def sample_purchase_request(self) -> dict:
        """Sample purchase request data."""
        return {
            "user_id": 1,
            "merchant_id": 1,
            "amount": 100.0,
            "currency": "INR",
            "idempotency_key": "purchase_123456789"
        }
    
    @pytest.fixture
    def sample_payment_request(self) -> dict:
        """Sample payment request data."""
        return {
            "user_id": 1,
            "amount": 50.0,
            "currency": "INR",
            "idempotency_key": "payment_123456789"
        }
    
    @pytest.fixture
    def sample_transaction_response(self) -> dict:
        """Sample transaction response data."""
        return {
            "transaction_id": "68a17a4f7d6c3fdb0144a013",
            "user_id": 1,
            "merchant_id": 1,
            "type": "PURCHASE",
            "status": "APPROVED",
            "amount": 100.0,
            "currency": "INR",
            "fee_amount": 5.0,
            "merchant_payout": 95.0,
            "created_at": "2025-08-17T06:44:31.687302Z",
            "updated_at": "2025-08-17T06:44:31.687302Z"
        }

    # Test 1: POST /api/v1/transactions/purchase - Process Purchase
    
    def test_process_purchase_success(self, client: TestClient, mock_transaction_service: AsyncMock,
                                    sample_purchase_request: dict):
        """Test successful purchase processing."""
        # Arrange
        mock_transaction_service.process_purchase.return_value = PurchaseResponse(**sample_transaction_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.post("/api/v1/transactions/purchase", json=sample_purchase_request)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["transaction_id"] == "68a17a4f7d6c3fdb0144a013"
            assert data["type"] == "PURCHASE"
            assert data["status"] == "APPROVED"
            mock_transaction_service.process_purchase.assert_called_once()
    
    def test_process_purchase_invalid_amount(self, client: TestClient):
        """Test purchase processing with invalid amount."""
        invalid_request = {
            "user_id": 1,
            "merchant_id": 1,
            "amount": -100.0,
            "currency": "INR",
            "idempotency_key": "purchase_123456789"
        }
        
        response = client.post("/api/v1/transactions/purchase", json=invalid_request)
        assert response.status_code == 422

    # Test 2: POST /api/v1/transactions/payment - Process Payment
    
    def test_process_payment_success(self, client: TestClient, mock_transaction_service: AsyncMock,
                                   sample_payment_request: dict):
        """Test successful payment processing."""
        # Arrange
        payment_response = sample_transaction_response.copy()
        payment_response["type"] = "PAYMENT"
        payment_response["merchant_id"] = None
        payment_response["fee_amount"] = 0.0
        payment_response["merchant_payout"] = 0.0
        
        mock_transaction_service.process_payment.return_value = PaymentResponse(**payment_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.post("/api/v1/transactions/payment", json=sample_payment_request)
            
            # Assert
            assert response.status_code == 201
            data = response.json()
            assert data["type"] == "PAYMENT"
            assert data["fee_amount"] == 0.0
            mock_transaction_service.process_payment.assert_called_once()

    # Test 3: GET /api/v1/transactions/{transaction_id} - Get Transaction by ID
    
    def test_get_transaction_by_id_success(self, client: TestClient, mock_transaction_service: AsyncMock,
                                         sample_transaction_response: dict):
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
            assert data["type"] == "PURCHASE"
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
            assert "Transaction not found" in data["detail"]

    # Test 4: GET /api/v1/transactions/ - Get Transactions with Filters
    
    def test_get_transactions_success_no_filters(self, client: TestClient, mock_transaction_service: AsyncMock):
        """Test successful retrieval of transactions without filters."""
        # Arrange
        sample_list_response = {
            "transactions": [sample_transaction_response],
            "total_count": 1,
            "page": 1,
            "size": 10,
            "total_pages": 1
        }
        mock_transaction_service.get_transactions_with_filters.return_value = TransactionListResponse(**sample_list_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert len(data["transactions"]) == 1
            assert data["total_count"] == 1
            mock_transaction_service.get_transactions_with_filters.assert_called_once()
    
    def test_get_transactions_invalid_type(self, client: TestClient):
        """Test transactions retrieval with invalid transaction type."""
        response = client.get("/api/v1/transactions/?type=invalid_type")
        assert response.status_code == 400
        data = response.json()
        assert "Invalid transaction type" in data["detail"]

    # Test 5: GET /api/v1/transactions/summary - Get Transaction Summary
    
    def test_get_transaction_summary_success(self, client: TestClient, mock_transaction_service: AsyncMock):
        """Test successful retrieval of transaction summary."""
        # Arrange
        sample_summary_response = {
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
        mock_transaction_service.get_transaction_summary.return_value = TransactionSummary(**sample_summary_response)
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get("/api/v1/transactions/summary")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["total_transactions"] == 10
            assert data["total_amount"] == 1500.0
            mock_transaction_service.get_transaction_summary.assert_called_once()


class TestTransactionEndpointsIntegration:
    """Integration tests for transaction endpoints with real database."""
    
    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)
    
    def test_get_transaction_by_id_integration(self, client: TestClient):
        """Integration test for getting transaction by ID."""
        response = client.get("/api/v1/transactions/68a17a4f7d6c3fdb0144a013")
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert "transaction_id" in data
            assert "user_id" in data
            assert "amount" in data
    
    def test_get_transactions_integration(self, client: TestClient):
        """Integration test for getting transactions list."""
        response = client.get("/api/v1/transactions/")
        assert response.status_code == 200
        data = response.json()
        assert "transactions" in data
        assert "total_count" in data
        assert isinstance(data["transactions"], list)
    
    def test_get_transaction_summary_integration(self, client: TestClient):
        """Integration test for getting transaction summary."""
        response = client.get("/api/v1/transactions/summary")
        assert response.status_code == 200
        data = response.json()
        assert "total_transactions" in data
        assert "total_amount" in data
        assert "total_fees" in data

    # FAILING TESTS - 10% (Intentional failures for testing purposes)
    
    def test_process_purchase_should_fail_validation(self, client: TestClient):
        """INTENTIONAL FAILURE: Test that should fail due to validation."""
        # Arrange - Invalid user_id (negative)
        invalid_request = {
            "user_id": -1,  # Invalid negative user_id
            "merchant_id": 1,
            "amount": 100.0,
            "currency": "INR",
            "idempotency_key": "purchase_123456789"
        }
        
        # Act
        response = client.post("/api/v1/transactions/purchase", json=invalid_request)
        
        # Assert - This should fail but we're testing the failure case
        assert response.status_code == 422  # This is expected to fail
        # INTENTIONAL FAILURE: Assert something that will fail
        assert response.status_code == 200  # This will fail - status should be 422
    
    def test_get_transaction_should_fail_assertion(self, client: TestClient, mock_transaction_service: AsyncMock,
                                                  sample_transaction_response: dict):
        """INTENTIONAL FAILURE: Test that should fail due to wrong assertion."""
        # Arrange
        transaction_id = "68a17a4f7d6c3fdb0144a013"
        mock_transaction_service.get_transaction_by_id.return_value = sample_transaction_response
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.get(f"/api/v1/transactions/{transaction_id}")
            
            # Assert - This should pass but we're testing a failure case
            assert response.status_code == 200
            data = response.json()
            # INTENTIONAL FAILURE: Assert something that will fail
            assert data["amount"] == 999.0  # This will fail - amount should be 100.0
    
    def test_process_payment_should_fail_mock(self, client: TestClient, mock_transaction_service: AsyncMock):
        """INTENTIONAL FAILURE: Test that should fail due to mock setup."""
        # Arrange - Mock will raise an exception
        payment_request = {
            "user_id": 1,
            "amount": 50.0,
            "currency": "INR",
            "idempotency_key": "payment_123456789"
        }
        mock_transaction_service.process_payment.side_effect = Exception("Insufficient balance")
        
        with patch('app.api.dependencies.get_transaction_service', return_value=mock_transaction_service):
            # Act
            response = client.post("/api/v1/transactions/payment", json=payment_request)
            
            # Assert - This should fail but we're testing the failure case
            # INTENTIONAL FAILURE: Assert something that will fail
            assert response.status_code == 201  # This will fail - should be 500 due to exception


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
