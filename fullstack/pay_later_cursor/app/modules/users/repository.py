from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from .models import User, UserBalance, UserBank
from app.common.exceptions import UserNotFound, InsufficientBalance
import structlog

logger = structlog.get_logger(__name__)

class UserRepository:
    """Repository for user-related database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.users_collection = database.users
        self.user_balances_collection = database.user_balances
        self.user_bank_collection = database.user_bank

    async def create_user(self, user: User) -> User:
        """Create a new user."""
        user_dict = user.to_dict()
        result = await self.users_collection.insert_one(user_dict)
        user.id = str(result.inserted_id)
        
        # Create user balance record
        user_balance = UserBalance(user_id=user.user_id)
        balance_dict = user_balance.to_dict()
        await self.user_balances_collection.insert_one(balance_dict)
        
        # Create user bank account with default 2000 balance
        user_bank = UserBank(user_id=user.user_id, balance=2000.0)
        bank_dict = user_bank.to_dict()
        await self.user_bank_collection.insert_one(bank_dict)
        
        logger.info("User created successfully", user_id=user.user_id, user_email=user.email)
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by custom user ID."""
        user_data = await self.users_collection.find_one({"user_id": user_id})
        if user_data:
            return User.from_dict(user_data)
        return None

    async def get_user_by_object_id(self, user_id: ObjectId) -> Optional[User]:
        """Get user by MongoDB ObjectId."""
        user_data = await self.users_collection.find_one({"_id": user_id})
        if user_data:
            return User.from_dict(user_data)
        return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_data = await self.users_collection.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None

    async def get_user_balance(self, user_id: int) -> Optional[UserBalance]:
        """Get user balance by user ID."""
        balance_data = await self.user_balances_collection.find_one({"user_id": user_id})
        if balance_data:
            return UserBalance.from_dict(balance_data)
        return None

    async def get_user_bank(self, user_id: int) -> Optional[UserBank]:
        """Get user bank account by user ID."""
        bank_data = await self.user_bank_collection.find_one({"user_id": user_id})
        if bank_data:
            return UserBank.from_dict(bank_data)
        return None

    async def update_user_balance(self, user_id: int, balance: UserBalance) -> bool:
        """Update user balance."""
        balance_dict = balance.to_dict()
        if balance.id:
            del balance_dict["_id"]  # Remove _id for update
        
        result = await self.user_balances_collection.update_one(
            {"user_id": user_id},
            {"$set": balance_dict}
        )
        return result.modified_count > 0

    async def update_user_bank(self, user_id: int, bank: UserBank) -> bool:
        """Update user bank account."""
        bank_dict = bank.to_dict()
        if bank.id:
            del bank_dict["_id"]  # Remove _id for update
        
        result = await self.user_bank_collection.update_one(
            {"user_id": user_id},
            {"$set": bank_dict}
        )
        return result.modified_count > 0

    async def update_user(self, user_id: int, user: User) -> bool:
        """Update user information."""
        user_dict = user.to_dict()
        if user.id:
            del user_dict["_id"]  # Remove _id for update
        
        result = await self.users_collection.update_one(
            {"user_id": user_id},
            {"$set": user_dict}
        )
        return result.modified_count > 0

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        cursor = self.users_collection.find().skip(skip).limit(limit)
        users = []
        async for user_data in cursor:
            users.append(User.from_dict(user_data))
        return users

    async def get_users_at_credit_limit(self) -> List[Dict[str, Any]]:
        """Get users who have reached their credit limit."""
        pipeline = [
            {
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_info"
                }
            },
            {
                "$unwind": "$user_info"
            },
            {
                "$match": {
                    "available_credit": {"$lte": 0}
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "name": "$user_info.name",
                    "email": "$user_info.email",
                    "credit_limit": 1,
                    "outstanding_amount": 1,
                    "available_credit": 1
                }
            }
        ]
        
        cursor = self.user_balances_collection.aggregate(pipeline)
        users = []
        async for user_data in cursor:
            users.append(user_data)
        return users

    async def get_total_outstanding_amount(self) -> float:
        """Get total outstanding amount across all users."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$outstanding_amount"}
                }
            }
        ]
        
        result = await self.user_balances_collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0.0

    async def process_merchant_purchase(self, user_id: int, purchase_amount: float, fee_amount: float) -> bool:
        """Process a merchant purchase - update user balance."""
        user_balance = await self.get_user_balance(user_id)
        if not user_balance:
            raise UserNotFound(f"User balance not found for user_id: {user_id}")
        
        # Check if user has sufficient available credit
        if user_balance.available_credit < purchase_amount:
            raise InsufficientBalance(str(user_id), purchase_amount, user_balance.available_credit)
        
        # Update balance
        user_balance.update_balance(purchase_amount, fee_amount)
        return await self.update_user_balance(user_id, user_balance)

    async def process_repayment(self, user_id: int, repayment_amount: float) -> bool:
        """Process a repayment - update both user balance and user bank."""
        # Get user balance
        user_balance = await self.get_user_balance(user_id)
        if not user_balance:
            raise UserNotFound(f"User balance not found for user_id: {user_id}")
        
        # Get user bank
        user_bank = await self.get_user_bank(user_id)
        if not user_bank:
            raise UserNotFound(f"User bank not found for user_id: {user_id}")
        
        # Check if user has sufficient bank balance
        if not user_bank.has_sufficient_funds(repayment_amount):
            raise InsufficientBalance(str(user_id), repayment_amount, user_bank.balance)
        
        # Check if repayment amount doesn't exceed outstanding amount
        if repayment_amount > user_balance.outstanding_amount:
            raise InsufficientBalance(str(user_id), repayment_amount, user_balance.outstanding_amount)
        
        # Process the repayment
        user_balance.add_payment(repayment_amount)
        user_bank.withdraw(repayment_amount)
        
        # Update both records
        balance_updated = await self.update_user_balance(user_id, user_balance)
        bank_updated = await self.update_user_bank(user_id, user_bank)
        
        return balance_updated and bank_updated

    async def get_user_financial_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive financial summary for a user."""
        user = await self.get_user_by_id(user_id)
        user_balance = await self.get_user_balance(user_id)
        user_bank = await self.get_user_bank(user_id)
        
        if not user or not user_balance or not user_bank:
            raise UserNotFound(f"User or financial data not found for user_id: {user_id}")
        
        return {
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email
            },
            "credit": {
                "credit_limit": user_balance.credit_limit,
                "available_credit": user_balance.available_credit,
                "outstanding_amount": user_balance.outstanding_amount,
                "total_merchant_usage": user_balance.total_merchant_usage,
                "reached_limit": user_balance.reached_limit,
                "utilization_percentage": user_balance.credit_utilization_percentage
            },
            "bank": {
                "balance": user_bank.balance,
                "total_deposited": user_bank.total_deposited,
                "total_withdrawn": user_bank.total_withdrawn,
                "last_transaction": user_bank.last_transaction_at
            }
        }
