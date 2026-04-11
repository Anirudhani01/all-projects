from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .routers import products, cart, orders, payments
from .db import create_db_and_tables, get_session
from sqlmodel import Session
import mysql.connector
from mysql.connector import Error

app = FastAPI(
    title="E-Commerce API",
    description="A modern e-commerce backend API built with FastAPI and MySQL",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1")
app.include_router(cart.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    create_db_and_tables()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to E-Commerce API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/test-db")
async def test_database(session: Session = Depends(get_session)):
    """Test database connection"""
    try:
        # Simple test query
        result = session.execute("SELECT 1 as test").fetchone()
        return {"message": "Database connection successful", "test_result": result[0]}
    except Exception as e:
        return {"error": f"Database connection failed: {str(e)}"}

@app.get("/api/v1/stats")
async def get_stats(session: Session = Depends(get_session)):
    """Get system statistics"""
    try:
        # Get basic stats using SQLModel ORM
        from .models import Product, Order, User, CartItem
        from sqlmodel import select
        
        total_products = len(session.exec(select(Product)).all())
        total_orders = len(session.exec(select(Order)).all())
        total_users = len(session.exec(select(User)).all())
        total_cart_items = len(session.exec(select(CartItem)).all())
        
        return {
            "total_products": total_products,
            "total_orders": total_orders,
            "total_users": total_users,
            "total_cart_items": total_cart_items
        }
    except Exception as e:
        return {"error": f"Failed to get stats: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
