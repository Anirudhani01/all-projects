from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from ...models.product import ProductCreate, ProductUpdate, ProductFilter
from ...core.crud.product import get_product_crud
from ...core.utils import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("/")
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=50, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    material: Optional[str] = Query(None, description="Filter by material"),
    size: Optional[str] = Query(None, description="Filter by size"),
    color: Optional[str] = Query(None, description="Filter by color"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort: str = Query("createdAt", description="Sort field"),
    order: str = Query("desc", description="Sort order"),
    featured: Optional[bool] = Query(None, description="Filter featured products")
):
    """Get paginated list of products with filters."""
    try:
        result = await get_product_crud().get_list(
            page=page,
            limit=limit,
            search=search,
            category=category,
            material=material,
            size=size,
            color=color,
            price_min=price_min,
            price_max=price_max,
            sort=sort,
            order=order,
            featured=featured
        )
        
        return create_success_response(
            data=result,
            message="Products retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve products"
        )


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get product by ID."""
    try:
        product = await get_product_crud().get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return create_success_response(
            data=product,
            message="Product retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve product"
        )


@router.get("/featured")
async def get_featured_products(
    limit: int = Query(8, ge=1, le=20, description="Number of featured products")
):
    """Get featured products."""
    try:
        products = await get_product_crud().get_featured(limit=limit)
        
        return create_success_response(
            data=products,
            message="Featured products retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting featured products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve featured products"
        )


@router.get("/related/{product_id}")
async def get_related_products(
    product_id: str,
    limit: int = Query(4, ge=1, le=10, description="Number of related products")
):
    """Get related products by category."""
    try:
        # Get the product to find its category
        product = await get_product_crud().get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        related_products = await get_product_crud().get_related(
            product_id=product_id,
            category=product["category"],
            limit=limit
        )
        
        return create_success_response(
            data=related_products,
            message="Related products retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting related products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve related products"
        )


@router.post("/", response_model=dict)
async def create_product(
    product_data: ProductCreate
):
    """Create a new product."""
    try:
        product_id = await get_product_crud().create(product_data.dict())
        if not product_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create product"
            )
        
        return create_success_response(
            data={"id": product_id},
            message="Product created successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create product"
        )


@router.put("/{product_id}")
async def update_product(
    product_id: str,
    product_update: ProductUpdate
):
    """Update product."""
    try:
        # Check if product exists
        existing_product = await get_product_crud().get_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        success = await get_product_crud().update(product_id, product_update.dict(exclude_unset=True))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update product"
            )
        
        return create_success_response(
            data=None,
            message="Product updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update product"
        )


@router.delete("/{product_id}")
async def delete_product(
    product_id: str
):
    """Delete product."""
    try:
        # Check if product exists
        existing_product = await get_product_crud().get_by_id(product_id)
        if not existing_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        success = await get_product_crud().delete(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete product"
            )
        
        return create_success_response(
            data=None,
            message="Product deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting product: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete product"
        )


@router.get("/categories")
async def get_categories():
    """Get unique product categories."""
    try:
        categories = await get_product_crud().get_categories()
        
        return create_success_response(
            data=categories,
            message="Categories retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve categories"
        )


@router.get("/materials")
async def get_materials():
    """Get unique product materials."""
    try:
        materials = await get_product_crud().get_materials()
        
        return create_success_response(
            data=materials,
            message="Materials retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting materials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve materials"
        )


@router.get("/sizes")
async def get_sizes():
    """Get unique product sizes."""
    try:
        sizes = await get_product_crud().get_sizes()
        
        return create_success_response(
            data=sizes,
            message="Sizes retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting sizes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sizes"
        )


@router.get("/colors")
async def get_colors():
    """Get unique product colors."""
    try:
        colors = await get_product_crud().get_colors()
        
        return create_success_response(
            data=colors,
            message="Colors retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting colors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve colors"
        )
