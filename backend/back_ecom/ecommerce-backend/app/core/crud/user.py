from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from ...config.database import get_database
import logging

logger = logging.getLogger(__name__)


class UserCRUD:
    def __init__(self):
        self.db = get_database()
        self.collection: AsyncIOMotorCollection = self.db.users

    async def create(self, user_data: Dict[str, Any]) -> str:
        """Create a new user."""
        try:
            result = await self.collection.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    async def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            from bson import ObjectId
            user = await self.collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                user.pop("_id", None)
            return user
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def get_list(self, filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get paginated list of users."""
        try:
            page = filter_params.get("page", 1)
            limit = filter_params.get("limit", 10)
            skip = (page - 1) * limit
            
            # Build filter
            filter_query = {}
            if "search" in filter_params and filter_params["search"]:
                filter_query["$or"] = [
                    {"name": {"$regex": filter_params["search"], "$options": "i"}},
                    {"email": {"$regex": filter_params["search"], "$options": "i"}}
                ]
            if "role" in filter_params and filter_params["role"]:
                filter_query["role"] = filter_params["role"]
            
            # Get total count
            total = await self.collection.count_documents(filter_query)
            
            # Get users
            cursor = self.collection.find(filter_query).skip(skip).limit(limit)
            users = []
            async for user in cursor:
                user["id"] = str(user["_id"])
                user.pop("_id", None)
                # Remove sensitive information
                user.pop("hashedPassword", None)
                users.append(user)
            
            return {
                "items": users,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        except Exception as e:
            logger.error(f"Error getting users list: {e}")
            return {"items": [], "pagination": {"page": 1, "limit": 10, "total": 0, "pages": 0}}

    async def update(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user."""
        try:
            from bson import ObjectId
            result = await self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    async def delete(self, user_id: str) -> bool:
        """Delete user."""
        try:
            from bson import ObjectId
            result = await self.collection.delete_one({"_id": ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            return False


def get_user_crud() -> UserCRUD:
    """Get user CRUD instance."""
    return UserCRUD()
