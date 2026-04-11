"""
Dependencies for API endpoints.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from bson import ObjectId

from ..core.database import get_database, Database
from ..core.security import security_utils
from ..core.exceptions import AuthenticationException, AuthorizationException
from ..models.user import User

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    database: Database = Depends(get_database)
) -> User:
    """Get current authenticated user."""
    try:
        # Verify token
        payload = security_utils.verify_token(credentials.credentials)
        if not payload:
            raise AuthenticationException("Invalid token")
        
        # Check token type
        token_type = payload.get("type")
        if token_type != "access":
            raise AuthenticationException("Invalid token type")
        
        # Get user ID
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        
        # Get user from database
        user_collection = database.get_collection("users")
        user_data = await user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_data:
            raise AuthenticationException("User not found")
        
        # Create user object
        user = User(**user_data)
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("User account is deactivated")
        
        return user
        
    except AuthenticationException:
        raise
    except Exception as e:
        raise AuthenticationException(f"Authentication failed: {str(e)}")


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthenticationException("User account is deactivated")
    return current_user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user with admin role."""
    if current_user.role != "admin":
        raise AuthorizationException("Admin access required")
    return current_user


async def get_merchant_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user with merchant role."""
    if current_user.role not in ["merchant", "admin"]:
        raise AuthorizationException("Merchant access required")
    return current_user


def get_user_by_id(user_id: str) -> str:
    """Validate and return user ID."""
    try:
        ObjectId(user_id)
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )


def get_merchant_by_id(merchant_id: str) -> str:
    """Validate and return merchant ID."""
    try:
        ObjectId(merchant_id)
        return merchant_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid merchant ID format"
        )


def get_transaction_by_id(transaction_id: str) -> str:
    """Validate and return transaction ID."""
    try:
        ObjectId(transaction_id)
        return transaction_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction ID format"
        )
