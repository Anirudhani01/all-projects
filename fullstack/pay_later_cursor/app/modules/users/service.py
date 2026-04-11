from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from .repository import UserRepository
from .models import User, UserBalance, UserBank
from app.common.exceptions import UserNotFound, InsufficientBalance, DuplicateEntity
from app.common.counters import CounterService, USER_ID_COUNTER
import structlog

logger = structlog.get_logger(__name__)

class UserService:
    """Service for user-related business logic."""

    def __init__(self, user_repository: UserRepository):
        self.repository = user_repository
        self.counter_service = CounterService(user_repository.database)

    async def create_user(self, name: str, email: str, phone: Optional[str] = None) -> User:
        """Create a new user with bank account and balance."""
        # Check if user already exists
        existing_user = await self.repository.get_user_by_email(email)
        if existing_user:
            raise DuplicateEntity("User", "email", email)
        
        # Generate auto-increment user ID
        user_id = await self.counter_service.get_next_id(USER_ID_COUNTER)
        
        # Create user
        user = User(
            user_id=user_id,
            name=name,
            email=email,
            phone=phone
        )
        
        # This will create user, user balance, and user bank account
        created_user = await self.repository.create_user(user)
        
        logger.info("User created with bank account", 
                   user_id=user_id, 
                   email=email, 
                   bank_balance=2000.0)
        
        return created_user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return await self.repository.get_user_by_email(email)

    async def update_user(self, user_id: int, name: Optional[str] = None, 
                         phone: Optional[str] = None) -> bool:
        """Update user information."""
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFound(f"User not found with ID: {user_id}")
        
        if name:
            user.name = name
        if phone:
            user.phone = phone
        
        return await self.repository.update_user(user_id, user)

    async def get_user_balance(self, user_id: int) -> Optional[UserBalance]:
        """Get user balance."""
        return await self.repository.get_user_balance(user_id)

    async def get_user_bank(self, user_id: int) -> Optional[UserBank]:
        """Get user bank account."""
        return await self.repository.get_user_bank(user_id)

    async def get_user_credit_info(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive user credit information."""
        user_balance = await self.repository.get_user_balance(user_id)
        if not user_balance:
            raise UserNotFound(f"User balance not found for user_id: {user_id}")
        
        return {
            "user_id": user_id,
            "credit_limit": user_balance.credit_limit,
            "available_credit": user_balance.available_credit,
            "outstanding_amount": user_balance.outstanding_amount,
            "total_merchant_usage": user_balance.total_merchant_usage,
            "total_purchases": user_balance.total_purchases,
            "total_payments": user_balance.total_payments,
            "reached_limit": user_balance.reached_limit,
            "utilization_percentage": user_balance.credit_utilization_percentage
        }

    async def update_user_credit_for_wallet(self, user_id: int, 
                                          purchase_amount: float, 
                                          fee_amount: float) -> bool:
        """Update user credit when adding money to merchant wallet."""
        return await self.repository.process_merchant_purchase(user_id, purchase_amount, fee_amount)

    async def check_user_credit_sufficiency(self, user_id: int, amount: float) -> bool:
        """Check if user has sufficient available credit."""
        user_balance = await self.repository.get_user_balance(user_id)
        if not user_balance:
            return False
        return user_balance.available_credit >= amount

    async def process_repayment(self, user_id: int, repayment_amount: float) -> Dict[str, Any]:
        """Process a repayment from user's bank account."""
        success = await self.repository.process_repayment(user_id, repayment_amount)
        
        if success:
            # Get updated financial data
            financial_summary = await self.repository.get_user_financial_summary(user_id)
            
            logger.info("Repayment processed successfully", 
                       user_id=user_id, 
                       repayment_amount=repayment_amount,
                       new_outstanding=financial_summary["credit"]["outstanding_amount"],
                       new_bank_balance=financial_summary["bank"]["balance"])
            
            return {
                "success": True,
                "message": "Repayment processed successfully",
                "repayment_amount": repayment_amount,
                "new_outstanding_amount": financial_summary["credit"]["outstanding_amount"],
                "new_bank_balance": financial_summary["bank"]["balance"]
            }
        else:
            return {
                "success": False,
                "message": "Failed to process repayment"
            }

    async def get_user_financial_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive financial summary for a user."""
        return await self.repository.get_user_financial_summary(user_id)

    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return await self.repository.get_all_users(skip, limit)

    async def get_users_at_credit_limit(self) -> List[Dict[str, Any]]:
        """Get users who have reached their credit limit."""
        return await self.repository.get_users_at_credit_limit()

    async def get_total_outstanding_amount(self) -> float:
        """Get total outstanding amount across all users."""
        return await self.repository.get_total_outstanding_amount()

    async def get_user_merchant_usage(self, user_id: int) -> Dict[str, Any]:
        """Get user's merchant usage breakdown."""
        user_balance = await self.repository.get_user_balance(user_id)
        if not user_balance:
            raise UserNotFound(f"User balance not found for user_id: {user_id}")
        
        return {
            "user_id": user_id,
            "total_merchant_usage": user_balance.total_merchant_usage,
            "total_purchases": user_balance.total_purchases,
            "total_payments": user_balance.total_payments,
            "outstanding_amount": user_balance.outstanding_amount,
            "available_credit": user_balance.available_credit
        }

    async def deposit_to_bank(self, user_id: int, amount: float) -> Dict[str, Any]:
        """Deposit money to user's bank account."""
        user_bank = await self.repository.get_user_bank(user_id)
        if not user_bank:
            raise UserNotFound(f"User bank not found for user_id: {user_id}")
        
        user_bank.add_deposit(amount)
        success = await self.repository.update_user_bank(user_id, user_bank)
        
        if success:
            logger.info("Deposit processed successfully", 
            user_id=user_id,
                       amount=amount,
                       new_balance=user_bank.balance)
            
            return {
                "success": True,
                "message": "Deposit processed successfully",
                "deposit_amount": amount,
                "new_balance": user_bank.balance
            }
        else:
            return {
                "success": False,
                "message": "Failed to process deposit"
            }

    async def get_bank_balance(self, user_id: int) -> float:
        """Get user's bank balance."""
        user_bank = await self.repository.get_user_bank(user_id)
        if not user_bank:
            raise UserNotFound(f"User bank not found for user_id: {user_id}")
        return user_bank.get_balance()

    async def check_bank_sufficiency(self, user_id: int, amount: float) -> bool:
        """Check if user has sufficient bank balance."""
        user_bank = await self.repository.get_user_bank(user_id)
        if not user_bank:
            return False
        return user_bank.has_sufficient_funds(amount)

    async def check_user_status(self, user_id: ObjectId) -> User:
        """Check if user exists and return user object."""
        user = await self.repository.get_user_by_object_id(user_id)
        if not user:
            raise UserNotFound(f"User not found with ObjectId: {user_id}")
        return user

    async def check_user_status_by_custom_id(self, custom_user_id: int) -> User:
        """Check if user exists by custom ID and return user object."""
        user = await self.get_user_by_id(custom_user_id)
        if not user:
            raise UserNotFound(f"User not found with custom ID: {custom_user_id}")
        return user
