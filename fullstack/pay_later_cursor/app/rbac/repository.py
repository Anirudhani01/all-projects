from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.rbac.models import Role, Permission, UserRole


class RBACRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.roles_collection = database.roles
        self.permissions_collection = database.permissions
        self.user_roles_collection = database.user_roles

    # Role operations
    async def create_role(self, role: Role) -> str:
        """Create a new role."""
        role_dict = role.dict(exclude={'id'})
        result = await self.roles_collection.insert_one(role_dict)
        return str(result.inserted_id)

    async def get_role_by_id(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        try:
            role_dict = await self.roles_collection.find_one({"_id": ObjectId(role_id)})
            if role_dict:
                role_dict["id"] = str(role_dict["_id"])
                return Role(**role_dict)
            return None
        except Exception:
            return None

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        role_dict = await self.roles_collection.find_one({"name": name})
        if role_dict:
            role_dict["id"] = str(role_dict["_id"])
            # Convert ObjectId to string for Pydantic validation
            if "_id" in role_dict:
                role_dict["_id"] = str(role_dict["_id"])
            return Role(**role_dict)
        return None

    async def get_all_roles(self) -> List[Role]:
        """Get all roles."""
        roles = []
        cursor = self.roles_collection.find({"is_active": True})
        async for role_dict in cursor:
            role_dict["id"] = str(role_dict["_id"])
            roles.append(Role(**role_dict))
        return roles

    async def update_role(self, role_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a role."""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.roles_collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_role(self, role_id: str) -> bool:
        """Delete a role (soft delete)."""
        result = await self.roles_collection.update_one(
            {"_id": ObjectId(role_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    # Permission operations
    async def create_permission(self, permission: Permission) -> str:
        """Create a new permission."""
        permission_dict = permission.dict(exclude={'id'})
        result = await self.permissions_collection.insert_one(permission_dict)
        return str(result.inserted_id)

    async def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get permission by ID."""
        try:
            permission_dict = await self.permissions_collection.find_one({"_id": ObjectId(permission_id)})
            if permission_dict:
                permission_dict["id"] = str(permission_dict["_id"])
                return Permission(**permission_dict)
            return None
        except Exception:
            return None

    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        permission_dict = await self.permissions_collection.find_one({"name": name})
        if permission_dict:
            permission_dict["id"] = str(permission_dict["_id"])
            # Convert ObjectId to string for Pydantic validation
            if "_id" in permission_dict:
                permission_dict["_id"] = str(permission_dict["_id"])
            return Permission(**permission_dict)
        return None

    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        permissions = []
        cursor = self.permissions_collection.find({"is_active": True})
        async for permission_dict in cursor:
            permission_dict["id"] = str(permission_dict["_id"])
            permissions.append(Permission(**permission_dict))
        return permissions

    async def get_permissions_by_ids(self, permission_ids: List[str]) -> List[Permission]:
        """Get permissions by IDs."""
        permissions = []
        object_ids = [ObjectId(pid) for pid in permission_ids]
        cursor = self.permissions_collection.find({"_id": {"$in": object_ids}})
        async for permission_dict in cursor:
            permission_dict["id"] = str(permission_dict["_id"])
            # Convert ObjectId to string for Pydantic validation
            if "_id" in permission_dict:
                permission_dict["_id"] = str(permission_dict["_id"])
            permissions.append(Permission(**permission_dict))
        return permissions

    async def update_permission(self, permission_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a permission."""
        update_data["updated_at"] = datetime.utcnow()
        result = await self.permissions_collection.update_one(
            {"_id": ObjectId(permission_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_permission(self, permission_id: str) -> bool:
        """Delete a permission (soft delete)."""
        result = await self.permissions_collection.update_one(
            {"_id": ObjectId(permission_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    # UserRole operations
    async def assign_role_to_user(self, user_role: UserRole) -> str:
        """Assign a role to a user."""
        user_role_dict = user_role.dict(exclude={'id'})
        result = await self.user_roles_collection.insert_one(user_role_dict)
        return str(result.inserted_id)

    async def get_user_roles(self, user_id: str) -> List[UserRole]:
        """Get all roles assigned to a user."""
        user_roles = []
        cursor = self.user_roles_collection.find({
            "user_id": user_id,
            "is_active": True
        })
        async for user_role_dict in cursor:
            user_role_dict["id"] = str(user_role_dict["_id"])
            # Convert ObjectId to string for Pydantic validation
            if "_id" in user_role_dict:
                user_role_dict["_id"] = str(user_role_dict["_id"])
            user_roles.append(UserRole(**user_role_dict))
        return user_roles

    async def get_user_role_by_id(self, user_role_id: str) -> Optional[UserRole]:
        """Get user role by ID."""
        try:
            user_role_dict = await self.user_roles_collection.find_one({"_id": ObjectId(user_role_id)})
            if user_role_dict:
                user_role_dict["id"] = str(user_role_dict["_id"])
                return UserRole(**user_role_dict)
            return None
        except Exception:
            return None

    async def remove_role_from_user(self, user_role_id: str) -> bool:
        """Remove a role from a user (soft delete)."""
        result = await self.user_roles_collection.update_one(
            {"_id": ObjectId(user_role_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user based on their roles."""
        # Get user's active roles
        user_roles = await self.get_user_roles(user_id)
        if not user_roles:
            return []

        # Get role IDs
        role_ids = [ur.role_id for ur in user_roles]
        
        # Get roles with their permissions
        roles = []
        object_ids = [ObjectId(rid) for rid in role_ids]
        cursor = self.roles_collection.find({"_id": {"$in": object_ids}, "is_active": True})
        async for role_dict in cursor:
            roles.append(role_dict)

        # Collect all permission IDs
        permission_ids = []
        for role in roles:
            permission_ids.extend(role.get("permissions", []))

        # Get unique permissions
        unique_permission_ids = list(set(permission_ids))
        
        # Get permission names
        permissions = await self.get_permissions_by_ids(unique_permission_ids)
        return [f"{p.resource}:{p.action}" for p in permissions]

    async def check_user_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if a user has a specific permission."""
        user_permissions = await self.get_user_permissions(user_id)
        required_permission = f"{resource}:{action}"
        return required_permission in user_permissions

    async def check_user_role(self, user_id: str, role_name: str) -> bool:
        """Check if a user has a specific role."""
        user_roles = await self.get_user_roles(user_id)
        if not user_roles:
            return False

        # Get role names for user's roles
        role_ids = [ur.role_id for ur in user_roles]
        object_ids = [ObjectId(rid) for rid in role_ids]
        cursor = self.roles_collection.find({"_id": {"$in": object_ids}, "is_active": True})
        
        async for role_dict in cursor:
            if role_dict.get("name") == role_name:
                return True
        
        return False
