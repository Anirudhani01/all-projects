from typing import Dict, List, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.rbac.models import Role, Permission, UserRole, ResourceType, PermissionAction
from app.rbac.repository import RBACRepository


class RBACInitializer:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.rbac_repo = RBACRepository(database)

    async def initialize_default_permissions(self) -> Dict[str, str]:
        """Initialize default permissions."""
        permissions = [
            # User permissions
            {"name": "users:read", "resource": "users", "action": "read", "description": "Read user information"},
            {"name": "users:write", "resource": "users", "action": "write", "description": "Create/update users"},
            {"name": "users:delete", "resource": "users", "action": "delete", "description": "Delete users"},
            
            # Merchant permissions
            {"name": "merchants:read", "resource": "merchants", "action": "read", "description": "Read merchant information"},
            {"name": "merchants:write", "resource": "merchants", "action": "write", "description": "Create/update merchants"},
            {"name": "merchants:delete", "resource": "merchants", "action": "delete", "description": "Delete merchants"},
            
            # Transaction permissions
            {"name": "transactions:read", "resource": "transactions", "action": "read", "description": "Read transaction information"},
            {"name": "transactions:write", "resource": "transactions", "action": "write", "description": "Create/update transactions"},
            {"name": "transactions:approve", "resource": "transactions", "action": "approve", "description": "Approve transactions"},
            
            # Report permissions
            {"name": "reports:read", "resource": "reports", "action": "read", "description": "Read reports"},
            {"name": "reports:export", "resource": "reports", "action": "export", "description": "Export reports"},
            
            # System permissions
            {"name": "system:admin", "resource": "system", "action": "admin", "description": "System administration"},
        ]
        
        permission_ids = {}
        for perm_data in permissions:
            existing = await self.rbac_repo.get_permission_by_name(perm_data["name"])
            if not existing:
                permission = Permission(**perm_data)
                perm_id = await self.rbac_repo.create_permission(permission)
                permission_ids[perm_data["name"]] = perm_id
            else:
                permission_ids[perm_data["name"]] = existing.id
        
        return permission_ids

    async def initialize_default_roles(self, permission_ids: Dict[str, str]) -> Dict[str, str]:
        """Initialize default roles."""
        roles = [
            {
                "name": "system_admin",
                "description": "System administrator with full access",
                "permissions": list(permission_ids.values())
            },
            {
                "name": "admin",
                "description": "Administrator with management access",
                "permissions": [
                    permission_ids["users:read"], permission_ids["users:write"],
                    permission_ids["merchants:read"], permission_ids["merchants:write"],
                    permission_ids["transactions:read"], permission_ids["transactions:write"], permission_ids["transactions:approve"],
                    permission_ids["reports:read"], permission_ids["reports:export"]
                ]
            },
            {
                "name": "merchant",
                "description": "Merchant with transaction and report access",
                "permissions": [
                    permission_ids["transactions:read"], permission_ids["transactions:write"],
                    permission_ids["reports:read"]
                ]
            },
            {
                "name": "user",
                "description": "Regular user with basic access",
                "permissions": [
                    permission_ids["transactions:read"], permission_ids["transactions:write"]
                ]
            }
        ]
        
        role_ids = {}
        for role_data in roles:
            existing = await self.rbac_repo.get_role_by_name(role_data["name"])
            if not existing:
                role = Role(**role_data)
                role_id = await self.rbac_repo.create_role(role)
                role_ids[role_data["name"]] = role_id
            else:
                role_ids[role_data["name"]] = existing.id
        
        return role_ids

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the complete RBAC system."""
        try:
            # Create indexes
            await self.database.roles.create_index("name", unique=True)
            await self.database.permissions.create_index("name", unique=True)
            await self.database.user_roles.create_index([("user_id", 1), ("role_id", 1)])
            
            # Initialize permissions
            permission_ids = await self.initialize_default_permissions()
            
            # Initialize roles
            role_ids = await self.initialize_default_roles(permission_ids)
            
            return {
                "status": "success",
                "permissions_created": len(permission_ids),
                "roles_created": len(role_ids),
                "message": "RBAC system initialized successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to initialize RBAC system: {str(e)}"
            }


async def initialize_rbac(database: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """Initialize RBAC system."""
    initializer = RBACInitializer(database)
    return await initializer.initialize()
