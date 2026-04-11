from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

import enum  # <-- this is Python's enum module
from sqlalchemy import Enum  # <-- this is SQLAlchemy's Enum type


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    description = Column(String(255))
    category = Column(String(50))
    price = Column(Float)
    stock = Column(Integer)

    cart_items = relationship("Cart", back_populates="product")
class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    total_price = Column(Float)

    product = relationship("Product", back_populates="cart_items")     
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100))
    amount = Column(Float)
    mode = Column(String(50))
    email = Column(String(100))
    date = Column(DateTime, default=datetime.now)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(100))
    price = Column(Float)
    status = Column(String(50))
    email = Column(String(100))
    order_date = Column(DateTime, default=datetime.now)

class PaymentMethod(enum.Enum):
    cash_on_delivery = "Cash on Delivery"
    debit_card = "Debit Card"
    credit_card = "Credit Card"
    
class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100))
    payment_method = Column(String(50))
    card_last4 = Column(String(4), nullable=True)
    total_amount = Column(Float)  # ✅ Must be here and match DB
    
    
    
    
    