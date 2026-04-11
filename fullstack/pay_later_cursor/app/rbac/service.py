from typing import List, Optional, Dict, Any
from datetime import datetime
from app.rbac.models import Role, Permission, UserRole, RoleResponse, PermissionResponse, UserRoleResponse
from app.rbac.repository import RBACRepository
from app.common.exceptions import NotFoundError, ValidationError, DuplicateEntity
import structlog

logger = structlog.get_logger(__name__)


class RBACService:
    """Service for RBAC operations."""
    
    def __init__(self, rbac_repository: RBACRepository):
        self.rbac_repository = rbac_repository
    
    # Role Management
    async def create_role(self, name: str, description: str, permissions: List[str] = None) -> RoleResponse:
        """Create a new role."""
        # Check if role already exists
        existing_role = await self.rbac_repository.get_role_by_name(name)
        if existing_role:
            raise DuplicateEntity("Role", "name", name)
        
        # Validate permissions
        if permissions:
            await self._validate_permissions(permissions)
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions or []
        )
        
        role_id = await self.rbac_repository.create_role(role)
        
        logger.info("Role created successfully", role_id=role_id, name=name)
        
        # Get the created role
        created_role = await self.rbac_repository.get_role_by_id(role_id)
        if not created_role:
            raise ValidationError("Failed to retrieve created role")
        
        return RoleResponse(
            id=str(created_role._id),
            name=created_role.name,
            description=created_role.description,
            permissions=created_role.permissions,
            is_active=created_role.is_active,
            created_at=created_role.created_at,
            updated_at=created_role.updated_at
        )
    
    async def get_role(self, role_id: str) -> RoleResponse:
        """Get role by ID."""
        role = await self.rbac_repository.get_role_by_id(role_id)
        if not role:
            raise NotFoundError(f"Role not found: {role_id}")
        
        return RoleResponse(
            id=str(role._id),
            name=role.name,
            description=role.description,
            permissions=role.permissions,
            is_active=role.is_active,
            created_at=role.created_at,
            updated_at=role.updated_at
        )
    
    async def get_all_roles(self, active_only: bool = True) -> List[RoleResponse]:
        """Get all roles."""
        roles = await self.rbac_repository.get_all_roles()
        
        return [
            RoleResponse(
                id=str(role._id),
                name=role.name,
                description=role.description,
                permissions=role.permissions,
                is_active=role.is_active,
                created_at=role.created_at,
                updated_at=role.updated_at
            )
            for role in roles
        ]
    
    async def update_role(self, role_id: str, update_data: Dict[str, Any]) -> RoleResponse:
        """Update role."""
        # Check if role exists
        existing_role = await self.rbac_repository.get_role_by_id(role_id)
        if not existing_role:
            raise NotFoundError(f"Role not found: {role_id}")
        
        # Validate permissions if being updated
        if "permissions" in update_data:
            await self._validate_permissions(update_data["permissions"])
        
        success = await self.rbac_repository.update_role(role_id, update_data)
        if not success:
            raise ValidationError("Failed to update role")
        
        # Get the updated role
        updated_role = await self.rbac_repository.get_role_by_id(role_id)
        if not updated_role:
            raise ValidationError("Failed to retrieve updated role")
        
        return RoleResponse(
            id=str(updated_role._id),
            name=updated_role.name,
            description=updated_role.description,
            permissions=updated_role.permissions,
            is_active=updated_role.is_active,
            created_at=updated_role.created_at,
            updated_at=updated_role.updated_at
        )
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete role (soft delete)."""
        # Check if role exists
        existing_role = await self.rbac_repository.get_role_by_id(role_id)
        if not existing_role:
            raise NotFoundError(f"Role not found: {role_id}")
        
        success = await self.rbac_repository.delete_role(role_id)
        if success:
            logger.info("Role deleted successfully", role_id=role_id)
        
        return success
    
    # Permission Management
    async def create_permission(self, name: str, resource: str, action: str, description: str) -> PermissionResponse:
        """Create a new permission."""
        # Check if permission already exists
        existing_permission = await self.rbac_repository.get_permission_by_name(name)
        if existing_permission:
            raise DuplicateEntity("Permission", "name", name)
        
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        
        permission_id = await self.rbac_repository.create_permission(permission)
        
        logger.info("Permission created successfully", permission_id=permission_id, name=name)
        
        # Get the created permission
        created_permission = await self.rbac_repository.get_permission_by_id(permission_id)
        if not created_permission:
            raise ValidationError("Failed to retrieve created permission")
        
        return PermissionResponse(
            id=str(created_permission._id),
            name=created_permission.name,
            resource=created_permission.resource,
            action=created_permission.action,
            description=created_permission.description,
            is_active=created_permission.is_active,
            created_at=created_permission.created_at,
            updated_at=created_permission.updated_at
        )
    
    async def get_all_permissions(self, active_only: bool = True) -> List[PermissionResponse]:
        """Get all permissions."""
        permissions = await self.rbac_repository.get_all_permissions()
        
        return [
            PermissionResponse(
                id=str(permission._id),
                name=permission.name,
                resource=permission.resource,
                action=permission.action,
                description=permission.description,
                is_active=permission.is_active
            )
            for permission in permissions
        ]
    
    # User Role Management
    async def assign_role_to_user(self, user_id: str, role_id: str, assigned_by: str, expires_at: Optional[datetime] = None) -> UserRoleResponse:
        """Assign role to user."""
        # Check if role exists
        role = await self.rbac_repository.get_role_by_id(role_id)
        if not role:
            raise NotFoundError(f"Role not found: {role_id}")
        
        # Check if user already has this role
        user_roles = await self.rbac_repository.get_user_roles(user_id)
        for user_role in user_roles:
            if user_role.role_id == role_id:
                raise ValidationError(f"User already has role: {role.name}")
        
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=assigned_by,
            expires_at=expires_at
        )
        
        user_role_id = await self.rbac_repository.assign_role_to_user(user_role)
        
        logger.info("Role assigned to user successfully", 
                   user_id=user_id, 
                   role_id=role_id,
                   assigned_by=assigned_by)
        
        # Get the created user role
        created_user_role = await self.rbac_repository.get_user_role_by_id(user_role_id)
        if not created_user_role:
            raise ValidationError("Failed to retrieve created user role")
        
        return UserRoleResponse(
            id=str(created_user_role._id),
            user_id=created_user_role.user_id,
            role_id=created_user_role.role_id,
            role_name=role.name,
            assigned_by=created_user_role.assigned_by,
            expires_at=created_user_role.expires_at,
            is_active=created_user_role.is_active,
            created_at=created_user_role.created_at,
            updated_at=created_user_role.updated_at
        )
    
    async def get_user_roles(self, user_id: str, active_only: bool = True) -> List[UserRoleResponse]:
        """Get all roles assigned to a user."""
        user_roles = await self.rbac_repository.get_user_roles(user_id)
        
        user_role_responses = []
        for user_role in user_roles:
            role = await self.rbac_repository.get_role_by_id(user_role.role_id)
            if role:
                user_role_responses.append(UserRoleResponse(
                    id=str(user_role._id),
                    user_id=user_role.user_id,
                    role_id=user_role.role_id,
                    role_name=role.name,
                    assigned_by=user_role.assigned_by,
                    expires_at=user_role.expires_at,
                    is_active=user_role.is_active,
                    created_at=user_role.created_at,
                    updated_at=user_role.updated_at
                ))
        
        return user_role_responses
    
    async def remove_user_role(self, user_id: str, role_id: str) -> bool:
        """Remove role from user."""
        # Find the user role record
        user_roles = await self.rbac_repository.get_user_roles(user_id)
        for user_role in user_roles:
            if user_role.role_id == role_id:
                success = await self.rbac_repository.remove_role_from_user(str(user_role._id))
                if success:
                    logger.info("Role removed from user successfully", user_id=user_id, role_id=role_id)
                return success
        
        return False
    
    # Permission Checking
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get all permissions for a user."""
        return await self.rbac_repository.get_user_permissions(user_id)
    
    async def check_user_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        # Parse permission string (format: "resource:action")
        if ":" not in permission:
            return False
        resource, action = permission.split(":", 1)
        return await self.rbac_repository.check_user_permission(user_id, resource, action)
    
    async def check_user_permissions(self, user_id: str, permissions: List[str]) -> Dict[str, bool]:
        """Check if user has multiple permissions."""
        user_permissions = await self.get_user_permissions(user_id)
        return {permission: permission in user_permissions for permission in permissions}
    
    # Helper Methods
    async def _validate_permissions(self, permissions: List[str]) -> None:
        """Validate that all permissions exist."""
        for permission in permissions:
            existing_permission = await self.rbac_repository.get_permission_by_name(permission)
            if not existing_permission:
                raise ValidationError(f"Permission not found: {permission}")
    
    async def get_user_role_names(self, user_id: str) -> List[str]:
        """Get role names for a user."""
        user_roles = await self.get_user_roles(user_id)
        return [user_role.role_name for user_role in user_roles]
    
    async def has_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role."""
        user_role_names = await self.get_user_role_names(user_id)
        return role_name in user_role_names
