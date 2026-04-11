"""
Security utilities for JWT token handling and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import JWT_CONFIG
import hashlib
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityUtils:
    """Security utilities for authentication and authorization."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=JWT_CONFIG["access_token_expire_minutes"]
            )
        
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            JWT_CONFIG["secret_key"], 
            algorithm=JWT_CONFIG["algorithm"]
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        
        expire = datetime.utcnow() + timedelta(
            days=JWT_CONFIG["refresh_token_expire_days"]
        )
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode, 
            JWT_CONFIG["secret_key"], 
            algorithm=JWT_CONFIG["algorithm"]
        )
        
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token, 
                JWT_CONFIG["secret_key"], 
                algorithms=[JWT_CONFIG["algorithm"]]
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT token verification failed: {e}")
            return None
    
    @staticmethod
    def hash_ssn(ssn: str) -> str:
        """Hash SSN using SHA-256."""
        return hashlib.sha256(ssn.encode()).hexdigest()
    
    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if token is expired."""
        payload = SecurityUtils.verify_token(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return datetime.utcnow() > datetime.fromtimestamp(exp)
    
    @staticmethod
    def get_token_type(token: str) -> Optional[str]:
        """Get token type (access or refresh)."""
        payload = SecurityUtils.verify_token(token)
        if not payload:
            return None
        
        return payload.get("type")


# Create security utils instance
security_utils = SecurityUtils()
