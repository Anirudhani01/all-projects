# Admin Authentication API

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import jwt
import hashlib
import secrets

from ..database import get_db
from ..config import settings

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# Simple admin user storage (in production, use proper database)
ADMIN_USERS = {
    "admin": {
        "username": "admin",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "is_active": True,
        "role": "admin"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Admin login endpoint"""
    username = request.username
    password = request.password
    
    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    if username not in ADMIN_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    user = ADMIN_USERS[username]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if password_hash != user["password_hash"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled"
        )
    
    access_token = create_access_token(data={"sub": username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": username,
            "role": user["role"]
        }
    }

@router.post("/logout")
async def logout():
    """Admin logout endpoint"""
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user(current_user: str = Depends(verify_token)):
    """Get current admin user info"""
    if current_user not in ADMIN_USERS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    user = ADMIN_USERS[current_user]
    return {
        "username": current_user,
        "role": user["role"],
        "is_active": user["is_active"]
    }

@router.post("/verify")
async def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify if token is valid"""
    username = verify_token(credentials)
    return {"valid": True, "username": username}
