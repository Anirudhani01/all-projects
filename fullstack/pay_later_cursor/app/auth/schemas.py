"""
Authentication schemas for LazyPay application API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


# Request Schemas
class LoginRequestSchema(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password", min_length=6)


class RegisterRequestSchema(BaseModel):
    """Register request schema."""
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., description="User full name", min_length=2)
    password: str = Field(..., description="User password", min_length=6)
    role: str = Field("user", description="User role")


class RefreshTokenRequestSchema(BaseModel):
    """Refresh token request schema."""
    refresh_token: str = Field(..., description="Valid refresh token")


class LogoutRequestSchema(BaseModel):
    """Logout request schema."""
    refresh_token: str = Field(..., description="Refresh token to invalidate")


class PasswordChangeRequestSchema(BaseModel):
    """Password change request schema."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password", min_length=6)


# Response Schemas
class LoginResponseSchema(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    access_expires_in: int = Field(180, description="Access token expiration in seconds (3 minutes)")
    refresh_expires_in: int = Field(300, description="Refresh token expiration in seconds (5 minutes)")
    user: dict = Field(..., description="User information")


class RefreshTokenResponseSchema(BaseModel):
    """Refresh token response schema."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(180, description="Token expiration in seconds (3 minutes)")


class LogoutResponseSchema(BaseModel):
    """Logout response schema."""
    message: str = Field("Successfully logged out", description="Logout message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PasswordChangeResponseSchema(BaseModel):
    """Password change response schema."""
    message: str = Field("Password changed successfully", description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserProfileResponseSchema(BaseModel):
    """User profile response schema."""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")


# Error Response Schemas
class AuthErrorResponseSchema(BaseModel):
    """Authentication error response schema."""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TokenErrorResponseSchema(BaseModel):
    """Token error response schema."""
    error: str = Field(..., description="Token error type")
    detail: str = Field(..., description="Token error message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Security Schemas
class SecurityScopes(BaseModel):
    """Security scopes for different roles."""
    user: list = Field(["read:own", "write:own"], description="User permissions")
    admin: list = Field(["read:all", "write:all", "delete:all"], description="Admin permissions")
    merchant: list = Field(["read:merchant", "write:merchant"], description="Merchant permissions")




