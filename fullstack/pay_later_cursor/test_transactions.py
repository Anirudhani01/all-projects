#!/usr/bin/env python3
"""
Simple test script to verify the transaction module implementation.
This script tests the basic structure and imports without requiring a running MongoDB instance.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that all transaction module components can be imported."""
    try:
        print("Testing imports...")
        
        # Test models
        from app.modules.transactions.models import Transaction, IdempotencyKey
        print("✓ Transaction models imported successfully")
        
        # Test schemas
        from app.modules.transactions.schemas import (
            PurchaseRequest, PaymentRequest, TransactionResponse,
            PurchaseResponse, PaymentResponse, TransactionListResponse,
            TransactionFilter, TransactionSummary
        )
        print("✓ Transaction schemas imported successfully")
        
        # Test repository
        from app.modules.transactions.repository import TransactionRepository
        print("✓ Transaction repository imported successfully")
        
        # Test service
        from app.modules.transactions.service import TransactionService
        print("✓ Transaction service imported successfully")
        
        # Test types
        from app.common.types import TransactionType, TransactionStatus, Currency
        print("✓ Transaction types imported successfully")
        
        # Test exceptions
        from app.common.exceptions import (
            UserNotFound, MerchantNotFound, CreditLimitExceeded,
            InsufficientBalance, DuplicateRequest
        )
        print("✓ Transaction exceptions imported successfully")
        
        # Test validators
        from app.common.validators import validate_amount, calculate_fee_amount, calculate_merchant_payout
        print("✓ Transaction validators imported successfully")
        
        print("\n🎉 All transaction module components imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_schema_validation():
    """Test basic schema validation."""
    try:
        print("\nTesting schema validation...")
        
        from app.modules.transactions.schemas import PurchaseRequest, PaymentRequest
        from app.common.types import Currency
        
        # Test purchase request validation
        purchase_data = {
            "user_id": "507f1f77bcf86cd799439011",
            "merchant_id": "507f1f77bcf86cd799439012",
            "amount": 100.50,
            "currency": Currency.INR,
            "idempotency_key": "test-key-123"
        }
        
        purchase_request = PurchaseRequest(**purchase_data)
        print("✓ Purchase request validation successful")
        
        # Test payment request validation
        payment_data = {
            "user_id": "507f1f77bcf86cd799439011",
            "amount": 50.25,
            "currency": Currency.INR
        }
        
        payment_request = PaymentRequest(**payment_data)
        print("✓ Payment request validation successful")
        
        print("🎉 Schema validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        return False

def test_model_creation():
    """Test model creation and serialization."""
    try:
        print("\nTesting model creation...")
        
        from app.modules.transactions.models import Transaction, IdempotencyKey
        from app.common.types import TransactionType, TransactionStatus, Currency
        from bson import ObjectId
        
        # Test transaction model
        transaction = Transaction(
            type=TransactionType.PURCHASE,
            user_id=ObjectId(),
            amount=100.0,
            currency=Currency.INR,
            status=TransactionStatus.APPROVED
        )
        
        # Test serialization
        transaction_dict = transaction.to_dict()
        print("✓ Transaction model creation and serialization successful")
        
        # Test idempotency key model
        idempotency_key = IdempotencyKey(
            scope="user:123",
            key="test-key"
        )
        
        key_dict = idempotency_key.to_dict()
        print("✓ Idempotency key model creation and serialization successful")
        
        print("🎉 Model creation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Model creation error: {e}")
        return False

def test_validator_functions():
    """Test validator functions."""
    try:
        print("\nTesting validator functions...")
        
        from app.common.validators import validate_amount, calculate_fee_amount, calculate_merchant_payout
        
        # Test amount validation
        amount = validate_amount(100.0, "test_amount")
        print("✓ Amount validation successful")
        
        # Test fee calculation
        fee = calculate_fee_amount(100.0, 2.5)  # 2.5% fee
        print(f"✓ Fee calculation successful: {fee}")
        
        # Test merchant payout calculation
        payout = calculate_merchant_payout(100.0, fee)
        print(f"✓ Merchant payout calculation successful: {payout}")
        
        print("🎉 Validator function tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Validator function error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Transaction Module Implementation")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_schema_validation,
        test_model_creation,
        test_validator_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Transaction module is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
