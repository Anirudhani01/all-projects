from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'anirudh',
    'password': 'password123',
    'database': 'ecom_db',
    'charset': 'utf8mb4'
}

# Create database URL for SQLModel
DATABASE_URL = f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}?charset={DB_CONFIG['charset']}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_recycle=300
)

def create_db_and_tables():
    """Create database tables using SQLModel"""
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully")

def get_session() -> Generator[Session, None, None]:
    """Dependency function for FastAPI to get database session"""
    with Session(engine) as session:
        yield session

# For backward compatibility
def get_db():
    """Legacy function for backward compatibility"""
    return get_session()
