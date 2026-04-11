from typing import List, Dict, Any, Optional
from bson import ObjectId
from ...config.database import get_collection
from ...schemas.wishlist import WishlistSchema
from ...core.utils import validate_object_id
import logging

logger = logging.getLogger(__name__)


class WishlistCRUD:
    def __init__(self):
        self.collection = get_collection("wishlist")
        self.products_collection = get_collection("products")
    
    async def add_to_wishlist(self, user_id: str, product_id: str) -> bool:
        """Add product to user's wishlist."""
        try:
            if not validate_object_id(user_id) or not validate_object_id(product_id):
                return False
            
            # Check if product exists
            product = await self.products_collection.find_one({"_id": ObjectId(product_id)})
            if not product:
                return False
            
            # Check if already in wishlist
            existing = await self.collection.find_one({
                "userId": user_id,
                "productId": product_id
            })
            
            if existing:
                return True  # Already in wishlist
            
            # Create wishlist item
            wishlist_item = WishlistSchema(userId=user_id, productId=product_id)
            
            result = await self.collection.insert_one(wishlist_item.to_dict())
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Error adding to wishlist: {e}")
            return False
    
    async def remove_from_wishlist(self, user_id: str, product_id: str) -> bool:
        """Remove product from user's wishlist."""
        try:
            if not validate_object_id(user_id) or not validate_object_id(product_id):
                return False
            
            result = await self.collection.delete_one({
                "userId": user_id,
                "productId": product_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error removing from wishlist: {e}")
            return False
    
    async def get_user_wishlist(self, user_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get user's wishlist with product details."""
        try:
            if not validate_object_id(user_id):
                return {"items": [], "pagination": {}}
            
            # Calculate skip value for pagination
            skip = (page - 1) * limit
            
            # Get total count
            total = await self.collection.count_documents({"userId": user_id})
            
            # Get wishlist items with product details
            pipeline = [
                {"$match": {"userId": user_id}},
                {"$lookup": {
                    "from": "products",
                    "localField": "productId",
                    "foreignField": "_id",
                    "as": "product"
                }},
                {"$unwind": "$product"},
                {"$project": {
                    "_id": 1,
                    "productId": 1,
                    "addedAt": 1,
                    "product": {
                        "id": "$product._id",
                        "name": "$product.name",
                        "price": "$product.price",
                        "images": "$product.images",
                        "category": "$product.category",
                        "material": "$product.material"
                    }
                }},
                {"$sort": {"addedAt": -1}},
                {"$skip": skip},
                {"$limit": limit}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            items = []
            
            async for item in cursor:
                item["id"] = str(item.pop("_id"))
                if "product" in item and "_id" in item["product"]:
                    item["product"]["id"] = str(item["product"].pop("_id"))
                items.append(item)
            
            # Create pagination info
            total_pages = (total + limit - 1) // limit
            pagination = {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            }
            
            return {
                "items": items,
                "pagination": pagination
            }
            
        except Exception as e:
            logger.error(f"Error getting user wishlist: {e}")
            return {"items": [], "pagination": {}}
    
    async def check_in_wishlist(self, user_id: str, product_id: str) -> bool:
        """Check if product is in user's wishlist."""
        try:
            if not validate_object_id(user_id) or not validate_object_id(product_id):
                return False
            
            item = await self.collection.find_one({
                "userId": user_id,
                "productId": product_id
            })
            
            return item is not None
            
        except Exception as e:
            logger.error(f"Error checking wishlist: {e}")
            return False
    
    async def get_wishlist_count(self, user_id: str) -> int:
        """Get total number of items in user's wishlist."""
        try:
            if not validate_object_id(user_id):
                return 0
            
            count = await self.collection.count_documents({"userId": user_id})
            return count
            
        except Exception as e:
            logger.error(f"Error getting wishlist count: {e}")
            return 0
    
    async def clear_wishlist(self, user_id: str) -> bool:
        """Clear user's entire wishlist."""
        try:
            if not validate_object_id(user_id):
                return False
            
            result = await self.collection.delete_many({"userId": user_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error clearing wishlist: {e}")
            return False


# Create instance - will be initialized when database connects
wishlist_crud = None

def get_wishlist_crud():
    global wishlist_crud
    if wishlist_crud is None:
        wishlist_crud = WishlistCRUD()
    return wishlist_crud
