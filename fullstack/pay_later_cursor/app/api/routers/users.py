from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.modules.users.service import UserService
from app.modules.users.schemas import (
    UserResponse, UserListResponse, UserDuesResponse, 
    UserBalanceResponse, UserCreditInfoResponse
)
from app.auth.dependencies import get_current_user
from app.db.mongo import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> UserService:
    """Dependency to get user service."""
    from app.modules.users.repository import UserRepository
    user_repository = UserRepository(database)
    return UserService(user_repository)

@router.get("/", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
):
    """Get all users with pagination."""
    users = await user_service.get_all_users(skip=skip, limit=limit)
    return UserListResponse(
        users=[UserResponse.from_user(user) for user in users],
        total=len(users),
        skip=skip,
        limit=limit
    )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """Get user by ID."""
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return UserResponse.from_user(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    name: Optional[str] = None,
    phone: Optional[str] = None,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile."""
    # Check if user is updating their own profile or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    success = await user_service.update_user(user_id, name=name, phone=phone)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    updated_user = await user_service.get_user_by_id(user_id)
    return UserResponse.from_user(updated_user)

@router.get("/{user_id}/balance", response_model=UserBalanceResponse)
async def get_user_balance(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get user balance information."""
    # Check if user is accessing their own balance or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's balance"
        )
    
    user_balance = await user_service.get_user_balance(user_id)
    if not user_balance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Balance not found for user {user_id}"
        )
    
    return UserBalanceResponse.from_user_balance(user_balance)

@router.get("/{user_id}/credit", response_model=UserCreditInfoResponse)
async def get_user_credit_info(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed user credit information."""
    # Check if user is accessing their own credit info or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's credit information"
        )
    
    try:
        credit_info = await user_service.get_user_credit_info(user_id)
        return UserCreditInfoResponse(**credit_info)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{user_id}/financial-summary")
async def get_user_financial_summary(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive financial summary for a user."""
    # Check if user is accessing their own summary or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's financial summary"
        )
    
    try:
        summary = await user_service.get_user_financial_summary(user_id)
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{user_id}/bank-balance")
async def get_user_bank_balance(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get user's bank balance."""
    # Check if user is accessing their own bank balance or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's bank balance"
        )
    
    try:
        balance = await user_service.get_bank_balance(user_id)
        return {
            "user_id": user_id,
            "bank_balance": balance,
            "message": "Bank balance retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/{user_id}/repay")
async def process_repayment(
    user_id: int,
    amount: float,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Process a repayment from user's bank account."""
    # Check if user is making their own repayment or is admin
    # current_user is a UserAuth object, not a dictionary
    if current_user.role not in ["admin", "user"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to make repayment"
        )
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repayment amount must be positive"
        )
    
    try:
        result = await user_service.process_repayment(user_id, amount)
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{user_id}/deposit")
async def deposit_to_bank(
    user_id: int,
    amount: float,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Deposit money to user's bank account."""
    # Check if user is making their own deposit or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to make deposit for this user"
        )
    
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deposit amount must be positive"
        )
    
    try:
        result = await user_service.deposit_to_bank(user_id, amount)
        if result["success"]:
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}/merchant-usage")
async def get_user_merchant_usage(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get user's merchant usage breakdown."""
    # Check if user is accessing their own usage or is admin
    if current_user.get("role") != "admin" and current_user.get("user_id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's merchant usage"
        )
    
    try:
        usage = await user_service.get_user_merchant_usage(user_id)
        return usage
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# Admin-only endpoints
@router.get("/admin/at-credit-limit")
async def get_users_at_credit_limit(
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get users who have reached their credit limit (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    users = await user_service.get_users_at_credit_limit()
    return {
        "users": users,
        "count": len(users),
        "message": "Users at credit limit retrieved successfully"
    }

@router.get("/admin/total-outstanding")
async def get_total_outstanding_amount(
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """Get total outstanding amount across all users (admin only)."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    total = await user_service.get_total_outstanding_amount()
    return {
        "total_outstanding_amount": total,
        "message": "Total outstanding amount retrieved successfully"
    }
