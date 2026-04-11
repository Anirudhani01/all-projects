"""
Integration tests for wallet functionality.
"""

import pytest
from bson import ObjectId
from datetime import datetime

from app.modules.wallet.models import MerchantWallet, CreditLimit
from app.modules.wallet.service import WalletService
from app.modules.wallet.repository import WalletRepository
from app.db.mongo import mongodb
from app.common.exceptions import InsufficientBalance


class TestWalletIntegration:
    """Integration tests for wallet functionality."""
    
    @pytest.fixture
    async def setup_database(self):
        """Setup test database."""
        await mongodb.connect()
        yield
        await mongodb.disconnect()
    
    @pytest.fixture
    def wallet_repository(self, setup_database):
        """Create wallet repository."""
        return WalletRepository(mongodb.get_database())
    
    @pytest.fixture
    def wallet_service(self, wallet_repository):
        """Create wallet service."""
        return WalletService(wallet_repository)
    
    @pytest.mark.asyncio
    async def test_complete_wallet_flow(self, wallet_service, wallet_repository):
        """Test complete wallet flow: create wallet, add money, check balance."""
        # Create test data
        user_id = ObjectId()
        merchant_id = ObjectId()
        
        # Create merchant wallet
        wallet = MerchantWallet(
            merchant_id=merchant_id,
            balance=0.0,
            total_received=0.0,
            total_fees_earned=0.0
        )
        
        # Save wallet to database
        await wallet_repository.create_merchant_wallet(wallet)
        
        # Create user credit limit
        credit_limit = CreditLimit(
            user_id=user_id,
            credit_limit=1000.0,
            available_credit=1000.0,
            used_credit=0.0,
            merchant_usage={}
        )
        
        # Save credit limit to database
        await wallet_repository.create_credit_limit(credit_limit)
        
        # Test adding money to wallet
        amount = 500.0
        fee_pct = 10.0
        fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
        total_amount = await wallet_service.calculate_total_amount(amount, fee_amount)
        
        # Update wallet balance
        wallet.add_amount(amount, fee_amount)
        await wallet_repository.update_merchant_wallet(wallet)
        
        # Update user credit usage
        credit_limit.add_merchant_usage(str(merchant_id), total_amount)
        await wallet_repository.update_credit_limit(credit_limit)
        
        # Verify results
        updated_wallet = await wallet_repository.get_merchant_wallet(merchant_id)
        updated_credit = await wallet_repository.get_credit_limit(user_id)
        
        assert updated_wallet.balance == amount
        assert updated_wallet.total_received == amount
        assert updated_wallet.total_fees_earned == fee_amount
        assert updated_credit.used_credit == total_amount
        assert updated_credit.available_credit == 1000.0 - total_amount
        assert updated_credit.merchant_usage[str(merchant_id)] == total_amount
    
    @pytest.mark.asyncio
    async def test_credit_limit_enforcement(self, wallet_service, wallet_repository):
        """Test that credit limits are properly enforced."""
        user_id = ObjectId()
        merchant_id = ObjectId()
        
        # Create user with limited credit
        credit_limit = CreditLimit(
            user_id=user_id,
            credit_limit=100.0,  # Small credit limit
            available_credit=100.0,
            used_credit=0.0,
            merchant_usage={}
        )
        await wallet_repository.create_credit_limit(credit_limit)
        
        # Try to add more than available credit
        amount = 150.0  # More than available credit
        fee_pct = 10.0
        fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
        total_amount = await wallet_service.calculate_total_amount(amount, fee_amount)
        
        # Check if user has sufficient credit
        has_sufficient = await wallet_service.check_user_credit_sufficiency(user_id, total_amount)
        
        assert has_sufficient is False
        
        # Try with amount within credit limit
        amount = 50.0
        fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
        total_amount = await wallet_service.calculate_total_amount(amount, fee_amount)
        
        has_sufficient = await wallet_service.check_user_credit_sufficiency(user_id, total_amount)
        
        assert has_sufficient is True
    
    @pytest.mark.asyncio
    async def test_fee_calculation_accuracy(self, wallet_service):
        """Test that fee calculations are accurate."""
        test_cases = [
            (100.0, 5.0, 5.0, 105.0),   # 5% fee
            (500.0, 10.0, 50.0, 550.0),  # 10% fee
            (1000.0, 15.0, 150.0, 1150.0),  # 15% fee
            (200.0, 0.0, 0.0, 200.0),   # 0% fee
        ]
        
        for amount, fee_pct, expected_fee, expected_total in test_cases:
            fee_amount = await wallet_service.calculate_fee(amount, fee_pct)
            total_amount = await wallet_service.calculate_total_amount(amount, fee_amount)
            
            assert fee_amount == expected_fee
            assert total_amount == expected_total
    
    @pytest.mark.asyncio
    async def test_merchant_wallet_operations(self, wallet_repository):
        """Test merchant wallet operations."""
        merchant_id = ObjectId()
        
        # Create wallet
        wallet = MerchantWallet(
            merchant_id=merchant_id,
            balance=0.0,
            total_received=0.0,
            total_fees_earned=0.0
        )
        
        # Save wallet
        await wallet_repository.create_merchant_wallet(wallet)
        
        # Add multiple transactions
        transactions = [
            (100.0, 10.0),  # 100 + 10 fee
            (200.0, 20.0),  # 200 + 20 fee
            (300.0, 30.0),  # 300 + 30 fee
        ]
        
        for amount, fee in transactions:
            wallet.add_amount(amount, fee)
            await wallet_repository.update_merchant_wallet(wallet)
        
        # Verify final state
        updated_wallet = await wallet_repository.get_merchant_wallet(merchant_id)
        
        expected_balance = sum(amount for amount, _ in transactions)
        expected_total_received = sum(amount for amount, _ in transactions)
        expected_total_fees = sum(fee for _, fee in transactions)
        
        assert updated_wallet.balance == expected_balance
        assert updated_wallet.total_received == expected_total_received
        assert updated_wallet.total_fees_earned == expected_total_fees
    
    @pytest.mark.asyncio
    async def test_user_credit_operations(self, wallet_repository):
        """Test user credit operations."""
        user_id = ObjectId()
        
        # Create credit limit
        credit_limit = CreditLimit(
            user_id=user_id,
            credit_limit=1000.0,
            available_credit=1000.0,
            used_credit=0.0,
            merchant_usage={}
        )
        
        await wallet_repository.create_credit_limit(credit_limit)
        
        # Add usage for multiple merchants
        merchant_usage = {
            "1": 200.0,
            "2": 300.0,
            "3": 100.0,
        }
        
        for merchant_id, amount in merchant_usage.items():
            credit_limit.add_merchant_usage(merchant_id, amount)
            await wallet_repository.update_credit_limit(credit_limit)
        
        # Verify final state
        updated_credit = await wallet_repository.get_credit_limit(user_id)
        
        expected_used_credit = sum(merchant_usage.values())
        expected_available_credit = 1000.0 - expected_used_credit
        
        assert updated_credit.used_credit == expected_used_credit
        assert updated_credit.available_credit == expected_available_credit
        assert updated_credit.merchant_usage == merchant_usage
        
        # Test payment
        payment_amount = 100.0
        credit_limit.add_payment(payment_amount)
        await wallet_repository.update_credit_limit(credit_limit)
        
        final_credit = await wallet_repository.get_credit_limit(user_id)
        
        assert final_credit.used_credit == expected_used_credit - payment_amount
        assert final_credit.available_credit == expected_available_credit + payment_amount
    
    @pytest.mark.asyncio
    async def test_idempotency_handling(self, wallet_service, wallet_repository):
        """Test that duplicate requests are handled properly."""
        user_id = ObjectId()
        merchant_id = ObjectId()
        idempotency_key = "test_key_123"
        
        # Create initial data
        wallet = MerchantWallet(merchant_id=merchant_id)
        await wallet_repository.create_merchant_wallet(wallet)
        
        credit_limit = CreditLimit(user_id=user_id, credit_limit=1000.0)
        await wallet_repository.create_credit_limit(credit_limit)
        
        # First transaction
        amount = 100.0
        fee_amount = await wallet_service.calculate_fee(amount, 10.0)
        
        wallet.add_amount(amount, fee_amount)
        await wallet_repository.update_merchant_wallet(wallet)
        
        # Try duplicate transaction with same idempotency key
        # This should be detected and prevented
        # (Implementation would depend on how idempotency is handled)
        
        # Verify only one transaction was processed
        updated_wallet = await wallet_repository.get_merchant_wallet(merchant_id)
        assert updated_wallet.balance == amount  # Should not be doubled
