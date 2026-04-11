"""
Authentication service for LazyPay application.
"""

import bcrypt
import structlog
from datetime import datetime
from typing import Optional

from app.auth.repository import AuthRepository
from app.auth.jwt_handler import jwt_handler
from app.auth.models import (
    UserAuth,
    TokenPair,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    PasswordChangeRequest
)
from app.auth.schemas import (
    LoginResponseSchema,
    RefreshTokenResponseSchema,
    LogoutResponseSchema,
    PasswordChangeResponseSchema,
    UserProfileResponseSchema
)
from app.common.exceptions import NotFoundError, ValidationError

logger = structlog.get_logger(__name__)


class AuthService:
    """Service for authentication-related business logic."""

    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )

    async def authenticate_user(
        self,
        email: str,
        password: str
    ) -> Optional[UserAuth]:
        """Authenticate a user with email and password."""
        
        logger.info("Authenticating user", email=email)
        
        # Get user by email
        user = await self.auth_repository.get_user_by_email(email)
        if not user:
            logger.warning("User not found", email=email)
            return None
        
        # Check if user is active
        if not user.is_active:
            logger.warning("User account is inactive", email=email)
            return None
        
        # Verify password
        is_valid = await self.auth_repository.verify_password(email, password)
        if not is_valid:
            logger.warning("Invalid password", email=email)
            return None
        
        # Update last login
        await self.auth_repository.update_last_login(user.user_id)
        
        logger.info("User authenticated successfully", user_id=user.user_id, email=email)
        return user

    async def login(
        self,
        login_request: LoginRequest
    ) -> LoginResponseSchema:
        """Authenticate user and return tokens."""
        
        logger.info("Processing login request", email=login_request.email)
        
        # Validate input
        if not login_request.email or not login_request.password:
            raise ValidationError("Email and password are required")
        
        # Authenticate user
        user = await self.authenticate_user(login_request.email, login_request.password)
        if not user:
            raise ValidationError("Invalid email or password")
        
        # Create tokens
        access_token = jwt_handler.create_access_token(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role
        )
        
        refresh_token = jwt_handler.create_refresh_token(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role
        )
        
        # Prepare response
        user_info = {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        
        logger.info("Login successful", user_id=user.user_id, email=user.email)
        
        return LoginResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            access_expires_in=180,  # 3 minutes
            refresh_expires_in=300,  # 5 minutes
            user=user_info
        )

    async def refresh_token(
        self,
        refresh_request: RefreshRequest
    ) -> RefreshTokenResponseSchema:
        """Refresh access token using refresh token."""
        
        logger.info("Processing token refresh request")
        
        # Validate refresh token
        token_data = jwt_handler.verify_refresh_token(refresh_request.refresh_token)
        
        # Check if token is blacklisted
        token_id = jwt_handler.get_token_id(refresh_request.refresh_token)
        if token_id:
            is_blacklisted = await self.auth_repository.is_token_blacklisted(token_id)
            if is_blacklisted:
                raise ValidationError("Token has been revoked")
        
        # Get user
        user = await self.auth_repository.get_user_by_id(token_data.user_id)
        if not user or not user.is_active:
            raise ValidationError("User not found or inactive")
        
        # Create new access token
        access_token = jwt_handler.create_access_token(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role
        )
        
        logger.info("Token refreshed successfully", user_id=user.user_id)
        
        return RefreshTokenResponseSchema(
            access_token=access_token,
            token_type="bearer",
            expires_in=180  # 3 minutes
        )

    async def logout(
        self,
        logout_request: LogoutRequest,
        current_user: UserAuth
    ) -> LogoutResponseSchema:
        """Logout user by blacklisting refresh token."""
        
        logger.info("Processing logout request", user_id=current_user.user_id)
        
        # Get token payload
        token_payload = jwt_handler.get_token_payload(logout_request.refresh_token)
        token_id = token_payload.get("jti")
        
        if token_id:
            # Get token expiration
            expires_at = jwt_handler.get_token_expiration(logout_request.refresh_token)
            
            # Blacklist the refresh token
            await self.auth_repository.blacklist_token(
                token_id=token_id,
                user_id=current_user.user_id,
                token_type="refresh",
                expires_at=expires_at or datetime.utcnow(),
                reason="User logout"
            )
            
            logger.info("Token blacklisted successfully", token_id=token_id, user_id=current_user.user_id)
        
        return LogoutResponseSchema(
            message="Successfully logged out",
            timestamp=datetime.utcnow()
        )

    async def change_password(
        self,
        password_request: PasswordChangeRequest,
        current_user: UserAuth
    ) -> PasswordChangeResponseSchema:
        """Change user password."""
        
        logger.info("Processing password change request", user_id=current_user.user_id)
        
        # Validate current password
        is_valid = await self.auth_repository.verify_password(
            current_user.email,
            password_request.current_password
        )
        
        if not is_valid:
            raise ValidationError("Current password is incorrect")
        
        # Hash new password
        new_password_hash = self.hash_password(password_request.new_password)
        
        # Update password
        await self.auth_repository.change_password(
            current_user.user_id,
            new_password_hash
        )
        
        logger.info("Password changed successfully", user_id=current_user.user_id)
        
        return PasswordChangeResponseSchema(
            message="Password changed successfully",
            timestamp=datetime.utcnow()
        )

    async def get_user_profile(
        self,
        user_id: str
    ) -> UserProfileResponseSchema:
        """Get user profile information."""
        
        logger.info("Getting user profile", user_id=user_id)
        
        user = await self.auth_repository.get_user_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        return UserProfileResponseSchema(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )

    async def create_user(
        self,
        email: str,
        name: str,
        password: str,
        role: str = "user",
        credit_limit: float = 1000.0
    ) -> UserAuth:
        """Create a new user account."""
        
        logger.info("Creating new user", email=email, role=role)
        
        # Validate input
        if not email or not name or not password:
            raise ValidationError("Email, name, and password are required")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long")
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user in auth system
        auth_user = await self.auth_repository.create_user(
            email=email,
            name=name,
            password_hash=password_hash,
            role=role
        )

        # Assign RBAC role to user
        try:
            from app.api.dependencies import get_database
            from app.rbac.repository import RBACRepository
            from app.rbac.models import UserRole
            database = get_database()
            rbac_repo = RBACRepository(database)
            role_obj = await rbac_repo.get_role_by_name(role)
            if role_obj:
                await rbac_repo.assign_role_to_user(UserRole(user_id=auth_user.user_id, role_id=role_obj.id, assigned_by="system"))
                logger.info("RBAC role assigned successfully", user_id=auth_user.user_id, role=role, role_id=role_obj.id)
            else:
                logger.warning("Role not found in RBAC system", role=role, user_id=auth_user.user_id)
        except Exception as e:
            logger.error("Failed to assign RBAC role", error=str(e), role=role, user_id=auth_user.user_id)
            # Non-fatal; continue

        # Also create user/merchant in main system (if service is available)
        try:
            from app.api.dependencies import get_database
            database = get_database()
            
            if role == "merchant":
                # Create merchant in merchant system
                from app.modules.merchants.service import MerchantService
                from app.modules.merchants.repository import MerchantRepository
                from app.modules.merchants.models import Merchant, MerchantFeeHistory
                
                merchant_repository = MerchantRepository(database)
                merchant_service = MerchantService(merchant_repository)
                
                # Create merchant in main system
                from app.modules.merchants.schemas import CreateMerchantRequest
                merchant_request = CreateMerchantRequest(
                    name=name,
                    email=email,
                    fee_pct=5.0  # Default fee percentage
                )
                
                created_merchant = await merchant_service.onboard_merchant(merchant_request)
                
                logger.info("Merchant created in both systems", 
                           auth_user_id=auth_user.user_id, 
                           merchant_id=str(created_merchant.id),
                           custom_merchant_id=created_merchant.merchant_id,
                           email=email)
            else:
                # Create user in main user system
                from app.modules.users.service import UserService
                from app.modules.users.repository import UserRepository
                from app.modules.users.models import User, UserBalance
                from app.common.types import UserStatus
                
                user_repository = UserRepository(database)
                
                # Create user in main system
                main_user = User(
                    name=name,
                    email=email,
                    credit_limit=credit_limit,
                    status=UserStatus.ACTIVE
                )
                
                created_main_user = await user_repository.create_user(main_user)
                
                # Create initial balance
                balance = UserBalance(
                    user_id=created_main_user._id,
                    outstanding_amount=0.0,
                    total_purchases=0.0,
                    total_payments=0.0,
                    version=1
                )
                
                await user_repository.create_user_balance(balance)
                
                logger.info("User created in both systems", 
                           auth_user_id=auth_user.user_id, 
                           main_user_id=str(created_main_user._id),
                           custom_user_id=created_main_user.custom_user_id,
                           email=email)
            
        except Exception as e:
            logger.warning(f"Failed to create {role} in main system", error=str(e), email=email)
            # Continue with auth user creation even if main system fails
        
        logger.info("User created successfully", user_id=auth_user.user_id, email=email)
        return auth_user

    async def validate_token(self, token: str) -> UserAuth:
        """Validate access token and return user information."""
        
        # Verify token
        token_data = jwt_handler.verify_access_token(token)
        
        # Check if token is blacklisted
        token_id = jwt_handler.get_token_id(token)
        if token_id:
            is_blacklisted = await self.auth_repository.is_token_blacklisted(token_id)
            if is_blacklisted:
                raise ValidationError("Token has been revoked")
        
        # Get user
        user = await self.auth_repository.get_user_by_id(token_data.user_id)
        if not user:
            raise NotFoundError("User not found")
        
        if not user.is_active:
            raise ValidationError("User account is inactive")
        
        return user

    async def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens from blacklist."""
        
        logger.info("Cleaning up expired tokens")
        
        deleted_count = await self.auth_repository.cleanup_expired_tokens()
        
        logger.info("Expired tokens cleaned up", deleted_count=deleted_count)
        return deleted_count




