from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from database.database import engine, Base
from routes import auth, cart, items
from middleware.auth import get_current_user

# Create database tables
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")
    yield
    # Shutdown
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Shopping Cart Backend API",
    description="A comprehensive backend API for online shopping cart with inventory validation",
    version="1.0.0",
    lifespan=lifespan
)

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(cart.router, prefix="/api/cart", tags=["Shopping Cart"])
app.include_router(items.router, prefix="/api/items", tags=["Items"])

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "OK", "timestamp": "2024-01-01T00:00:00Z"}

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Shopping Cart Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
