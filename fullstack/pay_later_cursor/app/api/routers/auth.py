"""
Authentication API router for LazyPay application.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from app.auth.service import AuthService
from app.auth.models import UserAuth
from app.auth.schemas import (
    LoginRequestSchema,
    RegisterRequestSchema,
    RefreshTokenRequestSchema,
    LogoutRequestSchema,
    PasswordChangeRequestSchema,
    LoginResponseSchema,
    RefreshTokenResponseSchema,
    LogoutResponseSchema,
    PasswordChangeResponseSchema,
    UserProfileResponseSchema,
    AuthErrorResponseSchema,
    TokenErrorResponseSchema
)
from app.auth.dependencies import (
    get_current_active_user,
    get_current_user,
    get_auth_service
)
from app.common.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme
security = HTTPBearer()


@router.post(
    "/login",
    response_model=LoginResponseSchema,
    summary="User login",
    description="Authenticate user and return access and refresh tokens",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "access_expires_in": 180,
                        "refresh_expires_in": 300,
                        "user": {
                            "user_id": "507f1f77bcf86cd799439011",
                            "email": "user@example.com",
                            "name": "John Doe",
                            "role": "user",
                            "is_active": True,
                            "created_at": "2025-08-17T10:00:00Z",
                            "last_login": "2025-08-17T10:00:00Z"
                        }
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": AuthErrorResponseSchema
        }
    }
)
async def login(
    login_request: LoginRequestSchema,
    auth_service: AuthService = Depends(get_auth_service)
) -> LoginResponseSchema:
    """
    Authenticate user and return JWT tokens.
    
    - **email**: User email address
    - **password**: User password (minimum 6 characters)
    
    Returns access token (3 minutes) and refresh token (5 minutes).
    """
    try:
        from app.auth.models import LoginRequest
        
        # Convert schema to model
        login_model = LoginRequest(
            email=login_request.email,
            password=login_request.password
        )
        
        return await auth_service.login(login_model)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/refresh",
    response_model=RefreshTokenResponseSchema,
    summary="Refresh access token",
    description="Get new access token using refresh token",
    responses={
        200: {
            "description": "Token refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 180
                    }
                }
            }
        },
        401: {
            "description": "Invalid or expired refresh token",
            "model": TokenErrorResponseSchema
        },
        422: {
            "description": "Validation error",
            "model": AuthErrorResponseSchema
        }
    }
)
async def refresh_token(
    refresh_request: RefreshTokenRequestSchema,
    auth_service: AuthService = Depends(get_auth_service)
) -> RefreshTokenResponseSchema:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token (3 minutes).
    """
    try:
        from app.auth.models import RefreshRequest
        
        # Convert schema to model
        refresh_model = RefreshRequest(
            refresh_token=refresh_request.refresh_token
        )
        
        return await auth_service.refresh_token(refresh_model)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post(
    "/logout",
    response_model=LogoutResponseSchema,
    summary="User logout",
    description="Logout user by blacklisting refresh token",
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Successfully logged out",
                        "timestamp": "2025-08-17T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponseSchema
        }
    }
)
async def logout(
    logout_request: LogoutRequestSchema,
    current_user: UserAuth = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> LogoutResponseSchema:
    """
    Logout user by blacklisting refresh token.
    
    - **refresh_token**: Refresh token to invalidate
    
    Requires authentication.
    """
    try:
        from app.auth.models import LogoutRequest
        
        # Convert schema to model
        logout_model = LogoutRequest(
            refresh_token=logout_request.refresh_token
        )
        
        return await auth_service.logout(logout_model, current_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/change-password",
    response_model=PasswordChangeResponseSchema,
    summary="Change password",
    description="Change user password",
    responses={
        200: {
            "description": "Password changed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password changed successfully",
                        "timestamp": "2025-08-17T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponseSchema
        },
        422: {
            "description": "Validation error",
            "model": AuthErrorResponseSchema
        }
    }
)
async def change_password(
    password_request: PasswordChangeRequestSchema,
    current_user: UserAuth = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> PasswordChangeResponseSchema:
    """
    Change user password.
    
    - **current_password**: Current password
    - **new_password**: New password (minimum 6 characters)
    
    Requires authentication.
    """
    try:
        from app.auth.models import PasswordChangeRequest
        
        # Convert schema to model
        password_model = PasswordChangeRequest(
            current_password=password_request.current_password,
            new_password=password_request.new_password
        )
        
        return await auth_service.change_password(password_model, current_user)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/profile",
    response_model=UserProfileResponseSchema,
    summary="Get user profile",
    description="Get current user profile information",
    responses={
        200: {
            "description": "User profile retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "507f1f77bcf86cd799439011",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2025-08-17T10:00:00Z",
                        "last_login": "2025-08-17T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponseSchema
        },
        404: {
            "description": "User not found",
            "model": AuthErrorResponseSchema
        }
    }
)
async def get_profile(
    current_user: UserAuth = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserProfileResponseSchema:
    """
    Get current user profile information.
    
    Requires authentication.
    """
    try:
        return await auth_service.get_user_profile(current_user.user_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/me")
async def get_current_user(
    current_user: UserAuth = Depends(get_current_active_user)
) -> UserAuth:
    """Get current user information."""
    return current_user


@router.get("/me/role")
async def get_current_user_role(
    current_user: UserAuth = Depends(get_current_active_user)
):
    """Get current user's role information."""
    from app.rbac.repository import RBACRepository
    from app.db.mongo import mongodb
    
    rbac_repo = RBACRepository(mongodb.get_database())
    user_roles = await rbac_repo.get_user_roles(str(current_user.user_id))
    
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "roles": user_roles
    }


@router.post("/create-default-users")
async def create_default_users(
    auth_service: AuthService = Depends(get_auth_service)
):
    """Create default users for testing."""
    try:
        from app.auth.schemas import RegisterRequestSchema
        
        # Create admin user
        admin_request = RegisterRequestSchema(
            email="admin@admin.com",
            name="John Admin",
            password="admin123",
            role="admin"
        )
        
        # Create merchant user
        merchant_request = RegisterRequestSchema(
            email="alice@merchant.com",
            name="Alice Merchant",
            password="merchant123",
            role="merchant"
        )
        
        # Create regular user
        user_request = RegisterRequestSchema(
            email="bob@user.com",
            name="Bob User",
            password="user123",
            role="user"
        )
        
        results = []
        
        try:
            admin_result = await auth_service.create_user(
                email=admin_request.email,
                name=admin_request.name,
                password=admin_request.password,
                role=admin_request.role
            )
            results.append({"email": "admin@admin.com", "status": "created", "user_id": admin_result.user_id})
        except Exception as e:
            results.append({"email": "admin@admin.com", "status": "error", "error": str(e)})
        
        try:
            merchant_result = await auth_service.create_user(
                email=merchant_request.email,
                name=merchant_request.name,
                password=merchant_request.password,
                role=merchant_request.role
            )
            results.append({"email": "alice@merchant.com", "status": "created", "user_id": merchant_result.user_id})
        except Exception as e:
            results.append({"email": "alice@merchant.com", "status": "error", "error": str(e)})
        
        try:
            user_result = await auth_service.create_user(
                email=user_request.email,
                name=user_request.name,
                password=user_request.password,
                role=user_request.role
            )
            results.append({"email": "bob@user.com", "status": "created", "user_id": user_result.user_id})
        except Exception as e:
            results.append({"email": "bob@user.com", "status": "error", "error": str(e)})
        
        return {"message": "Default users creation attempted", "results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create default users: {str(e)}")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/me",
    response_model=UserProfileResponseSchema,
    summary="Get current user",
    description="Get current authenticated user information",
    responses={
        200: {
            "description": "Current user retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "507f1f77bcf86cd799439011",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2025-08-17T10:00:00Z",
                        "last_login": "2025-08-17T10:00:00Z"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "model": AuthErrorResponseSchema
        }
    }
)
async def get_current_user_info(
    current_user: UserAuth = Depends(get_current_active_user)
) -> UserProfileResponseSchema:
    """
    Get current authenticated user information.
    
    Requires authentication.
    """
    return UserProfileResponseSchema(
        user_id=current_user.user_id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/assign-merchant-role/{email}")
async def assign_merchant_role(
	email: str,
	auth_service: AuthService = Depends(get_auth_service)
):
	"""Manually assign merchant role to a user (for testing)."""
	try:
		from app.api.dependencies import get_database
		from app.rbac.repository import RBACRepository
		from app.rbac.models import UserRole
		from app.auth.repository import AuthRepository
		
		# Get the user
		auth_repo = AuthRepository(get_database())
		user = await auth_repo.get_user_by_email(email)
		if not user:
			raise HTTPException(status_code=404, detail=f"User with email {email} not found")
		
		# Get merchant role
		rbac_repo = RBACRepository(get_database())
		merchant_role = await rbac_repo.get_role_by_name("merchant")
		if not merchant_role:
			raise HTTPException(status_code=404, detail="Merchant role not found in RBAC system")
		
		# Check if user already has merchant role
		has_role = await rbac_repo.check_user_role(str(user.user_id), "merchant")
		if has_role:
			return {"message": f"User {email} already has merchant role"}
		
		# Assign merchant role
		await rbac_repo.assign_role_to_user(UserRole(
			user_id=user.user_id, 
			role_id=merchant_role.id, 
			assigned_by="system"
		))
		
		return {
			"message": f"Merchant role assigned successfully to {email}",
			"user_id": user.user_id,
			"role_id": merchant_role.id
		}
		
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Failed to assign merchant role: {str(e)}")


@router.post(
    "/register",
    response_model=UserProfileResponseSchema,
    summary="Register new user",
    description="Create a new user account",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "user_id": "507f1f77bcf86cd799439011",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2025-08-17T10:00:00Z",
                        "last_login": None
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "model": AuthErrorResponseSchema
        }
    }
)
async def register_user(
    register_request: RegisterRequestSchema,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserProfileResponseSchema:
    """
    Create a new user account.
    
    - **email**: User email address
    - **name**: User full name
    - **password**: User password (minimum 6 characters)
    - **role**: User role (default: user)
    
    Returns created user profile.
    """
    try:
        user = await auth_service.create_user(
            register_request.email, 
            register_request.name, 
            register_request.password, 
            register_request.role
        )
        
        return UserProfileResponseSchema(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")




