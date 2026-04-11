from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional, List
from ...core.crud.user import get_user_crud
from ...core.utils import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    search: Optional[str] = Query(None, description="Search users by name or email"),
    role: Optional[str] = Query(None, description="Filter by user role"),
):
    """Get paginated list of users (Admin only)."""
    try:
        # Placeholder users data
        users_data = {
            "items": [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": 0,
                "pages": 0
            }
        }
        
        return create_success_response(
            data=users_data,
            message="Users retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get("/{user_id}")
async def get_user(
    user_id: str,
):
    """Get user by ID (Admin only)."""
    try:
        # Placeholder user data
        user_data = {
            "id": user_id,
            "email": "user@example.com",
            "first_name": "User",
            "last_name": "Example",
            "role": "user",
            "isActive": True,
            "createdAt": "2025-01-01T00:00:00Z"
        }
        
        return create_success_response(
            data=user_data,
            message="User retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: str,
    isActive: bool,
):
    """Update user active status (Admin only)."""
    try:
        # Placeholder update logic
        return create_success_response(
            data={"id": user_id, "isActive": isActive},
            message="User status updated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error updating user status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )
