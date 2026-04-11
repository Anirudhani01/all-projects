from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.api.error_handlers import register_exception_handlers
from app.api.routers import users, merchants, transactions
from app.common.logging import setup_logging
import structlog

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for development."""
    # Startup
    logger.info("Starting application in development mode", env=settings.app_env)
    
    # Setup logging
    setup_logging()
    
    # Skip MongoDB connection for development
    logger.warning("MongoDB connection skipped for development mode")
    logger.info("Application started successfully in development mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="LazyPay API (Development Mode)",
    description="A modular monolithic FastAPI application for a pay-later service - Development Mode (No MongoDB)",
    version="1.0.0-dev",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include routers (these will fail without MongoDB, but the app will start)
try:
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(merchants.router, prefix="/api/v1")
    app.include_router(transactions.router, prefix="/api/v1")
except Exception as e:
    logger.warning(f"Could not include routers due to MongoDB dependency: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lazypay", "mode": "development"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to LazyPay API (Development Mode)",
        "version": "1.0.0-dev",
        "docs": "/docs",
        "note": "This is running in development mode without MongoDB"
    }


@app.get("/setup")
async def setup_info():
    """Setup information endpoint."""
    return {
        "message": "LazyPay API Setup Information",
        "mongodb_required": True,
        "mongodb_uri": settings.mongodb_uri,
        "mongodb_db": settings.mongodb_db,
        "setup_instructions": [
            "1. Install MongoDB Community Server",
            "2. Start MongoDB service",
            "3. Run the main application with: python -m uvicorn app.main:app --reload",
            "4. Or use Docker: docker run -d --name mongodb -p 27017:27017 mongo:latest"
        ]
    }
