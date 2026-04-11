from typing import Optional, Dict, Any, List
from bson import ObjectId
from datetime import datetime
import structlog
from app.modules.wallet.repository import WalletRepository
from app.modules.wallet.models import MerchantWallet, CreditLimit
from app.common.types import TransactionType, TransactionStatus, Currency

logger = structlog.get_logger(__name__)


class WalletService:
    """Service for wallet-related business logic."""
    
    def __init__(self, wallet_repository: WalletRepository):
        self.wallet_repo = wallet_repository
    
    async def calculate_fee(self, amount: float, merchant_fee_pct: float) -> float:
        """Calculate fee amount based on merchant fee percentage."""
        try:
            fee_amount = (amount * merchant_fee_pct) / 100
            return round(fee_amount, 2)
        except Exception as e:
            logger.error("Failed to calculate fee", 
                        amount=amount,
                        merchant_fee_pct=merchant_fee_pct,
                        error=str(e))
            raise
    
    async def calculate_total_amount(self, amount: float, fee_amount: float) -> float:
        """Calculate total amount (base amount + fee)."""
        try:
            total_amount = amount + fee_amount
            return round(total_amount, 2)
        except Exception as e:
            logger.error("Failed to calculate total amount", 
                        amount=amount,
                        fee_amount=fee_amount,
                        error=str(e))
            raise
    
    async def get_user_credit_info(self, user_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get user's credit information."""
        try:
            credit_info = await self.wallet_repo.get_user_credit_info(user_id)
            if credit_info:
                logger.info("Retrieved user credit info", 
                           user_id=str(user_id),
                           credit_limit=credit_info["credit_limit"],
                           available_credit=credit_info["available_credit"])
            return credit_info
        except Exception as e:
            logger.error("Failed to get user credit info", 
                        user_id=str(user_id),
                        error=str(e))
            raise
    
    async def get_merchant_wallet_balance(self, merchant_id: ObjectId) -> float:
        """Get merchant's wallet balance."""
        try:
            balance = await self.wallet_repo.get_merchant_wallet_balance(merchant_id)
            logger.info("Retrieved merchant wallet balance", 
                       merchant_id=str(merchant_id),
                       balance=balance)
            return balance
        except Exception as e:
            logger.error("Failed to get merchant wallet balance", 
                        merchant_id=str(merchant_id),
                        error=str(e))
            raise
    
    async def check_user_credit_sufficiency(self, user_id: ObjectId, amount: float) -> bool:
        """Check if user has sufficient credit for the amount."""
        try:
            credit_info = await self.get_user_credit_info(user_id)
            if not credit_info:
                logger.warning("No credit info found for user", user_id=str(user_id))
                return False
            
            available_credit = credit_info["available_credit"]
            has_sufficient = available_credit >= amount
            
            logger.info("Credit sufficiency check", 
                       user_id=str(user_id),
                       required_amount=amount,
                       available_credit=available_credit,
                       has_sufficient=has_sufficient)
            
            return has_sufficient
        except Exception as e:
            logger.error("Failed to check credit sufficiency", 
                        user_id=str(user_id),
                        amount=amount,
                        error=str(e))
            raise
    
    async def add_to_merchant_wallet(self, user_id: ObjectId, merchant_id: ObjectId, 
                                   amount: float, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Add money to merchant wallet from user's credit."""
        try:
            logger.info("Starting wallet add operation", 
                       user_id=str(user_id),
                       merchant_id=str(merchant_id),
                       amount=amount)
            
            # Get merchant information
            merchant = await self.wallet_repo.get_merchant_by_id(merchant_id)
            if not merchant:
                raise ValueError(f"Merchant not found: {merchant_id}")
            
            # Calculate fee and total amount
            fee_pct = merchant.get("current_fee_pct", 0.0)
            fee_amount = await self.calculate_fee(amount, fee_pct)
            total_amount = await self.calculate_total_amount(amount, fee_amount)
            
            # Check credit sufficiency
            if not await self.check_user_credit_sufficiency(user_id, total_amount):
                raise ValueError(f"Insufficient credit. Required: {total_amount}")
            
            # Get current balances
            user_credit_before = await self.get_user_credit_info(user_id)
            merchant_balance_before = await self.get_merchant_wallet_balance(merchant_id)
            
            # Update merchant wallet balance
            await self.wallet_repo.update_merchant_wallet_balance(merchant_id, amount)
            
            # Update user credit usage
            await self.wallet_repo.update_user_credit_usage(user_id, total_amount)
            
            # Get updated balances
            user_credit_after = await self.get_user_credit_info(user_id)
            merchant_balance_after = await self.get_merchant_wallet_balance(merchant_id)
            
            # Create transaction record
            transaction_data = {
                "transaction_id": f"WALLET_{ObjectId()}",
                "type": TransactionType.WALLET_ADD,
                "user_id": user_id,
                "merchant_id": merchant_id,
                "amount": amount,
                "fee_amount": fee_amount,
                "total_amount": total_amount,
                "currency": Currency.INR,
                "status": TransactionStatus.APPROVED,
                "applied_fee_pct": fee_pct,
                "merchant_wallet_balance_before": merchant_balance_before,
                "merchant_wallet_balance_after": merchant_balance_after,
                "user_credit_before": user_credit_before["available_credit"] if user_credit_before else 0.0,
                "user_credit_after": user_credit_after["available_credit"] if user_credit_after else 0.0,
                "idempotency_key": idempotency_key,
                "reason": f"Wallet add to {merchant.get('name', 'Unknown')}",
                "created_at": datetime.utcnow()
            }
            
            transaction_id = await self.wallet_repo.create_wallet_transaction(transaction_data)
            
            result = {
                "transaction_id": transaction_id,
                "amount": amount,
                "fee_amount": fee_amount,
                "total_amount": total_amount,
                "merchant_name": merchant.get("name"),
                "merchant_balance_before": merchant_balance_before,
                "merchant_balance_after": merchant_balance_after,
                "user_credit_before": user_credit_before["available_credit"] if user_credit_before else 0.0,
                "user_credit_after": user_credit_after["available_credit"] if user_credit_after else 0.0
            }
            
            logger.info("Successfully added to merchant wallet", 
                       user_id=str(user_id),
                       merchant_id=str(merchant_id),
                       amount=amount,
                       transaction_id=transaction_id)
            
            return result
            
        except Exception as e:
            logger.error("Failed to add to merchant wallet", 
                        user_id=str(user_id),
                        merchant_id=str(merchant_id),
                        amount=amount,
                        error=str(e))
            raise
    
    async def process_wallet_payment(self, user_id: ObjectId, amount: float, 
                                   idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Process payment from user to PayLater."""
        try:
            logger.info("Starting wallet payment processing", 
                       user_id=str(user_id),
                       amount=amount)
            
            # Get current user credit info
            user_credit_before = await self.get_user_credit_info(user_id)
            if not user_credit_before:
                raise ValueError(f"User credit info not found: {user_id}")
            
            outstanding_amount = user_credit_before["outstanding_amount"]
            if outstanding_amount < amount:
                raise ValueError(f"Payment amount ({amount}) exceeds outstanding amount ({outstanding_amount})")
            
            # Update user balance (reduce outstanding amount)
            await self.wallet_repo.update_user_credit_usage(user_id, -amount)
            
            # Get updated credit info
            user_credit_after = await self.get_user_credit_info(user_id)
            
            # Create transaction record
            transaction_data = {
                "transaction_id": f"WALLET_{ObjectId()}",
                "type": TransactionType.WALLET_PAYMENT,
                "user_id": user_id,
                "amount": amount,
                "fee_amount": 0.0,
                "total_amount": amount,
                "currency": Currency.INR,
                "status": TransactionStatus.APPROVED,
                "user_credit_before": user_credit_before["outstanding_amount"],
                "user_credit_after": user_credit_after["outstanding_amount"],
                "idempotency_key": idempotency_key,
                "reason": "Payment to PayLater",
                "created_at": datetime.utcnow()
            }
            
            transaction_id = await self.wallet_repo.create_wallet_transaction(transaction_data)
            
            result = {
                "transaction_id": transaction_id,
                "amount": amount,
                "outstanding_before": user_credit_before["outstanding_amount"],
                "outstanding_after": user_credit_after["outstanding_amount"],
                "available_credit_before": user_credit_before["available_credit"],
                "available_credit_after": user_credit_after["available_credit"]
            }
            
            logger.info("Successfully processed wallet payment", 
                       user_id=str(user_id),
                       amount=amount,
                       transaction_id=transaction_id)
            
            return result
            
        except Exception as e:
            logger.error("Failed to process wallet payment", 
                        user_id=str(user_id),
                        amount=amount,
                        error=str(e))
            raise
    
    async def get_wallet_transactions(self, user_id: Optional[ObjectId] = None, 
                                    merchant_id: Optional[ObjectId] = None,
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get wallet transactions with optional filters."""
        try:
            transactions = await self.wallet_repo.get_wallet_transactions(
                user_id=user_id,
                merchant_id=merchant_id,
                limit=limit
            )
            
            logger.info("Retrieved wallet transactions", 
                       user_id=str(user_id) if user_id else None,
                       merchant_id=str(merchant_id) if merchant_id else None,
                       count=len(transactions))
            
            return transactions
            
        except Exception as e:
            logger.error("Failed to get wallet transactions", 
                        user_id=str(user_id) if user_id else None,
                        merchant_id=str(merchant_id) if merchant_id else None,
                        error=str(e))
            raise
    
    async def get_user_merchant_usage(self, user_id: ObjectId) -> Dict[str, Any]:
        """Get user's usage across all merchants."""
        try:
            # Get user's credit info
            credit_info = await self.get_user_credit_info(user_id)
            if not credit_info:
                return {"total_usage": 0.0, "merchant_breakdown": {}}
            
            # Get wallet transactions for the user
            transactions = await self.get_wallet_transactions(user_id=user_id, limit=1000)
            
            # Calculate merchant usage breakdown
            merchant_usage = {}
            total_usage = 0.0
            
            for transaction in transactions:
                if transaction["type"] == "wallet_add":
                    merchant_id = str(transaction["merchant_id"])
                    amount = transaction["total_amount"]
                    
                    if merchant_id not in merchant_usage:
                        merchant_usage[merchant_id] = 0.0
                    
                    merchant_usage[merchant_id] += amount
                    total_usage += amount
            
            result = {
                "total_usage": total_usage,
                "merchant_breakdown": merchant_usage,
                "credit_limit": credit_info["credit_limit"],
                "available_credit": credit_info["available_credit"],
                "outstanding_amount": credit_info["outstanding_amount"]
            }
            
            logger.info("Retrieved user merchant usage", 
                       user_id=str(user_id),
                       total_usage=total_usage,
                       merchant_count=len(merchant_usage))
            
            return result
            
        except Exception as e:
            logger.error("Failed to get user merchant usage", 
                        user_id=str(user_id),
                        error=str(e))
            raise
    
    async def get_merchant_wallet_summary(self, merchant_id: ObjectId) -> Dict[str, Any]:
        """Get merchant wallet summary."""
        try:
            # Get merchant info
            merchant = await self.wallet_repo.get_merchant_by_id(merchant_id)
            if not merchant:
                raise ValueError(f"Merchant not found: {merchant_id}")
            
            # Get wallet transactions for the merchant
            transactions = await self.get_wallet_transactions(merchant_id=merchant_id, limit=1000)
            
            # Calculate summary
            total_received = 0.0
            total_fees = 0.0
            transaction_count = 0
            
            for transaction in transactions:
                if transaction["type"] == "wallet_add":
                    total_received += transaction["amount"]
                    total_fees += transaction["fee_amount"]
                    transaction_count += 1
            
            result = {
                "merchant_id": str(merchant_id),
                "merchant_name": merchant.get("name"),
                "current_balance": merchant.get("wallet_balance", 0.0),
                "total_received": total_received,
                "total_fees": total_fees,
                "transaction_count": transaction_count,
                "fee_percentage": merchant.get("current_fee_pct", 0.0)
            }
            
            logger.info("Retrieved merchant wallet summary", 
                       merchant_id=str(merchant_id),
                       current_balance=result["current_balance"],
                       total_received=total_received)
            
            return result
            
        except Exception as e:
            logger.error("Failed to get merchant wallet summary", 
                        merchant_id=str(merchant_id),
                        error=str(e))
            raise
