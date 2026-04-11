from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pydantic import BaseModel
from typing import Optional


# --- Database Setup ---
DATABASE_URL = "mysql+mysqlconnector://anirudh:password123@localhost/ paylater_db "

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()

# --- Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    credit_limit = Column(Integer, default=5000)
    dues = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)

    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="user")

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    transaction_fee_percent = Column(Float)

    # Relationship to transactions
    transactions = relationship("Transaction", back_populates="merchant")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    merchant_id = Column(Integer, ForeignKey("merchants.id"))
    amount = Column(Float)
    fee = Column(Float)
    payable_amount = Column(Float)

    # Relationship to user and merchant
    user = relationship("User", back_populates="transactions")
    merchant = relationship("Merchant", back_populates="transactions")
Base.metadata.create_all(bind=engine)

# --- Schemas ---
class UserBase(BaseModel):
    name: str
    email: str

class MerchantCreate(BaseModel):
    name: str
    transaction_fee_percent: float

class FeeUpdate(BaseModel):
    transaction_fee_percent: float

class TransactionCreate(BaseModel):
    user_id: int
    merchant_id: int
    amount: float

class Repayment(BaseModel):
    user_id: int
    amount: float

# --- FastAPI App ---
app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- User Endpoints ---
@app.post("/users/")
def create_user(user: UserBase, db: Session = Depends(get_db)):
    db_user = User(
        name=user.name,
        email=user.email,
        credit_limit=5000  # ⬅️ Fixed credit limit
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/{user_id}/dues")
def get_user_dues(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "dues": user.dues}

@app.post("/users/repay")
def repay(payment: Repayment, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.dues -= min(payment.amount, user.dues)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users/credit_limit_reached")
def users_at_credit_limit(db: Session = Depends(get_db)):
    return db.query(User).filter(User.dues >= User.credit_limit).all()

@app.get("/users/total_dues")
def total_dues_all_users(db: Session = Depends(get_db)):
    total = db.query(func.sum(User.dues)).scalar()
    return {"total_dues": total}

@app.get("/users/{user_id}/summary")
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "name": user.name,
        "email": user.email,
        "dues": user.dues,
        "credit_limit": user.credit_limit,
        "balance": user.balance
    }

# --- Merchant Endpoints ---
@app.post("/merchants/")
def create_merchant(merchant: MerchantCreate, db: Session = Depends(get_db)):
    existing = db.query(Merchant).filter(Merchant.name == merchant.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Merchant already exists with this name.")
    db_merchant = Merchant(
        name=merchant.name,
        transaction_fee_percent=merchant.transaction_fee_percent
    )
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return db_merchant

@app.put("/merchants/{merchant_id}/update_fee")
def update_fee(merchant_id: int, fee: FeeUpdate, db: Session = Depends(get_db)):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    merchant.transaction_fee_percent = fee.transaction_fee_percent
    db.commit()
    return merchant

@app.get("/merchants/{merchant_id}/fees_collected")
def get_total_fee_by_merchant(merchant_id: int, db: Session = Depends(get_db)):
    total_fee = db.query(func.sum(Transaction.fee)).filter(Transaction.merchant_id == merchant_id).scalar()
    return {"merchant_id": merchant_id, "total_fees_collected": total_fee or 0.0}

# --- Transaction Endpoint ---
@app.post("/transactions/")
def create_transaction(txn: TransactionCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == txn.user_id).first()
    merchant = db.query(Merchant).filter(Merchant.id == txn.merchant_id).first()

    if not user or not merchant:
        raise HTTPException(status_code=404, detail="User or Merchant not found")

    if user.dues + txn.amount > user.credit_limit:
        raise HTTPException(status_code=400, detail="Credit limit exceeded")

    fee = txn.amount * merchant.transaction_fee_percent / 100
    payable_amount = txn.amount - fee

    transaction = Transaction(
        user_id=txn.user_id,
        merchant_id=txn.merchant_id,
        amount=txn.amount,
        fee=fee,
        payable_amount=payable_amount
    )

    user.dues += txn.amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction
