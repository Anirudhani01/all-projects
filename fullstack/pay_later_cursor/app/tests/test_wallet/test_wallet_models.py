"""
Unit tests for wallet models.
"""

import pytest
from datetime import datetime, timezone
from bson import ObjectId

from app.modules.wallet.models import MerchantWallet, CreditLimit


class TestMerchantWallet:
    """Test MerchantWallet model."""
    
    def test_merchant_wallet_creation(self):
        """Test creating a new merchant wallet."""
        merchant_id = ObjectId()
        wallet = MerchantWallet(
            merchant_id=merchant_id,
            balance=100.0,
            total_received=500.0,
            total_fees_earned=50.0
        )
        
        assert wallet.merchant_id == merchant_id
        assert wallet.balance == 100.0
        assert wallet.total_received == 500.0
        assert wallet.total_fees_earned == 50.0
        assert wallet.created_at is not None
        assert wallet.updated_at is not None
    
    def test_merchant_wallet_to_dict(self):
        """Test converting wallet to dictionary."""
        merchant_id = ObjectId()
        wallet = MerchantWallet(
            merchant_id=merchant_id,
            balance=200.0,
            total_received=1000.0,
            total_fees_earned=100.0
        )
        
        wallet_dict = wallet.to_dict()
        
        assert wallet_dict["merchant_id"] == merchant_id
        assert wallet_dict["balance"] == 200.0
        assert wallet_dict["total_received"] == 1000.0
        assert wallet_dict["total_fees_earned"] == 100.0
        assert "_id" in wallet_dict
        assert "created_at" in wallet_dict
        assert "updated_at" in wallet_dict
    
    def test_merchant_wallet_from_dict(self):
        """Test creating wallet from dictionary."""
        merchant_id = ObjectId()
        wallet_id = ObjectId()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        
        wallet_data = {
            "_id": wallet_id,
            "merchant_id": merchant_id,
            "balance": 300.0,
            "total_received": 1500.0,
            "total_fees_earned": 150.0,
            "last_transaction_at": updated_at,
            "created_at": created_at,
            "updated_at": updated_at
        }
        
        wallet = MerchantWallet.from_dict(wallet_data)
        
        assert wallet._id == wallet_id
        assert wallet.merchant_id == merchant_id
        assert wallet.balance == 300.0
        assert wallet.total_received == 1500.0
        assert wallet.total_fees_earned == 150.0
        assert wallet.last_transaction_at == updated_at
        assert wallet.created_at == created_at
        assert wallet.updated_at == updated_at
    
    def test_merchant_wallet_add_amount(self):
        """Test adding amount to wallet."""
        wallet = MerchantWallet(
            merchant_id=ObjectId(),
            balance=100.0,
            total_received=500.0,
            total_fees_earned=50.0
        )
        
        original_balance = wallet.balance
        original_total = wallet.total_received
        original_fees = wallet.total_fees_earned
        
        wallet.add_amount(200.0, 20.0)
        
        assert wallet.balance == original_balance + 200.0
        assert wallet.total_received == original_total + 200.0
        assert wallet.total_fees_earned == original_fees + 20.0
        assert wallet.last_transaction_at is not None
        assert wallet.updated_at > wallet.created_at
    
    def test_merchant_wallet_get_balance(self):
        """Test getting wallet balance."""
        wallet = MerchantWallet(
            merchant_id=ObjectId(),
            balance=250.0
        )
        
        assert wallet.get_balance() == 250.0


class TestCreditLimit:
    """Test CreditLimit model."""
    
    def test_credit_limit_creation(self):
        """Test creating a new credit limit."""
        user_id = ObjectId()
        credit_limit = CreditLimit(
            user_id=user_id,
            credit_limit=1000.0,
            available_credit=800.0,
            used_credit=200.0,
            merchant_usage={"1": 100.0, "2": 100.0}
        )
        
        assert credit_limit.user_id == user_id
        assert credit_limit.credit_limit == 1000.0
        assert credit_limit.available_credit == 800.0
        assert credit_limit.used_credit == 200.0
        assert credit_limit.merchant_usage == {"1": 100.0, "2": 100.0}
        assert credit_limit.created_at is not None
        assert credit_limit.updated_at is not None
    
    def test_credit_limit_to_dict(self):
        """Test converting credit limit to dictionary."""
        user_id = ObjectId()
        credit_limit = CreditLimit(
            user_id=user_id,
            credit_limit=2000.0,
            available_credit=1500.0,
            used_credit=500.0,
            merchant_usage={"1": 300.0, "2": 200.0}
        )
        
        credit_dict = credit_limit.to_dict()
        
        assert credit_dict["user_id"] == user_id
        assert credit_dict["credit_limit"] == 2000.0
        assert credit_dict["available_credit"] == 1500.0
        assert credit_dict["used_credit"] == 500.0
        assert credit_dict["merchant_usage"] == {"1": 300.0, "2": 200.0}
        assert "_id" in credit_dict
        assert "created_at" in credit_dict
        assert "updated_at" in credit_dict
    
    def test_credit_limit_from_dict(self):
        """Test creating credit limit from dictionary."""
        user_id = ObjectId()
        credit_id = ObjectId()
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        
        credit_data = {
            "_id": credit_id,
            "user_id": user_id,
            "credit_limit": 3000.0,
            "available_credit": 2000.0,
            "used_credit": 1000.0,
            "merchant_usage": {"1": 500.0, "2": 500.0},
            "created_at": created_at,
            "updated_at": updated_at
        }
        
        credit_limit = CreditLimit.from_dict(credit_data)
        
        assert credit_limit._id == credit_id
        assert credit_limit.user_id == user_id
        assert credit_limit.credit_limit == 3000.0
        assert credit_limit.available_credit == 2000.0
        assert credit_limit.used_credit == 1000.0
        assert credit_limit.merchant_usage == {"1": 500.0, "2": 500.0}
        assert credit_limit.created_at == created_at
        assert credit_limit.updated_at == updated_at
    
    def test_credit_limit_set_credit_limit(self):
        """Test setting credit limit."""
        credit_limit = CreditLimit(
            user_id=ObjectId(),
            credit_limit=1000.0,
            available_credit=800.0,
            used_credit=200.0
        )
        
        credit_limit.set_credit_limit(2000.0)
        
        assert credit_limit.credit_limit == 2000.0
        assert credit_limit.available_credit == 1800.0  # 2000 - 200
        assert credit_limit.updated_at > credit_limit.created_at
    
    def test_credit_limit_add_merchant_usage(self):
        """Test adding merchant usage."""
        credit_limit = CreditLimit(
            user_id=ObjectId(),
            credit_limit=1000.0,
            available_credit=800.0,
            used_credit=200.0,
            merchant_usage={"1": 200.0}
        )
        
        credit_limit.add_merchant_usage("2", 100.0)
        
        assert credit_limit.merchant_usage["2"] == 100.0
        assert credit_limit.used_credit == 300.0
        assert credit_limit.available_credit == 700.0  # 1000 - 300
        assert credit_limit.updated_at > credit_limit.created_at
    
    def test_credit_limit_add_payment(self):
        """Test adding payment."""
        credit_limit = CreditLimit(
            user_id=ObjectId(),
            credit_limit=1000.0,
            available_credit=600.0,
            used_credit=400.0
        )
        
        credit_limit.add_payment(100.0)
        
        assert credit_limit.used_credit == 300.0
        assert credit_limit.available_credit == 700.0  # 1000 - 300
        assert credit_limit.updated_at > credit_limit.created_at
    
    def test_credit_limit_get_merchant_usage(self):
        """Test getting merchant usage."""
        credit_limit = CreditLimit(
            user_id=ObjectId(),
            merchant_usage={"1": 200.0, "2": 300.0}
        )
        
        assert credit_limit.get_merchant_usage("1") == 200.0
        assert credit_limit.get_merchant_usage("2") == 300.0
        assert credit_limit.get_merchant_usage("3") == 0.0  # Non-existent merchant
    
    def test_credit_limit_has_sufficient_credit(self):
        """Test checking if user has sufficient credit."""
        credit_limit = CreditLimit(
            user_id=ObjectId(),
            credit_limit=1000.0,
            available_credit=500.0,
            used_credit=500.0
        )
        
        assert credit_limit.has_sufficient_credit(400.0) is True
        assert credit_limit.has_sufficient_credit(500.0) is True
        assert credit_limit.has_sufficient_credit(600.0) is False
