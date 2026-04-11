"""
Authentication repository for LazyPay application.
"""

from datetime import datetime
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClientSession
from bson import ObjectId
import bcrypt

from app.auth.models import UserAuth, TokenBlacklist
from app.common.exceptions import NotFoundError, ValidationError

class AuthRepository:
    """Repository for authentication-related database operations."""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database

    async def get_user_by_email(
        self,
        email: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> Optional[UserAuth]:
        """Get user by email address."""
        
        user_doc = await self.database.auth_users.find_one(
            {"email": email.lower()},
            session=session
        )
        
        if not user_doc:
            return None
        
        return UserAuth(
            user_id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc["name"],
            is_active=user_doc.get("is_active", True),
            role=user_doc.get("role", "user"),
            created_at=user_doc.get("created_at", datetime.utcnow()),
            last_login=user_doc.get("last_login")
        )

    async def get_user_by_id(
        self,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> Optional[UserAuth]:
        """Get user by ID."""
        
        try:
            user_doc = await self.database.auth_users.find_one(
                {"_id": ObjectId(user_id)},
                session=session
            )
        except Exception:
            return None
        
        if not user_doc:
            return None
        
        return UserAuth(
            user_id=str(user_doc["_id"]),
            email=user_doc["email"],
            name=user_doc["name"],
            is_active=user_doc.get("is_active", True),
            role=user_doc.get("role", "user"),
            created_at=user_doc.get("created_at", datetime.utcnow()),
            last_login=user_doc.get("last_login")
        )

    async def verify_password(
        self,
        email: str,
        password: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> bool:
        """Verify user password."""
        
        user_doc = await self.database.auth_users.find_one(
            {"email": email.lower()},
            {"password_hash": 1},
            session=session
        )
        
        if not user_doc or "password_hash" not in user_doc:
            return False
        
        # Verify password
        return bcrypt.checkpw(
            password.encode('utf-8'),
            user_doc["password_hash"].encode('utf-8')
        )

    async def update_last_login(
        self,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """Update user's last login timestamp."""
        
        await self.database.auth_users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow()}},
            session=session
        )

    async def change_password(
        self,
        user_id: str,
        new_password_hash: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """Change user password."""
        
        result = await self.database.auth_users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_password_hash}},
            session=session
        )
        
        if result.matched_count == 0:
            raise NotFoundError(f"User {user_id} not found")

    async def blacklist_token(
        self,
        token_id: str,
        user_id: str,
        token_type: str,
        expires_at: datetime,
        reason: Optional[str] = None,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """Add token to blacklist."""
        
        blacklist_entry = TokenBlacklist(
            token_id=token_id,
            user_id=user_id,
            token_type=token_type,
            expires_at=expires_at,
            reason=reason
        )
        
        await self.database.token_blacklist.insert_one(
            blacklist_entry.dict(),
            session=session
        )

    async def is_token_blacklisted(
        self,
        token_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> bool:
        """Check if token is blacklisted."""
        
        blacklisted = await self.database.token_blacklist.find_one(
            {"token_id": token_id},
            session=session
        )
        
        return blacklisted is not None

    async def cleanup_expired_tokens(
        self,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> int:
        """Remove expired tokens from blacklist."""
        
        result = await self.database.token_blacklist.delete_many(
            {"expires_at": {"$lt": datetime.utcnow()}},
            session=session
        )
        
        return result.deleted_count

    async def get_user_tokens(
        self,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> List[TokenBlacklist]:
        """Get all blacklisted tokens for a user."""
        
        cursor = self.database.token_blacklist.find(
            {"user_id": user_id},
            session=session
        )
        
        tokens = []
        async for doc in cursor:
            tokens.append(TokenBlacklist(**doc))
        
        return tokens

    async def create_user(
        self,
        email: str,
        name: str,
        password_hash: str,
        role: str = "user",
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> UserAuth:
        """Create a new user."""
        
        # Check if user already exists
        existing_user = await self.get_user_by_email(email, session)
        if existing_user:
            raise ValidationError(f"User with email {email} already exists")
        
        # Create user document
        user_doc = {
            "email": email.lower(),
            "name": name,
            "password_hash": password_hash,
            "role": role,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "last_login": None
        }
        
        result = await self.database.auth_users.insert_one(user_doc, session=session)
        
        return UserAuth(
            user_id=str(result.inserted_id),
            email=email,
            name=name,
            is_active=True,
            role=role,
            created_at=user_doc["created_at"],
            last_login=None
        )

    async def deactivate_user(
        self,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """Deactivate a user account."""
        
        result = await self.database.auth_users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}},
            session=session
        )
        
        if result.matched_count == 0:
            raise NotFoundError(f"User {user_id} not found")

    async def activate_user(
        self,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """Activate a user account."""
        
        result = await self.database.auth_users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": True}},
            session=session
        )
        
        if result.matched_count == 0:
            raise NotFoundError(f"User {user_id} not found")

    async def update_user_role(
        self,
        user_id: str,
        new_role: str,
        session: Optional[AsyncIOMotorClientSession] = None
    ) -> None:
        """Update user role."""
        
        valid_roles = ["user", "admin", "merchant"]
        if new_role not in valid_roles:
            raise ValidationError(f"Invalid role. Must be one of: {valid_roles}")
        
        result = await self.database.auth_users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"role": new_role}},
            session=session
        )
        
        if result.matched_count == 0:
            raise NotFoundError(f"User {user_id} not found")




