from database import engine
from models import Base

# ⚠️ WARNING: This will delete all data and recreate the tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Database tables dropped and recreated with updated schema.")
