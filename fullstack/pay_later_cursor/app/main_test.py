"""
Test-specific FastAPI application that bypasses database connections.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.routers import users, merchants, transactions
from app.api.error_handlers import register_exception_handlers
from app.config.settings import get_settings

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan for testing - no database connection."""
    logger.info("Starting test application", env="test")
    yield
    logger.info("Shutting down test application", env="test")


def create_test_app() -> FastAPI:
    """Create FastAPI application for testing."""
    settings = get_settings()
    
    app = FastAPI(
        title="LazyPay API - Test",
        description="LazyPay API for testing",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup exception handlers
    register_exception_handlers(app)
    
    # Include routers
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(merchants.router, prefix="/api/v1/merchants", tags=["merchants"])
    app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["transactions"])
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "lazypay", "environment": "test"}
    
    return app


# Create the test app instance
app = create_test_app()
