import os
from sqlmodel import SQLModel, create_engine, Session

# Use SQLite for development/testing - no external database required
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./restaurant.db")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
