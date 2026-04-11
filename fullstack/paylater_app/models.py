from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255), unique=True)
    credit_limit = Column(Integer)
    balance = Column(Integer, default=0)
    dues = Column(Integer, default=0)

    transactions = relationship("Transaction", back_populates="user")  # ✅

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    transaction_fee_percent = Column(Float)

    transactions = relationship("Transaction", back_populates="merchant")  # ✅ add this

# In models.py

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    amount = Column(Float)
    fee = Column(Float)
    # payable_amount = Column(Float)  # ✅ Add this line

    user = relationship("User", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
