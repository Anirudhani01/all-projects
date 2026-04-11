from typing import List, Optional, Dict, Any
from bson import ObjectId
from ...config.database import get_collection
from ...schemas.category import CategorySchema, SubcategorySchema
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CategoryCRUD:
    def __init__(self):
        self.collection = get_collection("categories")
        self.subcategory_collection = get_collection("subcategories")
    
    async def create_category(self, category_data: dict) -> Optional[str]:
        """Create a new category."""
        try:
            # Check if category with same slug already exists
            existing_category = await self.collection.find_one({"slug": category_data["slug"]})
            if existing_category:
                logger.warning(f"Category with slug '{category_data['slug']}' already exists")
                return None
            
            # Create category schema instance
            category = CategorySchema(
                name=category_data["name"],
                slug=category_data["slug"],
                description=category_data.get("description"),
                image=category_data.get("image"),
                icon=category_data.get("icon"),
                isActive=category_data.get("isActive", True),
                isFeatured=category_data.get("isFeatured", False),
                sortOrder=category_data.get("sortOrder", 0)
            )
            
            result = await self.collection.insert_one(category.to_dict())
            logger.info(f"Created category: {category_data['name']} with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return None
    
    async def get_category_by_id(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category by ID."""
        try:
            from ...core.utils import validate_object_id
            if not validate_object_id(category_id):
                return None
            
            category = await self.collection.find_one({"_id": ObjectId(category_id)})
            if category:
                return self.format_category_response(category)
            return None
            
        except Exception as e:
            logger.error(f"Error getting category by ID: {e}")
            return None
    
    async def get_category_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get category by slug."""
        try:
            category = await self.collection.find_one({"slug": slug})
            if category:
                return self.format_category_response(category)
            return None
            
        except Exception as e:
            logger.error(f"Error getting category by slug: {e}")
            return None
    
    async def get_all_categories(self, filter_params: dict = None) -> List[Dict[str, Any]]:
        """Get all categories with optional filtering."""
        try:
            filter_query = {}
            
            if filter_params:
                if filter_params.get("isActive") is not None:
                    filter_query["isActive"] = filter_params["isActive"]
                if filter_params.get("isFeatured") is not None:
                    filter_query["isFeatured"] = filter_params["isFeatured"]
                if filter_params.get("search"):
                    filter_query["$text"] = {"$search": filter_params["search"]}
            
            # Build sort query
            sort_field = filter_params.get("sortBy", "sortOrder") if filter_params else "sortOrder"
            sort_order = 1 if (filter_params and filter_params.get("sortOrder") == "asc") else -1
            
            cursor = self.collection.find(filter_query).sort(sort_field, sort_order)
            categories = []
            
            async for category in cursor:
                categories.append(self.format_category_response(category))
            
            return categories
            
        except Exception as e:
            logger.error(f"Error getting all categories: {e}")
            return []
    
    def format_category_response(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format category data for API response."""
        formatted_data = category_data.copy()
        
        # Convert _id to id
        if "_id" in formatted_data:
            formatted_data["id"] = str(formatted_data["_id"])
        
        # Ensure required fields are present
        if "createdAt" not in formatted_data:
            formatted_data["createdAt"] = datetime.utcnow()
        elif hasattr(formatted_data["createdAt"], 'isoformat'):
            formatted_data["createdAt"] = formatted_data["createdAt"].isoformat()
        
        if "updatedAt" not in formatted_data:
            formatted_data["updatedAt"] = datetime.utcnow()
        elif hasattr(formatted_data["updatedAt"], 'isoformat'):
            formatted_data["updatedAt"] = formatted_data["updatedAt"].isoformat()
        
        return formatted_data
    
    async def update_category(self, category_id: str, update_data: dict) -> bool:
        """Update category."""
        try:
            from ...core.utils import validate_object_id
            if not validate_object_id(category_id):
                return False
            
            # Check if slug is being updated and if it conflicts with existing
            if "slug" in update_data:
                existing_category = await self.collection.find_one({
                    "slug": update_data["slug"],
                    "_id": {"$ne": ObjectId(category_id)}
                })
                if existing_category:
                    logger.warning(f"Category with slug '{update_data['slug']}' already exists")
                    return False
            
            # Add updated timestamp
            update_data["updatedAt"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(category_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated category: {category_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error updating category: {e}")
            return False
    
    async def delete_category(self, category_id: str) -> bool:
        """Delete category and all its subcategories."""
        try:
            from ...core.utils import validate_object_id
            if not validate_object_id(category_id):
                return False
            
            # Check if category has products
            from ...core.crud.product import get_product_crud
            product_count = await get_product_crud().count_by_category(category_id)
            
            if product_count > 0:
                logger.warning(f"Cannot delete category {category_id} - it has {product_count} products")
                return False
            
            # Delete all subcategories first
            await self.subcategory_collection.delete_many({"categoryId": category_id})
            
            # Delete the category
            result = await self.collection.delete_one({"_id": ObjectId(category_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted category: {category_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting category: {e}")
            return False
    
    async def create_subcategory(self, subcategory_data: dict) -> Optional[str]:
        """Create a new subcategory."""
        try:
            # Check if subcategory with same slug already exists in this category
            existing_subcategory = await self.subcategory_collection.find_one({
                "slug": subcategory_data["slug"],
                "categoryId": subcategory_data["categoryId"]
            })
            if existing_subcategory:
                logger.warning(f"Subcategory with slug '{subcategory_data['slug']}' already exists in category")
                return None
            
            # Verify category exists
            category = await self.collection.find_one({"_id": ObjectId(subcategory_data["categoryId"])})
            if not category:
                logger.error(f"Category {subcategory_data['categoryId']} not found")
                return None
            
            # Create subcategory schema instance
            subcategory = SubcategorySchema(
                name=subcategory_data["name"],
                slug=subcategory_data["slug"],
                categoryId=subcategory_data["categoryId"],
                description=subcategory_data.get("description"),
                isActive=subcategory_data.get("isActive", True)
            )
            
            result = await self.subcategory_collection.insert_one(subcategory.to_dict())
            logger.info(f"Created subcategory: {subcategory_data['name']} with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating subcategory: {e}")
            return None
    
    async def get_subcategories_by_category(self, category_id: str) -> List[Dict[str, Any]]:
        """Get all subcategories for a specific category."""
        try:
            from ...core.utils import validate_object_id
            if not validate_object_id(category_id):
                return []
            
            cursor = self.subcategory_collection.find({"categoryId": category_id, "isActive": True})
            subcategories = []
            
            async for subcategory in cursor:
                subcategories.append(self.format_subcategory_response(subcategory))
            
            return subcategories
            
        except Exception as e:
            logger.error(f"Error getting subcategories by category: {e}")
            return []
    
    async def get_category_with_subcategories(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get category with populated subcategories."""
        try:
            category = await self.get_category_by_id(category_id)
            if not category:
                return None
            
            # Get subcategories
            subcategories = await self.get_subcategories_by_category(category_id)
            category["subcategories"] = subcategories
            
            return category
            
        except Exception as e:
            logger.error(f"Error getting category with subcategories: {e}")
            return None
    
    async def update_product_count(self, category_id: str, increment: bool = True) -> bool:
        """Update product count for a category."""
        try:
            from ...core.utils import validate_object_id
            if not validate_object_id(category_id):
                return False
            
            update_operation = "$inc" if increment else "$dec"
            result = await self.collection.update_one(
                {"_id": ObjectId(category_id)},
                {update_operation: {"productCount": 1}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating product count: {e}")
            return False
    
    def format_subcategory_response(self, subcategory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format subcategory data for API response."""
        formatted_data = subcategory_data.copy()
        
        # Convert _id to id
        if "_id" in formatted_data:
            formatted_data["id"] = str(formatted_data["_id"])
        
        # Ensure required fields are present
        if "createdAt" not in formatted_data:
            formatted_data["createdAt"] = datetime.utcnow()
        elif hasattr(formatted_data["createdAt"], 'isoformat'):
            formatted_data["createdAt"] = formatted_data["createdAt"].isoformat()
        
        if "updatedAt" not in formatted_data:
            formatted_data["updatedAt"] = datetime.utcnow()
        elif hasattr(formatted_data["updatedAt"], 'isoformat'):
            formatted_data["updatedAt"] = formatted_data["updatedAt"].isoformat()
        
        return formatted_data


# Create instance - will be initialized when database connects
category_crud = None

def get_category_crud():
    global category_crud
    if category_crud is None:
        category_crud = CategoryCRUD()
    return category_crud
