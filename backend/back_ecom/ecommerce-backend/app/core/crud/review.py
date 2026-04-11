from typing import List, Dict, Any, Optional
from bson import ObjectId
from ...config.database import get_collection
from ...schemas.review import ReviewSchema
from ...core.utils import validate_object_id
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ReviewCRUD:
    def __init__(self):
        self.collection = get_collection("reviews")
        self.products_collection = get_collection("products")
    
    async def create(self, review_data: dict) -> Optional[str]:
        """Create a new review."""
        try:
            # Validate product ID
            if not validate_object_id(review_data["productId"]):
                return None
            
            # Check if product exists
            product = await self.products_collection.find_one({"_id": ObjectId(review_data["productId"])})
            if not product:
                return None
            
            # Create review schema instance
            review = ReviewSchema(
                productId=review_data["productId"],
                userId=review_data["userId"],
                rating=review_data["rating"],
                comment=review_data["comment"],
                userName=review_data["userName"]
            )
            
            result = await self.collection.insert_one(review.to_dict())
            
            # Update product rating and review count
            await self._update_product_stats(review_data["productId"])
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            return None
    
    async def get_by_id(self, review_id: str) -> Optional[Dict[str, Any]]:
        """Get review by ID."""
        try:
            if not validate_object_id(review_id):
                return None
            
            review = await self.collection.find_one({"_id": ObjectId(review_id)})
            if review:
                review["id"] = str(review.pop("_id"))
                return review
            return None
            
        except Exception as e:
            logger.error(f"Error getting review by ID: {e}")
            return None
    
    async def get_by_product(self, product_id: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get reviews for a specific product."""
        try:
            if not validate_object_id(product_id):
                return {"reviews": [], "pagination": {}}
            
            # Calculate skip value for pagination
            skip = (page - 1) * limit
            
            # Get total count
            total = await self.collection.count_documents({"productId": product_id})
            
            # Get reviews
            cursor = self.collection.find({"productId": product_id}).sort([("createdAt", -1)]).skip(skip).limit(limit)
            reviews = []
            
            async for review in cursor:
                review["id"] = str(review.pop("_id"))
                reviews.append(review)
            
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
                "reviews": reviews,
                "pagination": pagination
            }
            
        except Exception as e:
            logger.error(f"Error getting product reviews: {e}")
            return {"reviews": [], "pagination": {}}
    
    async def get_by_user(self, user_id: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get reviews by a specific user."""
        try:
            if not validate_object_id(user_id):
                return {"reviews": [], "pagination": {}}
            
            # Calculate skip value for pagination
            skip = (page - 1) * limit
            
            # Get total count
            total = await self.collection.count_documents({"userId": user_id})
            
            # Get reviews
            cursor = self.collection.find({"userId": user_id}).sort([("createdAt", -1)]).skip(skip).limit(limit)
            reviews = []
            
            async for review in cursor:
                review["id"] = str(review.pop("_id"))
                reviews.append(review)
            
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
                "reviews": reviews,
                "pagination": pagination
            }
            
        except Exception as e:
            logger.error(f"Error getting user reviews: {e}")
            return {"reviews": [], "pagination": {}}
    
    async def update(self, review_id: str, user_id: str, update_data: dict) -> bool:
        """Update review."""
        try:
            if not validate_object_id(review_id):
                return False
            
            # Check if review exists and belongs to user
            review = await self.collection.find_one({
                "_id": ObjectId(review_id),
                "userId": user_id
            })
            
            if not review:
                return False
            
            # Add updated timestamp
            update_data["updatedAt"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": ObjectId(review_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                # Update product rating and review count
                await self._update_product_stats(review["productId"])
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating review: {e}")
            return False
    
    async def delete(self, review_id: str, user_id: str) -> bool:
        """Delete review."""
        try:
            if not validate_object_id(review_id):
                return False
            
            # Check if review exists and belongs to user
            review = await self.collection.find_one({
                "_id": ObjectId(review_id),
                "userId": user_id
            })
            
            if not review:
                return False
            
            result = await self.collection.delete_one({"_id": ObjectId(review_id)})
            
            if result.deleted_count > 0:
                # Update product rating and review count
                await self._update_product_stats(review["productId"])
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting review: {e}")
            return False
    
    async def _update_product_stats(self, product_id: str):
        """Update product rating and review count."""
        try:
            # Calculate average rating
            pipeline = [
                {"$match": {"productId": product_id}},
                {"$group": {
                    "_id": None,
                    "avgRating": {"$avg": "$rating"},
                    "reviewCount": {"$sum": 1}
                }}
            ]
            
            result = list(await self.collection.aggregate(pipeline))
            
            if result:
                avg_rating = round(result[0]["avgRating"], 2)
                review_count = result[0]["reviewCount"]
                
                # Update product
                await self.products_collection.update_one(
                    {"_id": ObjectId(product_id)},
                    {
                        "$set": {
                            "rating": avg_rating,
                            "reviewCount": review_count,
                            "updatedAt": datetime.utcnow()
                        }
                    }
                )
            
        except Exception as e:
            logger.error(f"Error updating product stats: {e}")


# Create instance - will be initialized when database connects
review_crud = None

def get_review_crud():
    global review_crud
    if review_crud is None:
        review_crud = ReviewCRUD()
    return review_crud
