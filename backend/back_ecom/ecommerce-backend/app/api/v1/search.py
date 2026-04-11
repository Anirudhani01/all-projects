from fastapi import APIRouter, HTTPException, status, Query
from typing import Optional
from ...core.crud.product import get_product_crud
from ...core.utils import create_success_response, create_error_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("/")
async def global_search(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(12, ge=1, le=50, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category"),
    material: Optional[str] = Query(None, description="Filter by material"),
    price_min: Optional[float] = Query(None, ge=0, description="Minimum price"),
    price_max: Optional[float] = Query(None, ge=0, description="Maximum price"),
    sort: str = Query("relevance", description="Sort field"),
    order: str = Query("desc", description="Sort order")
):
    """Global search across all products."""
    try:
        # Map relevance sort to text score for MongoDB text search
        if sort == "relevance":
            sort = "createdAt"  # Default sort for text search
        
        result = await get_product_crud().get_list(
            page=page,
            limit=limit,
            search=q,
            category=category,
            material=material,
            price_min=price_min,
            price_max=price_max,
            sort=sort,
            order=order
        )
        
        return create_success_response(
            data=result,
            message="Search completed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error performing search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform search"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Number of suggestions")
):
    """Get search suggestions based on partial query."""
    try:
        # Get products that match the partial query
        result = await get_product_crud().get_list(
            page=1,
            limit=limit,
            search=q
        )
        
        # Extract suggestions from product names and categories
        suggestions = []
        seen = set()
        
        for product in result.get("items", []):
            # Add product name suggestions
            name = product.get("name", "").lower()
            if q.lower() in name and name not in seen:
                suggestions.append({
                    "type": "product",
                    "text": product["name"],
                    "id": product["id"]
                })
                seen.add(name)
            
            # Add category suggestions
            category = product.get("category", "").lower()
            if q.lower() in category and category not in seen:
                suggestions.append({
                    "type": "category",
                    "text": product["category"]
                })
                seen.add(category)
            
            # Add material suggestions
            material = product.get("material", "").lower()
            if q.lower() in material and material not in seen:
                suggestions.append({
                    "type": "material",
                    "text": product["material"]
                })
                seen.add(material)
            
            if len(suggestions) >= limit:
                break
        
        return create_success_response(
            data=suggestions,
            message="Search suggestions retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search suggestions"
        )


@router.get("/trending")
async def get_trending_searches(
    limit: int = Query(10, ge=1, le=20, description="Number of trending searches")
):
    """Get trending search terms (placeholder for future analytics)."""
    try:
        # For now, return popular categories and materials
        # In the future, this could be based on actual search analytics
        categories = await get_product_crud().get_categories()
        materials = await get_product_crud().get_materials()
        
        trending = []
        
        # Add top categories
        for category in categories[:limit//2]:
            trending.append({
                "type": "category",
                "text": category,
                "count": 0  # Placeholder for actual analytics
            })
        
        # Add top materials
        for material in materials[:limit//2]:
            trending.append({
                "type": "material",
                "text": material,
                "count": 0  # Placeholder for actual analytics
            })
        
        return create_success_response(
            data=trending[:limit],
            message="Trending searches retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting trending searches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending searches"
        )


@router.get("/filters")
async def get_search_filters():
    """Get available search filters."""
    try:
        # Get all available filter options
        categories = await get_product_crud().get_categories()
        materials = await get_product_crud().get_materials()
        sizes = await get_product_crud().get_sizes()
        colors = await get_product_crud().get_colors()
        
        filters = {
            "categories": categories,
            "materials": materials,
            "sizes": sizes,
            "colors": colors,
            "price_range": {
                "min": 0,  # Placeholder - could be calculated from actual data
                "max": 1000  # Placeholder - could be calculated from actual data
            }
        }
        
        return create_success_response(
            data=filters,
            message="Search filters retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting search filters: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search filters"
        )
