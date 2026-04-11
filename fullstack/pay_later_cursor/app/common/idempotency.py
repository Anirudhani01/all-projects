import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from bson import ObjectId
from app.config.settings import settings
from app.common.exceptions import DuplicateRequest


class IdempotencyService:
    """Service for handling idempotency keys."""
    
    def __init__(self, database):
        self.database = database
        self.collection = database.idempotency_keys
    
    async def check_and_create_key(
        self, 
        scope: str, 
        key: str, 
        response_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if idempotency key exists, create if not.
        Returns True if key was created, False if it already existed.
        """
        if not key:
            return True  # No idempotency key provided
        
        # Calculate TTL
        ttl_expires_at = datetime.utcnow() + timedelta(hours=settings.idempotency_ttl_hours)
        
        # Create document
        doc = {
            "scope": scope,
            "key": key,
            "created_at": datetime.utcnow(),
            "ttl_expires_at": ttl_expires_at
        }
        
        # Add response hash if provided
        if response_data:
            response_hash = self._hash_response(response_data)
            doc["response_hash"] = response_hash
        
        try:
            await self.collection.insert_one(doc)
            return True  # Key created successfully
        except Exception as e:
            # Check if it's a duplicate key error
            if "duplicate key" in str(e).lower():
                return False  # Key already exists
            raise  # Re-raise other errors
    
    async def get_cached_response(self, scope: str, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response for an idempotency key."""
        if not key:
            return None
        
        doc = await self.collection.find_one(
            {"scope": scope, "key": key},
            {"response_hash": 1}
        )
        
        return doc.get("response_hash") if doc else None
    
    def _hash_response(self, response_data: Dict[str, Any]) -> str:
        """Create a hash of the response data."""
        response_str = json.dumps(response_data, sort_keys=True, default=str)
        return hashlib.sha256(response_str.encode()).hexdigest()
    
    def generate_user_scope(self, user_id: ObjectId) -> str:
        """Generate scope for user-specific idempotency."""
        return f"user:{user_id}"
    
    def generate_global_scope(self) -> str:
        """Generate scope for global idempotency."""
        return "global"


def extract_idempotency_key_from_headers(headers: Dict[str, str]) -> Optional[str]:
    """Extract idempotency key from request headers."""
    return headers.get("idempotency-key") or headers.get("Idempotency-Key")


def extract_idempotency_key_from_body(body: Dict[str, Any]) -> Optional[str]:
    """Extract idempotency key from request body."""
    return body.get("idempotency_key")
