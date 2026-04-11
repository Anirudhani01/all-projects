from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from ...models.review import ReviewCreate, ReviewUpdate
from ...core.crud.review import get_review_crud
from ...core.utils import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/")
async def create_review(
    review_data: ReviewCreate,
    user_id: str = Query(..., description="User ID")
):
    """Create a new review."""
    try:
        # Set the user ID from the parameter
        review_data.userId = user_id
        
        review_id = await get_review_crud().create(review_data.dict())
        
        if not review_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review already exists for this product or invalid data"
            )
        
        return create_success_response(
            data={"id": review_id},
            message="Review created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )


@router.get("/")
async def get_reviews(
    product_id: Optional[str] = Query(None, description="Filter by product ID"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    sort_by: str = Query("createdAt", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)")
):
    """Get paginated list of reviews with optional filtering."""
    try:
        filter_params = {
            "productId": product_id,
            "userId": user_id,
            "page": page,
            "limit": limit,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }
        
        # Remove None values
        filter_params = {k: v for k, v in filter_params.items() if v is not None}
        
        reviews = await get_review_crud().get_list(filter_params)
        
        return create_success_response(
            data=reviews,
            message="Reviews retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reviews"
        )


@router.get("/{review_id}")
async def get_review(review_id: str):
    """Get review by ID."""
    try:
        review = await get_review_crud().get_by_id(review_id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        return create_success_response(
            data=review,
            message="Review retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve review"
        )


@router.put("/{review_id}")
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    user_id: str = Query(..., description="User ID")
):
    """Update review by ID."""
    try:
        # Check if review exists and belongs to user
        existing_review = await get_review_crud().get_by_id(review_id)
        if not existing_review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        if existing_review.get("userId") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update review - not your review"
            )
        
        success = await get_review_crud().update(
            review_id,
            review_update.dict(exclude_unset=True)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update review"
            )
        
        return create_success_response(
            data=None,
            message="Review updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review"
        )


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    user_id: str = Query(..., description="User ID")
):
    """Delete a review."""
    try:
        # Check if review exists and belongs to user
        existing_review = await get_review_crud().get_by_id(review_id)
        if not existing_review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )
        
        if existing_review.get("userId") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete review - not your review"
            )
        
        success = await get_review_crud().delete(
            review_id=review_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete review"
            )
        
        return create_success_response(
            data=None,
            message="Review deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete review"
        )
