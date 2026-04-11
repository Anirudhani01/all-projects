from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.auth.dependencies import get_current_active_user
from app.auth.models import UserAuth
from app.rbac.service import RBACService
from app.rbac.repository import RBACRepository
from app.rbac.models import (
    RoleCreateRequest, RoleUpdateRequest, RoleResponse,
    PermissionCreateRequest, PermissionResponse,
    UserRoleCreateRequest, UserRoleResponse
)
from app.db.mongo import get_database
from app.rbac.middleware import require_admin_role

# Create router
router = APIRouter(prefix="/rbac", tags=["RBAC"])

# Get RBAC service instance
async def get_rbac_service() -> RBACService:
    database = await get_database()
    rbac_repo = RBACRepository(database)
    return RBACService(rbac_repo)


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    current_user: UserAuth = Depends(require_admin_role),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Get all roles."""
    return await rbac_service.get_all_roles()


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreateRequest,
    current_user: UserAuth = Depends(require_admin_role),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Create a new role."""
    return await rbac_service.create_role(
        name=role_data.name,
        description=role_data.description or "",
        permissions=role_data.permissions
    )


@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    current_user: UserAuth = Depends(require_admin_role),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Get all permissions."""
    return await rbac_service.get_all_permissions()


@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreateRequest,
    current_user: UserAuth = Depends(require_admin_role),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Create a new permission."""
    return await rbac_service.create_permission(
        name=permission_data.name,
        resource=permission_data.resource,
        action=permission_data.action,
        description=permission_data.description or ""
    )


@router.post("/user-roles", response_model=UserRoleResponse)
async def assign_role_to_user(
    user_role_data: UserRoleCreateRequest,
    current_user: UserAuth = Depends(require_admin_role),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Assign a role to a user."""
    return await rbac_service.assign_role_to_user(
        user_id=user_role_data.user_id,
        role_id=user_role_data.role_id,
        assigned_by=str(current_user.id),
        expires_at=user_role_data.expires_at
    )


@router.get("/user-roles/{user_id}", response_model=List[UserRoleResponse])
async def get_user_roles(
    user_id: str,
    current_user: UserAuth = Depends(require_admin_role),
    rbac_service: RBACService = Depends(get_rbac_service)
):
    """Get roles assigned to a user."""
    return await rbac_service.get_user_roles(user_id)


@router.get("/health")
async def rbac_health_check():
    """RBAC health check endpoint."""
    return {"status": "healthy", "module": "rbac"}
