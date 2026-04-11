from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time

from .config.settings import settings
from .config.database import connect_to_mongo, close_mongo_connection
from .api.v1 import products, wishlist, reviews, search, categories, analytics, orders, users

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting E-commerce Backend...")
    try:
        await connect_to_mongo()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down E-commerce Backend...")
    try:
        await close_mongo_connection()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error closing database connection: {e}")


# Create FastAPI application
app = FastAPI(
    title="E-commerce Backend API",
    description="A comprehensive e-commerce backend API built with FastAPI and MongoDB",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for production
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure this properly for production
    )

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add error handling middleware
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR"
        }
    )


# Include API routes
app.include_router(products.router, prefix="/api/v1")
app.include_router(wishlist.router, prefix="/api/v1")
app.include_router(reviews.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ecommerce-backend",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "E-commerce Backend API",
        "version": "1.0.0",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
