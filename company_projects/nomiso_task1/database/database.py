from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os

# Database URL for MySQL
DATABASE_URL = "mysql+pymysql://anirudh:password123@localhost:3306/shopping_cart"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    category = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="item", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cart_items")
    item = relationship("Item", back_populates="cart_items")

# Initialize database with sample data
def init_db():
    db = SessionLocal()
    try:
        # Check if data already exists
        existing_items = db.query(Item).first()
        if existing_items:
            return
        
        # Create sample items
        sample_items = [
            Item(
                name="Laptop",
                description="High-performance laptop with latest specs",
                price=999.99,
                stock_quantity=50,
                category="Electronics"
            ),
            Item(
                name="Smartphone",
                description="Latest smartphone model",
                price=699.99,
                stock_quantity=100,
                category="Electronics"
            ),
            Item(
                name="Headphones",
                description="Wireless noise-canceling headphones",
                price=199.99,
                stock_quantity=75,
                category="Electronics"
            ),
            Item(
                name="Book",
                description="Programming fundamentals",
                price=49.99,
                stock_quantity=200,
                category="Books"
            ),
            Item(
                name="T-shirt",
                description="Cotton casual t-shirt",
                price=24.99,
                stock_quantity=150,
                category="Clothing"
            )
        ]
        
        # Create sample user
        sample_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="$2b$12$dummy.hash.for.testing.purposes"
        )
        
        # Add to database
        db.add_all(sample_items)
        db.add(sample_user)
        db.commit()
        
        print("Sample data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

# Call init_db when module is imported
if __name__ == "__main__":
    init_db()
