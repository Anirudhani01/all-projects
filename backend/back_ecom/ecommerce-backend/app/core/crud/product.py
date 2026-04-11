from typing import List, Dict, Any, Optional
from bson import ObjectId
from ...config.database import get_collection
from ...schemas.product import ProductSchema, ColorSchema
from ...core.utils import (
    create_pagination_info, 
    build_product_filter, 
    build_sort_query,
    format_product_response,
    validate_object_id
)
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ProductCRUD:
    def __init__(self):
        self.collection = get_collection("products")
    
    async def create(self, product_data: dict) -> Optional[str]:
        """Create a new product."""
        try:
            # Create product schema instance
            product = ProductSchema(
                name=product_data["name"],
                description=product_data["description"],
                price=product_data["price"],
                material=product_data["material"],
                category=product_data["category"],
                images=product_data["images"],
                colors=[ColorSchema(**color) for color in product_data["colors"]],
                sizes=product_data["sizes"],
                originalPrice=product_data.get("originalPrice"),
                discount=product_data.get("discount"),
                availableSizes=product_data.get("availableSizes"),
                care=product_data.get("care"),
                features=product_data.get("features"),
                tags=product_data.get("tags"),
                isFeatured=product_data.get("isFeatured", False)
            )
            
            result = await self.collection.insert_one(product.to_dict())
            
            # Update category product count
            if result.inserted_id:
                await self.update_category_product_count(product_data["category"], increment=True)
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating product: {e}")
            return None
    
    async def get_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID."""
        try:
            if not validate_object_id(product_id):
                return None
            
            product = await self.collection.find_one({"_id": ObjectId(product_id)})
            if product:
                return format_product_response(product)
            return None
            
        except Exception as e:
            logger.error(f"Error getting product by ID: {e}")
            return None
    
    async def get_list(
        self,
        page: int = 1,
        limit: int = 12,
        search: Optional[str] = None,
        category: Optional[str] = None,
        material: Optional[str] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        sort: str = "createdAt",
        order: str = "desc",
        featured: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Get paginated list of products with filters."""
        try:
            # Build filter query
            filter_query = build_product_filter(
                search=search,
                category=category,
                material=material,
                size=size,
                color=color,
                price_min=price_min,
                price_max=price_max,
                featured=featured
            )
            
            # Build sort query
            sort_query = build_sort_query(sort, order)
            
            # Calculate skip value for pagination
            skip = (page - 1) * limit
            
            # Get total count
            total = await self.collection.count_documents(filter_query)
            
            # Get products
            cursor = self.collection.find(filter_query).sort(sort_query).skip(skip).limit(limit)
            products = []
            
            async for product in cursor:
                products.append(format_product_response(product))
            
            # Create pagination info
            pagination = create_pagination_info(page, limit, total)
            
            return {
                "items": products,
                "pagination": pagination,
                "filters": {
                    "applied": {
                        "search": search,
                        "category": category,
                        "material": material,
                        "size": size,
                        "color": color,
                        "price_min": price_min,
                        "price_max": price_max,
                        "featured": featured
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting product list: {e}")
            return {"items": [], "pagination": {}, "filters": {}}
    
    async def get_featured(self, limit: int = 8) -> List[Dict[str, Any]]:
        """Get featured products."""
        try:
            cursor = self.collection.find({"isFeatured": True}).limit(limit)
            products = []
            
            async for product in cursor:
                products.append(format_product_response(product))
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting featured products: {e}")
            return []
    
    async def get_related(self, product_id: str, category: str, limit: int = 4) -> List[Dict[str, Any]]:
        """Get related products by category."""
        try:
            if not validate_object_id(product_id):
                return []
            
            cursor = self.collection.find({
                "category": category,
                "_id": {"$ne": ObjectId(product_id)}
            }).limit(limit)
            
            products = []
            async for product in cursor:
                products.append(format_product_response(product))
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting related products: {e}")
            return []
    
    async def update(self, product_id: str, update_data: dict) -> bool:
        """Update product."""
        try:
            if not validate_object_id(product_id):
                return False
            
            # Add updated timestamp
            update_data["updatedAt"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return False
    
    async def delete(self, product_id: str) -> bool:
        """Delete product."""
        try:
            if not validate_object_id(product_id):
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(product_id)})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False
    
    async def get_categories(self) -> List[str]:
        """Get unique product categories."""
        try:
            categories = await self.collection.distinct("category")
            return sorted(categories)
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    async def get_materials(self) -> List[str]:
        """Get unique product materials."""
        try:
            materials = await self.collection.distinct("material")
            return sorted(materials)
            
        except Exception as e:
            logger.error(f"Error getting materials: {e}")
            return []
    
    async def get_sizes(self) -> List[str]:
        """Get unique product sizes."""
        try:
            sizes = await self.collection.distinct("sizes")
            # Flatten the list of size lists
            all_sizes = set()
            for size_list in sizes:
                if isinstance(size_list, list):
                    all_sizes.update(size_list)
                else:
                    all_sizes.add(size_list)
            
            return sorted(list(all_sizes))
            
        except Exception as e:
            logger.error(f"Error getting sizes: {e}")
            return []
    
    async def get_colors(self) -> List[str]:
        """Get unique product colors."""
        try:
            colors = await self.collection.distinct("colors.name")
            return sorted(colors)
            
        except Exception as e:
            logger.error(f"Error getting colors: {e}")
            return []
    
    async def count_by_category(self, category_id: str) -> int:
        """Count products in a specific category."""
        try:
            if not validate_object_id(category_id):
                return 0
            
            # First get the category to find its slug
            from ...core.crud.category import get_category_crud
            category = await get_category_crud().get_category_by_id(category_id)
            if not category:
                return 0
            
            # Count products with this category slug
            count = await self.collection.count_documents({"category": category["slug"]})
            return count
            
        except Exception as e:
            logger.error(f"Error counting products by category: {e}")
            return 0
    
    async def update_category_product_count(self, category_slug: str, increment: bool = True) -> bool:
        """Update product count for a category by slug."""
        try:
            from ...core.crud.category import get_category_crud
            
            # Find category by slug
            category = await get_category_crud().get_category_by_slug(category_slug)
            if not category:
                logger.warning(f"Category with slug '{category_slug}' not found")
                return False
            
            # Update product count
            success = await get_category_crud().update_product_count(category["id"], increment)
            return success
            
        except Exception as e:
            logger.error(f"Error updating category product count: {e}")
            return False


# Create instance - will be initialized when database connects
product_crud = None

def get_product_crud():
    global product_crud
    if product_crud is None:
        product_crud = ProductCRUD()
    return product_crud
