from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Update with your credentials
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://anirudh:password123@localhost/ecommerce"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
# ✅ ADD THIS FUNCTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()