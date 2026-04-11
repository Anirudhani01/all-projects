from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, index=True)
    items = Column(String(1000))  # Length specified for MySQL
    total_bill = Column(Float)
    entry_time = Column(DateTime, default=datetime.utcnow)
    closing_time = Column(DateTime, nullable=True)