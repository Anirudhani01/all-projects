from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field


class Role(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True
    }


class Permission(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True
    }


class UserRole(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    role_id: str
    assigned_by: Optional[str] = None
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True
    }


# Enums
class ResourceType(str):
    USERS = "users"
    MERCHANTS = "merchants"
    TRANSACTIONS = "transactions"
    REPORTS = "reports"
    SYSTEM = "system"
    # NEW: Wallet system resources
    WALLET = "wallet"
    CREDIT = "credit"
    WALLET_TRANSACTIONS = "wallet_transactions"


class PermissionAction(str):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    APPROVE = "approve"
    EXPORT = "export"


# Request/Response models
class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    permissions: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PermissionCreateRequest(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class PermissionResponse(BaseModel):
    id: str
    name: str
    resource: str
    action: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserRoleCreateRequest(BaseModel):
    user_id: str
    role_id: str
    expires_at: Optional[datetime] = None


class UserRoleResponse(BaseModel):
    id: str
    user_id: str
    role_id: str
    role_name: Optional[str] = None
    assigned_by: Optional[str]
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
