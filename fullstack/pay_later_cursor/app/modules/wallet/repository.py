from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
import structlog
from app.modules.wallet.models import MerchantWallet, CreditLimit

logger = structlog.get_logger(__name__)


class WalletRepository:
    """Repository for wallet-related database operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.merchant_wallets = database.merchant_wallets
        self.credit_limits = database.credit_limits
        self.merchants = database.merchants
        self.user_balances = database.user_balances
        self.transactions = database.transactions
    
    # Merchant Wallet Operations
    async def create_merchant_wallet(self, wallet: MerchantWallet) -> str:
        """Create a new merchant wallet."""
        try:
            wallet_dict = wallet.to_dict()
            result = await self.merchant_wallets.insert_one(wallet_dict)
            logger.info("Created merchant wallet", 
                       merchant_id=str(wallet.merchant_id),
                       wallet_id=str(result.inserted_id))
            return str(result.inserted_id)
        except Exception as e:
            logger.error("Failed to create merchant wallet", 
                        merchant_id=str(wallet.merchant_id),
                        error=str(e))
            raise
    
    async def get_merchant_wallet(self, merchant_id: ObjectId) -> Optional[MerchantWallet]:
        """Get merchant wallet by merchant ID."""
        try:
            doc = await self.merchant_wallets.find_one({"merchant_id": merchant_id})
            if doc:
                return MerchantWallet.from_dict(doc)
            return None
        except Exception as e:
            logger.error("Failed to get merchant wallet", 
                        merchant_id=str(merchant_id),
                        error=str(e))
            raise
    
    async def update_merchant_wallet(self, merchant_id: ObjectId, update_data: Dict[str, Any]) -> bool:
        """Update merchant wallet."""
        try:
            result = await self.merchant_wallets.update_one(
                {"merchant_id": merchant_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                logger.info("Updated merchant wallet", 
                           merchant_id=str(merchant_id),
                           modified_count=result.modified_count)
                return True
            return False
        except Exception as e:
            logger.error("Failed to update merchant wallet", 
                        merchant_id=str(merchant_id),
                        error=str(e))
            raise
    
    async def get_all_merchant_wallets(self) -> List[MerchantWallet]:
        """Get all merchant wallets."""
        try:
            cursor = self.merchant_wallets.find({})
            wallets = []
            async for doc in cursor:
                wallets.append(MerchantWallet.from_dict(doc))
            return wallets
        except Exception as e:
            logger.error("Failed to get all merchant wallets", error=str(e))
            raise
    
    # Credit Limit Operations
    async def create_credit_limit(self, credit_limit: CreditLimit) -> str:
        """Create a new credit limit record."""
        try:
            credit_dict = credit_limit.to_dict()
            result = await self.credit_limits.insert_one(credit_dict)
            logger.info("Created credit limit", 
                       user_id=str(credit_limit.user_id),
                       credit_id=str(result.inserted_id))
            return str(result.inserted_id)
        except Exception as e:
            logger.error("Failed to create credit limit", 
                        user_id=str(credit_limit.user_id),
                        error=str(e))
            raise
    
    async def get_credit_limit(self, user_id: ObjectId) -> Optional[CreditLimit]:
        """Get credit limit by user ID."""
        try:
            doc = await self.credit_limits.find_one({"user_id": user_id})
            if doc:
                return CreditLimit.from_dict(doc)
            return None
        except Exception as e:
            logger.error("Failed to get credit limit", 
                        user_id=str(user_id),
                        error=str(e))
            raise
    
    async def update_credit_limit(self, user_id: ObjectId, update_data: Dict[str, Any]) -> bool:
        """Update credit limit."""
        try:
            result = await self.credit_limits.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                logger.info("Updated credit limit", 
                           user_id=str(user_id),
                           modified_count=result.modified_count)
                return True
            return False
        except Exception as e:
            logger.error("Failed to update credit limit", 
                        user_id=str(user_id),
                        error=str(e))
            raise
    
    async def get_all_credit_limits(self) -> List[CreditLimit]:
        """Get all credit limits."""
        try:
            cursor = self.credit_limits.find({})
            credit_limits = []
            async for doc in cursor:
                credit_limits.append(CreditLimit.from_dict(doc))
            return credit_limits
        except Exception as e:
            logger.error("Failed to get all credit limits", error=str(e))
            raise
    
    # Enhanced Merchant Operations
    async def update_merchant_wallet_balance(self, merchant_id: ObjectId, amount: float) -> bool:
        """Update merchant's wallet balance in merchants collection."""
        try:
            result = await self.merchants.update_one(
                {"_id": merchant_id},
                {
                    "$inc": {
                        "wallet_balance": amount,
                        "total_received": amount
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            if result.modified_count > 0:
                logger.info("Updated merchant wallet balance", 
                           merchant_id=str(merchant_id),
                           amount=amount)
                return True
            return False
        except Exception as e:
            logger.error("Failed to update merchant wallet balance", 
                        merchant_id=str(merchant_id),
                        amount=amount,
                        error=str(e))
            raise
    
    async def get_merchant_wallet_balance(self, merchant_id: ObjectId) -> float:
        """Get merchant's wallet balance from merchants collection."""
        try:
            doc = await self.merchants.find_one({"_id": merchant_id})
            if doc:
                return doc.get("wallet_balance", 0.0)
            return 0.0
        except Exception as e:
            logger.error("Failed to get merchant wallet balance", 
                        merchant_id=str(merchant_id),
                        error=str(e))
            raise
    
    # Enhanced User Balance Operations
    async def update_user_credit_usage(self, user_id: ObjectId, amount: float) -> bool:
        """Update user's credit usage in user_balances collection."""
        try:
            # First get current user balance to calculate new available credit
            current_balance = await self.user_balances.find_one({"user_id": user_id})
            if not current_balance:
                logger.error("User balance not found", user_id=str(user_id))
                return False
            
            current_outstanding = current_balance.get("outstanding_amount", 0.0)
            credit_limit = current_balance.get("credit_limit", 2000.0)
            new_outstanding = current_outstanding + amount
            new_available_credit = credit_limit - new_outstanding
            
            result = await self.user_balances.update_one(
                {"user_id": user_id},
                {
                    "$inc": {
                        "outstanding_amount": amount,
                        "total_merchant_usage": amount
                    },
                    "$set": {
                        "available_credit": new_available_credit,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            if result.modified_count > 0:
                logger.info("Updated user credit usage", 
                           user_id=str(user_id),
                           amount=amount,
                           new_outstanding=new_outstanding,
                           new_available_credit=new_available_credit)
                return True
            return False
        except Exception as e:
            logger.error("Failed to update user credit usage", 
                        user_id=str(user_id),
                        amount=amount,
                        error=str(e))
            raise
    
    async def get_user_credit_info(self, user_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get user's credit information from user_balances collection."""
        try:
            doc = await self.user_balances.find_one({"user_id": user_id})
            if doc:
                return {
                    "credit_limit": doc.get("credit_limit", 0.0),
                    "outstanding_amount": doc.get("outstanding_amount", 0.0),
                    "available_credit": doc.get("available_credit", 0.0),
                    "total_merchant_usage": doc.get("total_merchant_usage", 0.0)
                }
            return None
        except Exception as e:
            logger.error("Failed to get user credit info", 
                        user_id=str(user_id),
                        error=str(e))
            raise
    
    # Transaction Operations
    async def create_wallet_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Create a wallet transaction."""
        try:
            result = await self.transactions.insert_one(transaction_data)
            logger.info("Created wallet transaction", 
                       transaction_id=str(result.inserted_id))
            return str(result.inserted_id)
        except Exception as e:
            logger.error("Failed to create wallet transaction", error=str(e))
            raise
    
    async def get_wallet_transactions(self, user_id: Optional[ObjectId] = None, 
                                    merchant_id: Optional[ObjectId] = None,
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get wallet transactions with optional filters."""
        try:
            filter_query = {}
            if user_id:
                filter_query["user_id"] = user_id
            if merchant_id:
                filter_query["merchant_id"] = merchant_id
            
            # Add wallet transaction types
            filter_query["type"] = {"$in": ["wallet_add", "wallet_payment"]}
            
            cursor = self.transactions.find(filter_query).sort("created_at", -1).limit(limit)
            transactions = []
            async for doc in cursor:
                transactions.append(doc)
            return transactions
        except Exception as e:
            logger.error("Failed to get wallet transactions", error=str(e))
            raise
    
    # Utility Operations
    async def get_merchant_by_id(self, merchant_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get merchant by ID."""
        try:
            return await self.merchants.find_one({"_id": merchant_id})
        except Exception as e:
            logger.error("Failed to get merchant", 
                        merchant_id=str(merchant_id),
                        error=str(e))
            raise
    
    async def get_user_by_id(self, user_id: ObjectId) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            return await self.user_balances.find_one({"user_id": user_id})
        except Exception as e:
            logger.error("Failed to get user", 
                        user_id=str(user_id),
                        error=str(e))
            raise
