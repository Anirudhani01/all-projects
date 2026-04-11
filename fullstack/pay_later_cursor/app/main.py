from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.db.mongo import get_database, connect_to_mongo, close_mongo_connection
from app.rbac.initializer import initialize_rbac
from app.api.error_handlers import register_exception_handlers
from app.api.routers import users, merchants, transactions, reports, auth, rbac, wallet
from app.common.logging import setup_logging
import structlog

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting application", env=settings.app_env)
    
    # Setup logging
    setup_logging()
    
    # Connect to MongoDB
    await connect_to_mongo()
    
    # Initialize RBAC system
    try:
        database = await get_database()
        rbac_result = await initialize_rbac(database)
        logger.info("RBAC system initialized", result=rbac_result)
    except Exception as e:
        logger.error("Failed to initialize RBAC system", error=str(e))
        # Don't fail startup, just log the error
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_mongo_connection()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="LazyPay API",
    description="A modular monolithic FastAPI application for a pay-later service",
    version="1.0.0",
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

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(merchants.router, prefix="/api/v1")
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(rbac.router, prefix="/api/v1")
app.include_router(wallet.router, prefix="/api/v1")


# Note: RBAC initialization is now handled in the lifespan context manager


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "lazypay"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to LazyPay API",
        "version": "1.0.0",
        "docs": "/docs"
    }
