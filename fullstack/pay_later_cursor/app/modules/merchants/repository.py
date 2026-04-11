from typing import Optional, List, Tuple
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.merchants.models import Merchant, MerchantFeeHistory
from app.common.exceptions import MerchantNotFound, DuplicateEntity
from app.common.counters import CounterService, MERCHANT_ID_COUNTER
import structlog

logger = structlog.get_logger(__name__)


class MerchantRepository:
    """Repository for merchant and fee history operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.merchants_collection = database.merchants
        self.fee_history_collection = database.merchant_fee_history
        self.counter_service = CounterService(database)
    
    async def create_merchant(self, merchant: Merchant) -> Merchant:
        """Create a new merchant with auto-increment ID."""
        try:
            # Generate auto-increment merchant ID
            custom_merchant_id = await self.counter_service.get_next_id(MERCHANT_ID_COUNTER)
            merchant.custom_merchant_id = custom_merchant_id
            
            merchant_dict = merchant.to_dict()
            await self.merchants_collection.insert_one(merchant_dict)
            logger.info("Merchant created", merchant_id=str(merchant._id), custom_merchant_id=custom_merchant_id, name=merchant.name)
            return merchant
        except Exception as e:
            if "duplicate key" in str(e).lower() and "name" in str(e).lower():
                raise DuplicateEntity("Merchant", "name", merchant.name)
            raise
    
    async def get_merchant_by_id(self, merchant_id: ObjectId) -> Optional[Merchant]:
        """Get merchant by ID."""
        merchant_data = await self.merchants_collection.find_one({"_id": merchant_id})
        if merchant_data:
            return Merchant.from_dict(merchant_data)
        return None
    
    async def get_merchant_by_custom_id(self, custom_merchant_id: int) -> Optional[Merchant]:
        """Get merchant by custom auto-increment ID."""
        merchant_data = await self.merchants_collection.find_one({"custom_merchant_id": custom_merchant_id})
        if merchant_data:
            return Merchant.from_dict(merchant_data)
        return None
    
    async def get_merchant_by_name(self, name: str) -> Optional[Merchant]:
        """Get merchant by name."""
        merchant_data = await self.merchants_collection.find_one({"name": name})
        if merchant_data:
            return Merchant.from_dict(merchant_data)
        return None

    async def get_merchant_by_email(self, email: str) -> Optional[Merchant]:
        """Get merchant by email address."""
        merchant_data = await self.merchants_collection.find_one({"email": email})
        if merchant_data:
            return Merchant.from_dict(merchant_data)
        return None
    
    async def get_all_merchants(
        self,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[Merchant], int]:
        """Get all merchants with pagination."""
        skip = (page - 1) * size
        
        # Get total count
        total = await self.merchants_collection.count_documents({})
        
        # Get paginated results
        cursor = self.merchants_collection.find({}).sort(
            "created_at", -1
        ).skip(skip).limit(size)
        
        merchants = []
        async for doc in cursor:
            merchant = Merchant.from_dict(doc)
            merchants.append(merchant)
        
        return merchants, total
    
    async def update_merchant_fee(
        self, 
        merchant_id: ObjectId, 
        new_fee_pct: float
    ) -> Optional[Merchant]:
        """Update merchant fee percentage."""
        update_data = {
            "current_fee_pct": new_fee_pct,
            "updated_at": datetime.utcnow()
        }
        
        result = await self.merchants_collection.find_one_and_update(
            {"_id": merchant_id},
            {"$set": update_data},
            return_document=True
        )
        
        if result:
            return Merchant.from_dict(result)
        return None
    
    async def create_fee_history_entry(self, entry: MerchantFeeHistory) -> MerchantFeeHistory:
        """Create a new fee history entry."""
        entry_dict = entry.to_dict()
        await self.fee_history_collection.insert_one(entry_dict)
        logger.info("Fee history entry created", 
                   merchant_id=str(entry.merchant_id), 
                   fee_pct=entry.fee_pct)
        return entry
    
    async def get_fee_history(
        self, 
        merchant_id: ObjectId,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[MerchantFeeHistory], int]:
        """Get fee history for a merchant with pagination and date filtering."""
        skip = (page - 1) * size
        
        # Build filter
        filter_query = {"merchant_id": merchant_id}
        
        if from_date or to_date:
            date_filter = {}
            if from_date:
                date_filter["$gte"] = from_date
            if to_date:
                date_filter["$lte"] = to_date
            filter_query["effective_from"] = date_filter
        
        # Get total count
        total = await self.fee_history_collection.count_documents(filter_query)
        
        # Get paginated results
        cursor = self.fee_history_collection.find(filter_query).sort(
            "effective_from", -1
        ).skip(skip).limit(size)
        
        entries = []
        async for doc in cursor:
            entry = MerchantFeeHistory.from_dict(doc)
            entries.append(entry)
        
        return entries, total
    
    async def get_current_fee(self, merchant_id: ObjectId) -> Optional[float]:
        """Get current fee percentage for a merchant."""
        merchant = await self.get_merchant_by_id(merchant_id)
        return merchant.current_fee_pct if merchant else None
    
    async def get_merchants_with_fees(self) -> List[dict]:
        """Get all merchants with their current fees."""
        pipeline = [
            {
                "$project": {
                    "merchant_id": "$_id",
                    "name": 1,
                    "current_fee_pct": 1
                }
            }
        ]
        
        cursor = self.merchants_collection.aggregate(pipeline)
        merchants = []
        async for doc in cursor:
            merchants.append(doc)
        
        return merchants
