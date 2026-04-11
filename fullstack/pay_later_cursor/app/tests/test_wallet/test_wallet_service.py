"""
Unit tests for wallet service.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from bson import ObjectId

from app.modules.wallet.service import WalletService
from app.modules.wallet.repository import WalletRepository
from app.common.exceptions import InsufficientBalance


class TestWalletService:
    """Test WalletService."""
    
    @pytest.fixture
    def mock_repository(self):
        """Create a mock wallet repository."""
        return Mock(spec=WalletRepository)
    
    @pytest.fixture
    def wallet_service(self, mock_repository):
        """Create a wallet service with mock repository."""
        return WalletService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_calculate_fee(self, wallet_service):
        """Test fee calculation."""
        amount = 500.0
        fee_pct = 10.0
        
        fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
        
        assert fee_amount == 50.0
    
    @pytest.mark.asyncio
    async def test_calculate_fee_zero_percentage(self, wallet_service):
        """Test fee calculation with zero percentage."""
        amount = 500.0
        fee_pct = 0.0
        
        fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
        
        assert fee_amount == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_total_amount(self, wallet_service):
        """Test total amount calculation."""
        amount = 500.0
        fee_amount = 50.0
        
        total_amount = await wallet_service.calculate_total_amount(amount, fee_amount)
        
        assert total_amount == 550.0
    
    @pytest.mark.asyncio
    async def test_get_user_credit_info_success(self, wallet_service, mock_repository):
        """Test getting user credit info successfully."""
        user_id = ObjectId()
        mock_repository.get_user_balance.return_value = {
            "credit_limit": 1000.0,
            "outstanding_amount": 200.0,
            "available_credit": 800.0,
            "total_merchant_usage": 300.0,
            "total_purchases": 500.0,
            "total_payments": 300.0
        }
        mock_repository.get_user_by_id.return_value = {
            "credit_limit": 1000.0
        }
        
        credit_info = await wallet_service.get_user_credit_info(user_id)
        
        assert credit_info is not None
        assert credit_info["credit_limit"] == 1000.0
        assert credit_info["outstanding_amount"] == 200.0
        assert credit_info["available_credit"] == 800.0
        assert credit_info["total_merchant_usage"] == 300.0
        mock_repository.get_user_balance.assert_called_once_with(user_id)
        mock_repository.get_user_by_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_credit_info_no_balance(self, wallet_service, mock_repository):
        """Test getting user credit info when no balance exists."""
        user_id = ObjectId()
        mock_repository.get_user_balance.return_value = None
        
        credit_info = await wallet_service.get_user_credit_info(user_id)
        
        assert credit_info is None
        mock_repository.get_user_balance.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_merchant_wallet_balance_success(self, wallet_service, mock_repository):
        """Test getting merchant wallet balance successfully."""
        merchant_id = ObjectId()
        mock_repository.get_merchant_by_id.return_value = {
            "wallet_balance": 500.0
        }
        
        balance = await wallet_service.get_merchant_wallet_balance(merchant_id)
        
        assert balance == 500.0
        mock_repository.get_merchant_by_id.assert_called_once_with(merchant_id)
    
    @pytest.mark.asyncio
    async def test_get_merchant_wallet_balance_no_merchant(self, wallet_service, mock_repository):
        """Test getting merchant wallet balance when merchant doesn't exist."""
        merchant_id = ObjectId()
        mock_repository.get_merchant_by_id.return_value = None
        
        balance = await wallet_service.get_merchant_wallet_balance(merchant_id)
        
        assert balance == 0.0
        mock_repository.get_merchant_by_id.assert_called_once_with(merchant_id)
    
    @pytest.mark.asyncio
    async def test_check_user_credit_sufficiency_sufficient(self, wallet_service, mock_repository):
        """Test credit sufficiency check when user has sufficient credit."""
        user_id = ObjectId()
        amount = 500.0
        
        # Mock the get_user_credit_info method
        wallet_service.get_user_credit_info = AsyncMock(return_value={
            "available_credit": 800.0
        })
        
        has_sufficient = await wallet_service.check_user_credit_sufficiency(user_id, amount)
        
        assert has_sufficient is True
        wallet_service.get_user_credit_info.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_check_user_credit_sufficiency_insufficient(self, wallet_service, mock_repository):
        """Test credit sufficiency check when user has insufficient credit."""
        user_id = ObjectId()
        amount = 1000.0
        
        # Mock the get_user_credit_info method
        wallet_service.get_user_credit_info = AsyncMock(return_value={
            "available_credit": 500.0
        })
        
        has_sufficient = await wallet_service.check_user_credit_sufficiency(user_id, amount)
        
        assert has_sufficient is False
        wallet_service.get_user_credit_info.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_check_user_credit_sufficiency_no_credit_info(self, wallet_service, mock_repository):
        """Test credit sufficiency check when no credit info exists."""
        user_id = ObjectId()
        amount = 500.0
        
        # Mock the get_user_credit_info method
        wallet_service.get_user_credit_info = AsyncMock(return_value=None)
        
        has_sufficient = await wallet_service.check_user_credit_sufficiency(user_id, amount)
        
        assert has_sufficient is False
        wallet_service.get_user_credit_info.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_wallet_transactions_success(self, wallet_service, mock_repository):
        """Test getting wallet transactions successfully."""
        user_id = ObjectId()
        merchant_id = ObjectId()
        limit = 10
        
        mock_transactions = [
            {
                "_id": ObjectId(),
                "type": "wallet_add",
                "user_id": user_id,
                "merchant_id": merchant_id,
                "amount": 500.0,
                "fee_amount": 50.0,
                "total_amount": 550.0,
                "status": "APPROVED",
                "created_at": "2025-08-18T10:00:00Z"
            }
        ]
        mock_repository.get_wallet_transactions.return_value = mock_transactions
        
        transactions = await wallet_service.get_wallet_transactions(
            user_id=user_id,
            merchant_id=merchant_id,
            limit=limit
        )
        
        assert transactions == mock_transactions
        mock_repository.get_wallet_transactions.assert_called_once_with(
            user_id=user_id,
            merchant_id=merchant_id,
            limit=limit
        )
    
    @pytest.mark.asyncio
    async def test_get_user_merchant_usage_success(self, wallet_service, mock_repository):
        """Test getting user merchant usage successfully."""
        user_id = ObjectId()
        
        # Mock the get_user_credit_info method
        wallet_service.get_user_credit_info = AsyncMock(return_value={
            "credit_limit": 1000.0,
            "outstanding_amount": 200.0,
            "available_credit": 800.0,
            "total_merchant_usage": 300.0
        })
        
        # Mock the get_merchant_usage_breakdown method
        wallet_service.get_merchant_usage_breakdown = AsyncMock(return_value={
            "1": 150.0,
            "2": 150.0
        })
        
        usage_info = await wallet_service.get_user_merchant_usage(user_id)
        
        assert usage_info is not None
        assert usage_info["total_usage"] == 300.0
        assert usage_info["credit_limit"] == 1000.0
        assert usage_info["available_credit"] == 800.0
        assert usage_info["outstanding_amount"] == 200.0
        assert usage_info["merchant_count"] == 2
        assert usage_info["merchant_breakdown"] == {"1": 150.0, "2": 150.0}
        
        wallet_service.get_user_credit_info.assert_called_once_with(user_id)
        wallet_service.get_merchant_usage_breakdown.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_merchant_wallet_summary_success(self, wallet_service, mock_repository):
        """Test getting merchant wallet summary successfully."""
        merchant_id = ObjectId()
        
        # Mock the get_merchant_by_id method
        mock_repository.get_merchant_by_id.return_value = {
            "_id": merchant_id,
            "name": "Test Merchant",
            "wallet_balance": 500.0,
            "total_received": 1000.0,
            "current_fee_pct": 10.0
        }
        
        # Mock the get_wallet_transaction_count method
        mock_repository.get_wallet_transaction_count.return_value = 5
        
        # Mock the get_total_fees_earned method
        mock_repository.get_total_fees_earned.return_value = 100.0
        
        summary = await wallet_service.get_merchant_wallet_summary(merchant_id)
        
        assert summary is not None
        assert summary["merchant_id"] == str(merchant_id)
        assert summary["merchant_name"] == "Test Merchant"
        assert summary["current_balance"] == 500.0
        assert summary["total_received"] == 1000.0
        assert summary["total_fees"] == 100.0
        assert summary["transaction_count"] == 5
        assert summary["fee_percentage"] == 10.0
        
        mock_repository.get_merchant_by_id.assert_called_once_with(merchant_id)
        mock_repository.get_wallet_transaction_count.assert_called_once_with(merchant_id)
        mock_repository.get_total_fees_earned.assert_called_once_with(merchant_id)
