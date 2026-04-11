from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Import the appropriate config based on database type
try:
    from config_sqlite import settings as sqlite_settings
    if sqlite_settings.database_type.lower() == "sqlite":
        settings = sqlite_settings
except ImportError:
    pass

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,   # Verify connections before use
    pool_recycle=3600     # Recycle connections every hour
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
