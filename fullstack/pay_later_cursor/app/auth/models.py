"""
Authentication models for LazyPay application.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserAuth(BaseModel):
    """User authentication model."""
    
    user_id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    is_active: bool = Field(default=True, description="Whether user account is active")
    role: str = Field(default="user", description="User role (user, admin, merchant)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation timestamp")
    last_login: Optional[datetime] = Field(default=None, description="Last login timestamp")


class TokenData(BaseModel):
    """Token data model for JWT payload."""
    
    user_id: str = Field(..., description="User ID from token")
    email: str = Field(..., description="User email from token")
    name: str = Field(..., description="User name from token")
    role: str = Field(..., description="User role from token")
    exp: datetime = Field(..., description="Token expiration timestamp")
    iat: datetime = Field(..., description="Token issued at timestamp")
    token_type: str = Field(..., description="Token type (access, refresh)")


class TokenPair(BaseModel):
    """Token pair model for access and refresh tokens."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")


class LoginRequest(BaseModel):
    """Login request model."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=6)


class RefreshRequest(BaseModel):
    """Refresh token request model."""
    
    refresh_token: str = Field(..., description="Valid refresh token")


class LogoutRequest(BaseModel):
    """Logout request model."""
    
    refresh_token: str = Field(..., description="Refresh token to invalidate")


class PasswordChangeRequest(BaseModel):
    """Password change request model."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password", min_length=6)


class TokenBlacklist(BaseModel):
    """Token blacklist model for logout functionality."""
    
    token_id: str = Field(..., description="Unique token identifier")
    user_id: str = Field(..., description="User ID who owns the token")
    token_type: str = Field(..., description="Token type (access, refresh)")
    expires_at: datetime = Field(..., description="Token expiration timestamp")
    reason: Optional[str] = Field(default=None, description="Reason for blacklisting")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Blacklist entry creation timestamp")
