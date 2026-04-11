from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from app.modules.transactions.models import Transaction, IdempotencyKey
from app.common.exceptions import DuplicateRequest
from app.common.types import TransactionType, TransactionStatus
import structlog

logger = structlog.get_logger(__name__)


class TransactionRepository:
    """Repository for transaction operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.transactions_collection = database.transactions
        self.idempotency_keys_collection = database.idempotency_keys
    
    async def create_transaction(
        self, 
        transaction: Transaction,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> Transaction:
        """Create a new transaction."""
        try:
            transaction_dict = transaction.to_dict()
            
            if session:
                await self.transactions_collection.insert_one(transaction_dict, session=session)
            else:
                await self.transactions_collection.insert_one(transaction_dict)
            
            logger.info("Transaction created", 
                       transaction_id=str(transaction._id),
                       type=transaction.type.value,
                       user_id=str(transaction.user_id),
                       amount=transaction.amount,
                       status=transaction.status.value)
            
            return transaction
            
        except Exception as e:
            if "duplicate key" in str(e).lower() and "idempotency_key" in str(e).lower():
                raise DuplicateRequest(transaction.idempotency_key or "unknown")
            raise
    
    async def get_transaction_by_id(
        self, 
        transaction_id: ObjectId
    ) -> Optional[Transaction]:
        """Get transaction by ID."""
        transaction_data = await self.transactions_collection.find_one({"_id": transaction_id})
        if transaction_data:
            return Transaction.from_dict(transaction_data)
        return None
    
    async def get_transactions_by_user(
        self,
        user_id: ObjectId,
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[Transaction], int]:
        """Get transactions for a user with pagination."""
        skip = (page - 1) * size
        
        # Get total count
        total = await self.transactions_collection.count_documents({"user_id": user_id})
        
        # Get paginated results
        cursor = self.transactions_collection.find({"user_id": user_id}).sort(
            "created_at", -1
        ).skip(skip).limit(size)
        
        transactions = []
        async for doc in cursor:
            transaction = Transaction.from_dict(doc)
            transactions.append(transaction)
        
        return transactions, total
    
    async def get_transactions_with_filters(
        self,
        filters: Dict[str, Any],
        page: int = 1,
        size: int = 10
    ) -> Tuple[List[Transaction], int]:
        """Get transactions with filters and pagination."""
        skip = (page - 1) * size
        
        # Build filter query
        filter_query = {}
        
        if filters.get("user_id"):
            try:
                filter_query["user_id"] = ObjectId(filters["user_id"])
            except Exception:
                return [], 0
        
        if filters.get("merchant_id"):
            try:
                filter_query["merchant_id"] = ObjectId(filters["merchant_id"])
            except Exception:
                return [], 0
        
        if filters.get("type"):
            filter_query["type"] = filters["type"]
        
        if filters.get("status"):
            filter_query["status"] = filters["status"]
        
        if filters.get("from_date") or filters.get("to_date"):
            date_filter = {}
            if filters.get("from_date"):
                date_filter["$gte"] = filters["from_date"]
            if filters.get("to_date"):
                date_filter["$lte"] = filters["to_date"]
            filter_query["created_at"] = date_filter
        
        # Get total count
        total = await self.transactions_collection.count_documents(filter_query)
        
        # Get paginated results
        cursor = self.transactions_collection.find(filter_query).sort(
            "created_at", -1
        ).skip(skip).limit(size)
        
        transactions = []
        async for doc in cursor:
            transaction = Transaction.from_dict(doc)
            transactions.append(transaction)
        
        return transactions, total
    
    async def check_idempotency_key(
        self, 
        scope: str, 
        key: str
    ) -> Optional[Dict[str, Any]]:
        """Check if idempotency key exists and return cached response."""
        if not key:
            return None
        
        doc = await self.idempotency_keys_collection.find_one(
            {"scope": scope, "key": key},
            {"response_hash": 1}
        )
        
        return doc.get("response_hash") if doc else None
    
    async def create_idempotency_key(
        self, 
        idempotency_key: IdempotencyKey,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> IdempotencyKey:
        """Create an idempotency key."""
        try:
            key_dict = idempotency_key.to_dict()
            
            if session:
                await self.idempotency_keys_collection.insert_one(key_dict, session=session)
            else:
                await self.idempotency_keys_collection.insert_one(key_dict)
            
            logger.info("Idempotency key created", 
                       scope=idempotency_key.scope,
                       key=idempotency_key.key)
            
            return idempotency_key
            
        except Exception as e:
            if "duplicate key" in str(e).lower():
                raise DuplicateRequest(idempotency_key.key)
            raise
    
    async def get_transaction_summary(
        self,
        user_id: Optional[ObjectId] = None,
        merchant_id: Optional[ObjectId] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get transaction summary statistics."""
        # Build match stage
        match_stage = {}
        
        if user_id:
            match_stage["user_id"] = user_id
        
        if merchant_id:
            match_stage["merchant_id"] = merchant_id
        
        if from_date or to_date:
            date_filter = {}
            if from_date:
                date_filter["$gte"] = from_date
            if to_date:
                date_filter["$lte"] = to_date
            match_stage["created_at"] = date_filter
        
        pipeline = []
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "total_transactions": {"$sum": 1},
                    "total_amount": {"$sum": "$amount"},
                    "total_fees": {"$sum": {"$ifNull": ["$fee_amount", 0]}},
                    "purchase_count": {
                        "$sum": {"$cond": [{"$eq": ["$type", "PURCHASE"]}, 1, 0]}
                    },
                    "payment_count": {
                        "$sum": {"$cond": [{"$eq": ["$type", "PAYMENT"]}, 1, 0]}
                    },
                    "approved_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "APPROVED"]}, 1, 0]}
                    },
                    "rejected_count": {
                        "$sum": {"$cond": [{"$eq": ["$status", "REJECTED"]}, 1, 0]}
                    }
                }
            }
        ])
        
        cursor = self.transactions_collection.aggregate(pipeline)
        result = await cursor.next()
        
        if result:
            return {
                "total_transactions": result["total_transactions"],
                "total_amount": result["total_amount"],
                "total_fees": result["total_fees"],
                "purchase_count": result["purchase_count"],
                "payment_count": result["payment_count"],
                "approved_count": result["approved_count"],
                "rejected_count": result["rejected_count"]
            }
        
        return {
            "total_transactions": 0,
            "total_amount": 0.0,
            "total_fees": 0.0,
            "purchase_count": 0,
            "payment_count": 0,
            "approved_count": 0,
            "rejected_count": 0
        }
    
    async def get_user_transaction_history(
        self,
        user_id: ObjectId,
        limit: int = 10
    ) -> List[Transaction]:
        """Get recent transaction history for a user."""
        cursor = self.transactions_collection.find({"user_id": user_id}).sort(
            "created_at", -1
        ).limit(limit)
        
        transactions = []
        async for doc in cursor:
            transaction = Transaction.from_dict(doc)
            transactions.append(transaction)
        
        return transactions
