from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.dependencies import get_current_active_user
from app.auth.models import UserAuth
from app.rbac.repository import RBACRepository
from app.db.mongo import get_database

security = HTTPBearer()

# Get RBAC repository instance
async def get_rbac_repository() -> RBACRepository:
	database = await get_database()
	return RBACRepository(database)

# Base permission checking function
async def check_permission(
	user: UserAuth,
	resource: str,
	action: str,
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> bool:
	"""Check if user has permission for resource:action."""
	return await rbac_repo.check_user_permission(str(user.user_id), resource, action)

# Base role checking function
async def check_role(
	user: UserAuth,
	role_name: str,
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> bool:
	"""Check if user has specific role."""
	return await rbac_repo.check_user_role(str(user.user_id), role_name)

# Permission middleware functions
async def require_permission(
	resource: str,
	action: str,
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require specific permission."""
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), resource, action)
	if not has_permission:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=f"Insufficient permissions. Required: {resource}:{action}"
		)
	return current_user

async def require_any_permission(
	permissions: List[str],
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require any of the specified permissions."""
	user_permissions = await rbac_repo.get_user_permissions(str(current_user.user_id))
	for permission in permissions:
		if permission in user_permissions:
			return current_user
	
	raise HTTPException(
		status_code=status.HTTP_403_FORBIDDEN,
		detail=f"Insufficient permissions. Required any of: {permissions}"
	)

async def require_all_permissions(
	permissions: List[str],
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require all specified permissions."""
	user_permissions = await rbac_repo.get_user_permissions(str(current_user.user_id))
	for permission in permissions:
		if permission not in user_permissions:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail=f"Insufficient permissions. Required: {permission}"
			)
	return current_user

# Role middleware functions
async def require_role(
	role_name: str,
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require specific role."""
	has_role = await rbac_repo.check_user_role(str(current_user.user_id), role_name)
	if not has_role:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail=f"Insufficient role. Required: {role_name}"
		)
	return current_user

async def require_any_role(
	role_names: List[str],
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require any of the specified roles."""
	for role_name in role_names:
		has_role = await rbac_repo.check_user_role(str(current_user.user_id), role_name)
		if has_role:
			return current_user
	
	raise HTTPException(
		status_code=status.HTTP_403_FORBIDDEN,
		detail=f"Insufficient role. Required any of: {role_names}"
	)

# Specific permission middleware functions
async def require_users_read(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "users", "read")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: users:read")
	return current_user

async def require_users_write(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "users", "write")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: users:write")
	return current_user

async def require_users_delete(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "users", "delete")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: users:delete")
	return current_user

async def require_merchants_read(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "merchants", "read")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: merchants:read")
	return current_user

async def require_merchants_write(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "merchants", "write")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: merchants:write")
	return current_user

async def require_transactions_read(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "transactions", "read")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: transactions:read")
	return current_user

async def require_transactions_write(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "transactions", "write")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: transactions:write")
	return current_user

async def require_transactions_approve(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "transactions", "approve")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: transactions:approve")
	return current_user

async def require_reports_read(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "reports", "read")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: reports:read")
	return current_user

async def require_reports_export(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	has_permission = await rbac_repo.check_user_permission(str(current_user.user_id), "reports", "export")
	if not has_permission:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions. Required: reports:export")
	return current_user

# Specific role middleware functions
async def require_system_admin(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require system_admin role."""
	has_role = await rbac_repo.check_user_role(str(current_user.user_id), "system_admin")
	if not has_role:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Insufficient role. Required: system_admin"
		)
	return current_user

async def require_admin_role(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require admin role."""
	has_role = await rbac_repo.check_user_role(str(current_user.user_id), "admin")
	if not has_role:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Insufficient role. Required: admin"
		)
	return current_user

async def require_merchant_role(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require merchant role."""
	has_role = await rbac_repo.check_user_role(str(current_user.user_id), "merchant")
	if not has_role:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Insufficient role. Required: merchant"
		)
	return current_user

async def require_user_role(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require user role."""
	has_role = await rbac_repo.check_user_role(str(current_user.user_id), "user")
	if not has_role:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Insufficient role. Required: user"
		)
	return current_user

# Combined role middleware functions
async def require_admin_or_merchant(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require either admin or merchant role."""
	for role_name in ["admin", "merchant"]:
		if await rbac_repo.check_user_role(str(current_user.user_id), role_name):
			return current_user
	raise HTTPException(
		status_code=status.HTTP_403_FORBIDDEN,
		detail="Insufficient role. Required any of: ['admin', 'merchant']"
	)

async def require_admin_or_user(
	current_user: UserAuth = Depends(get_current_active_user),
	rbac_repo: RBACRepository = Depends(get_rbac_repository)
) -> UserAuth:
	"""Require either admin or user role."""
	for role_name in ["admin", "user"]:
		if await rbac_repo.check_user_role(str(current_user.user_id), role_name):
			return current_user
	raise HTTPException(
		status_code=status.HTTP_403_FORBIDDEN,
		detail="Insufficient role. Required any of: ['admin', 'user']"
	)
