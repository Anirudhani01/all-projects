"""
JWT handler for LazyPay application authentication.
"""

import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
import structlog

from app.auth.models import TokenData, TokenBlacklist
from app.config.settings import settings

logger = structlog.get_logger(__name__)


class JWTHandler:
    """JWT token handler for authentication."""
    
    def __init__(self):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 3  # 3 minutes
        self.refresh_token_expire_minutes = 5  # 5 minutes
        
    def create_access_token(
        self,
        user_id: str,
        email: str,
        name: str,
        role: str = "user"
    ) -> str:
        """Create JWT access token."""
        
        # Token expiration
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        # Token payload
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "access",
            "jti": str(uuid.uuid4())  # JWT ID for blacklisting
        }
        
        # Create token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(
            "Access token created",
            user_id=user_id,
            expires_at=expire.isoformat(),
            token_id=payload["jti"]
        )
        
        return token
    
    def create_refresh_token(
        self,
        user_id: str,
        email: str,
        name: str,
        role: str = "user"
    ) -> str:
        """Create JWT refresh token."""
        
        # Token expiration
        expire = datetime.utcnow() + timedelta(minutes=self.refresh_token_expire_minutes)
        
        # Token payload
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "refresh",
            "jti": str(uuid.uuid4())  # JWT ID for blacklisting
        }
        
        # Create token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        logger.info(
            "Refresh token created",
            user_id=user_id,
            expires_at=expire.isoformat(),
            token_id=payload["jti"]
        )
        
        return token
    
    def verify_token(self, token: str) -> TokenData:
        """Verify and decode JWT token."""
        
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Extract token data
            token_data = TokenData(
                user_id=payload["sub"],
                email=payload["email"],
                name=payload["name"],
                role=payload["role"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                token_type=payload["token_type"]
            )
            
            # Check if token is expired
            if datetime.utcnow() > token_data.exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            logger.debug(
                "Token verified successfully",
                user_id=token_data.user_id,
                token_type=token_data.token_type
            )
            
            return token_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired", token=token[:20] + "...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except (jwt.InvalidTokenError, jwt.DecodeError) as e:
            logger.warning("Invalid token", error=str(e), token=token[:20] + "...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except KeyError as e:
            logger.error("Missing required token field", field=str(e), token=token[:20] + "...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format"
            )
    
    def verify_access_token(self, token: str) -> TokenData:
        """Verify access token specifically."""
        
        token_data = self.verify_token(token)
        
        if token_data.token_type != "access":
            logger.warning("Wrong token type used as access token", token_type=token_data.token_type)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return token_data
    
    def verify_refresh_token(self, token: str) -> TokenData:
        """Verify refresh token specifically."""
        
        token_data = self.verify_token(token)
        
        if token_data.token_type != "refresh":
            logger.warning("Wrong token type used as refresh token", token_type=token_data.token_type)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        return token_data
    
    def get_token_payload(self, token: str) -> Dict[str, Any]:
        """Get token payload without verification (for blacklist checking)."""
        
        try:
            # Decode without verification to get payload
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": False})
            return payload
        except jwt.JWTError:
            return {}
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired."""
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": False})
            exp_timestamp = payload.get("exp")
            
            if not exp_timestamp:
                return True
            
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            return datetime.utcnow() > exp_datetime
            
        except jwt.JWTError:
            return True
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """Get token expiration time."""
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": False})
            exp_timestamp = payload.get("exp")
            
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
            
            return None
            
        except jwt.JWTError:
            return None
    
    def get_token_id(self, token: str) -> Optional[str]:
        """Get JWT ID from token."""
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_signature": False})
            return payload.get("jti")
        except jwt.JWTError:
            return None


# Global JWT handler instance
jwt_handler = JWTHandler()




