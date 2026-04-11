from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from ...models.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryList,
    SubcategoryCreate, SubcategoryUpdate, SubcategoryResponse, SubcategoryList,
    CategoryFilter
)
from ...core.crud.category import get_category_crud
from ...core.utils import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate
):
    """Create a new category."""
    try:
        category_id = await get_category_crud().create_category(category_data.dict())
        
        if not category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this slug already exists"
            )
        
        # Get created category
        category = await get_category_crud().get_category_by_id(category_id)
        
        return create_success_response(
            data=category,
            message="Category created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=CategoryList)
async def get_categories(
    isActive: Optional[bool] = Query(None, description="Filter by active status"),
    isFeatured: Optional[bool] = Query(None, description="Filter by featured status"),
    search: Optional[str] = Query(None, description="Search categories by name"),
    sortBy: str = Query("sortOrder", description="Sort field"),
    sortOrder: str = Query("asc", description="Sort order (asc/desc)")
):
    """Get all categories with optional filtering."""
    try:
        filter_params = {
            "isActive": isActive,
            "isFeatured": isFeatured,
            "search": search,
            "sortBy": sortBy,
            "sortOrder": sortOrder
        }
        
        # Remove None values
        filter_params = {k: v for k, v in filter_params.items() if v is not None}
        
        categories = await get_category_crud().get_all_categories(filter_params)
        
        return create_success_response(
            data=categories,
            message="Categories retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    """Get a specific category by ID."""
    try:
        category = await get_category_crud().get_category_by_id(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return create_success_response(
            data=category,
            message="Category retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(slug: str):
    """Get a specific category by slug."""
    try:
        category = await get_category_crud().get_category_by_slug(slug)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return create_success_response(
            data=category,
            message="Category retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category by slug: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate
):
    """Update a category."""
    try:
        # Remove None values from update data
        update_data = {k: v for k, v in category_data.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid update data provided"
            )
        
        success = await get_category_crud().update_category(category_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update category or slug already exists"
            )
        
        # Get updated category
        category = await get_category_crud().get_category_by_id(category_id)
        
        return create_success_response(
            data=category,
            message="Category updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{category_id}")
async def delete_category(
    category_id: str
):
    """Delete a category."""
    try:
        success = await get_category_crud().delete_category(category_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category - it has products or doesn't exist"
            )
        
        return create_success_response(
            data=None,
            message="Category deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Subcategory endpoints
@router.post("/{category_id}/subcategories", response_model=SubcategoryResponse)
async def create_subcategory(
    category_id: str,
    subcategory_data: SubcategoryCreate
):
    """Create a new subcategory."""
    try:
        # Add category ID to subcategory data
        subcategory_data_dict = subcategory_data.dict()
        subcategory_data_dict["categoryId"] = category_id
        
        subcategory_id = await get_category_crud().create_subcategory(subcategory_data_dict)
        
        if not subcategory_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subcategory with this slug already exists in this category"
            )
        
        # Get created subcategory
        subcategories = await get_category_crud().get_subcategories_by_category(category_id)
        subcategory = next((s for s in subcategories if s["id"] == subcategory_id), None)
        
        if not subcategory:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve created subcategory"
            )
        
        return create_success_response(
            data=subcategory,
            message="Subcategory created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subcategory: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{category_id}/subcategories", response_model=SubcategoryList)
async def get_subcategories(category_id: str):
    """Get all subcategories for a specific category."""
    try:
        subcategories = await get_category_crud().get_subcategories_by_category(category_id)
        
        return create_success_response(
            data=subcategories,
            message="Subcategories retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting subcategories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{category_id}/with-subcategories", response_model=CategoryResponse)
async def get_category_with_subcategories(category_id: str):
    """Get a category with all its subcategories."""
    try:
        category = await get_category_crud().get_category_with_subcategories(category_id)
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return create_success_response(
            data=category,
            message="Category with subcategories retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category with subcategories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
