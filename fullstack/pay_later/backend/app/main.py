"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from contextlib import asynccontextmanager

from .core.config import settings, CORS_CONFIG
from .core.database import database
from .core.exceptions import PayLaterException, handle_pay_later_exception
from .api.v1 import auth, users, credit_limits, transactions, merchants

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting Pay-Later API...")
    await database.connect()
    logger.info("Pay-Later API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Pay-Later API...")
    await database.disconnect()
    logger.info("Pay-Later API shut down successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A minimalistic enterprise-grade pay-later application API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_CONFIG["origins"],
    allow_credentials=CORS_CONFIG["allow_credentials"],
    allow_methods=CORS_CONFIG["allow_methods"],
    allow_headers=CORS_CONFIG["allow_headers"],
)

# Add trusted host middleware for production
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure with actual allowed hosts
    )


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(PayLaterException)
async def pay_later_exception_handler(request: Request, exc: PayLaterException):
    """Handle PayLaterException."""
    return handle_pay_later_exception(exc)


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "type": "internal_error"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(credit_limits.router, prefix="/api/v1/credit-limits", tags=["Credit Limits"])
app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
app.include_router(merchants.router, prefix="/api/v1/merchants", tags=["Merchants"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else None
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
