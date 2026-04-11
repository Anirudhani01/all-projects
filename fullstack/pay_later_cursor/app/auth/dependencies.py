"""
Authentication dependencies for LazyPay application.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.service import AuthService
from app.auth.models import UserAuth
from app.auth.jwt_handler import jwt_handler
from app.auth.repository import AuthRepository
from app.api.dependencies import get_database

# Security scheme
security = HTTPBearer(auto_error=False)


def get_auth_repository(
    database = Depends(get_database)
) -> AuthRepository:
    """Get auth repository instance."""
    return AuthRepository(database)


def get_auth_service(
    auth_repository: AuthRepository = Depends(get_auth_repository)
) -> AuthService:
    """Get auth service instance."""
    return AuthService(auth_repository)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserAuth:
    """Get current authenticated user from JWT token."""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        # Validate token and get user
        user = await auth_service.validate_token(credentials.credentials)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(
    current_user: UserAuth = Depends(get_current_user)
) -> UserAuth:
    """Get current active user."""
    
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    return current_user


async def get_current_admin_user(
    current_user: UserAuth = Depends(get_current_active_user)
) -> UserAuth:
    """Get current admin user."""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return current_user


async def get_current_merchant_user(
    current_user: UserAuth = Depends(get_current_active_user)
) -> UserAuth:
    """Get current merchant user."""
    
    if current_user.role not in ["merchant", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Merchant access required"
        )
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[UserAuth]:
    """Get current user if authenticated, otherwise return None."""
    
    if not credentials:
        return None
    
    try:
        user = await auth_service.validate_token(credentials.credentials)
        return user
    except Exception:
        return None


def require_role(required_role: str):
    """Dependency factory for role-based access control."""
    
    async def role_checker(
        current_user: UserAuth = Depends(get_current_active_user)
    ) -> UserAuth:
        """Check if user has required role."""
        
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"{required_role.capitalize()} access required"
            )
        
        return current_user
    
    return role_checker


def require_any_role(required_roles: list):
    """Dependency factory for multiple role-based access control."""
    
    async def role_checker(
        current_user: UserAuth = Depends(get_current_active_user)
    ) -> UserAuth:
        """Check if user has any of the required roles."""
        
        if current_user.role not in required_roles and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(required_roles)}"
            )
        
        return current_user
    
    return role_checker


# Predefined role dependencies
require_user = require_role("user")
require_merchant = require_role("merchant")
require_admin = require_role("admin")
require_user_or_merchant = require_any_role(["user", "merchant"])
require_merchant_or_admin = require_any_role(["merchant", "admin"])




