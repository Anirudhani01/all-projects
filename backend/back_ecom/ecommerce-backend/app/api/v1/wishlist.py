from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from ...models.wishlist import WishlistItemCreate
from ...core.crud.wishlist import get_wishlist_crud
from ...core.utils import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.post("/")
async def add_to_wishlist(
    item: WishlistItemCreate,
    user_id: str = Query(..., description="User ID")
):
    """Add item to user's wishlist."""
    try:
        # Add user_id to item data
        item_data = item.dict()
        item_data["userId"] = user_id
        
        wishlist_id = await get_wishlist_crud().add_item(item_data)
        
        if not wishlist_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item already in wishlist or invalid data"
            )
        
        return create_success_response(
            data={"id": wishlist_id},
            message="Item added to wishlist successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding item to wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to wishlist"
        )


@router.get("/")
async def get_wishlist(
    user_id: str = Query(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page")
):
    """Get user's wishlist items."""
    try:
        wishlist_items = await get_wishlist_crud().get_wishlist(
            user_id=user_id,
            page=page,
            limit=limit
        )
        
        return create_success_response(
            data=wishlist_items,
            message="Wishlist retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wishlist"
        )


@router.delete("/{item_id}")
async def remove_from_wishlist(
    item_id: str,
    user_id: str = Query(..., description="User ID")
):
    """Remove item from user's wishlist."""
    try:
        success = await get_wishlist_crud().remove_item(
            item_id=item_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Item not found in wishlist or cannot be removed"
            )
        
        return create_success_response(
            data=None,
            message="Item removed from wishlist successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing item from wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove item from wishlist"
        )


@router.get("/count")
async def get_wishlist_count(
    user_id: str = Query(..., description="User ID")
):
    """Get count of items in user's wishlist."""
    try:
        count = await get_wishlist_crud().get_wishlist_count(user_id)
        
        return create_success_response(
            data={"count": count},
            message="Wishlist count retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting wishlist count: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wishlist count"
        )


@router.delete("/")
async def clear_wishlist(
    user_id: str = Query(..., description="User ID")
):
    """Clear all items from user's wishlist."""
    try:
        success = await get_wishlist_crud().clear_wishlist(user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to clear wishlist"
            )
        
        return create_success_response(
            data=None,
            message="Wishlist cleared successfully"
        )
        
    except Exception as e:
        logger.error(f"Error clearing wishlist: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear wishlist"
        )
