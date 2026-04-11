from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from ...config.database import get_database
import logging

logger = logging.getLogger(__name__)


class OrderCRUD:
    def __init__(self):
        self.db = get_database()
        self.collection: AsyncIOMotorCollection = self.db.orders

    async def create(self, order_data: Dict[str, Any]) -> str:
        """Create a new order."""
        try:
            result = await self.collection.insert_one(order_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None

    async def get_by_id(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Get order by ID."""
        try:
            from bson import ObjectId
            order = await self.collection.find_one({"_id": ObjectId(order_id)})
            if order:
                order["id"] = str(order["_id"])
                order.pop("_id", None)
            return order
        except Exception as e:
            logger.error(f"Error getting order: {e}")
            return None

    async def get_list(self, filter_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get paginated list of orders."""
        try:
            page = filter_params.get("page", 1)
            limit = filter_params.get("limit", 10)
            skip = (page - 1) * limit
            
            # Build filter
            filter_query = {}
            if "status" in filter_params and filter_params["status"]:
                filter_query["status"] = filter_params["status"]
            
            # Get total count
            total = await self.collection.count_documents(filter_query)
            
            # Get orders
            cursor = self.collection.find(filter_query).skip(skip).limit(limit)
            orders = []
            async for order in cursor:
                order["id"] = str(order["_id"])
                order.pop("_id", None)
                orders.append(order)
            
            return {
                "items": orders,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "pages": (total + limit - 1) // limit
                }
            }
        except Exception as e:
            logger.error(f"Error getting orders list: {e}")
            return {"items": [], "pagination": {"page": 1, "limit": 10, "total": 0, "pages": 0}}

    async def update(self, order_id: str, update_data: Dict[str, Any]) -> bool:
        """Update order."""
        try:
            from bson import ObjectId
            result = await self.collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating order: {e}")
            return False

    async def delete(self, order_id: str) -> bool:
        """Delete order."""
        try:
            from bson import ObjectId
            result = await self.collection.delete_one({"_id": ObjectId(order_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting order: {e}")
            return False


def get_order_crud() -> OrderCRUD:
    """Get order CRUD instance."""
    return OrderCRUD()
