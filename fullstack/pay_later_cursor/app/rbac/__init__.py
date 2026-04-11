"""
RBAC (Role-Based Access Control) Module

This module provides role-based access control functionality for the LazyPay application.
It includes models, repository, service, initializer, and middleware components.
"""

from .models import (
    Role, Permission, UserRole,
    ResourceType, PermissionAction,
    RoleCreateRequest, RoleUpdateRequest, RoleResponse,
    PermissionCreateRequest, PermissionResponse,
    UserRoleCreateRequest, UserRoleResponse
)

from .repository import RBACRepository
from .service import RBACService
from .initializer import RBACInitializer, initialize_rbac
from .middleware import (
    require_permission, require_any_permission, require_all_permissions,
    require_role, require_any_role,
    require_users_read, require_users_write, require_users_delete,
    require_transactions_read, require_transactions_write, require_transactions_approve,
    require_reports_read, require_reports_export,
    require_merchants_read, require_merchants_write,
    require_system_admin, require_admin_role, require_merchant_role, require_user_role,
    require_admin_or_merchant, require_admin_or_user
)

__all__ = [
    # Models
    'Role', 'Permission', 'UserRole',
    'ResourceType', 'PermissionAction',
    'RoleCreateRequest', 'RoleUpdateRequest', 'RoleResponse',
    'PermissionCreateRequest', 'PermissionResponse',
    'UserRoleCreateRequest', 'UserRoleResponse',
    
    # Repository
    'RBACRepository',
    
    # Service
    'RBACService',
    
    # Initializer
    'RBACInitializer', 'initialize_rbac',
    
    # Middleware
    'require_permission', 'require_any_permission', 'require_all_permissions',
    'require_role', 'require_any_role',
    'require_users_read', 'require_users_write', 'require_users_delete',
    'require_transactions_read', 'require_transactions_write', 'require_transactions_approve',
    'require_reports_read', 'require_reports_export',
    'require_merchants_read', 'require_merchants_write',
    'require_system_admin', 'require_admin_role', 'require_merchant_role', 'require_user_role',
    'require_admin_or_merchant', 'require_admin_or_user'
]
