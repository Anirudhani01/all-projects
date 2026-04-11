from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select

app = FastAPI()

# --- Database Setup ---
DATABASE_URL = "mysql+pymysql://anirudh:password123@localhost/paylater_db1"
engine = create_engine(DATABASE_URL, echo=True)

# --- SQLModel Table Definitions ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    credit_limit: int = 5000  # available credit
    dues: float = 0.0

class Merchant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    transaction_fee_percent: float

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    merchant_id: int = Field(foreign_key="merchant.id")
    amount: float
    fee: float

# --- Pydantic Schemas ---
class UserCreate(SQLModel):
    name: str
    email: str

class UserRead(SQLModel):
    id: int
    name: str
    email: str
    credit_limit: int
    dues: float

    class Config:
        orm_mode = True

class UserRepay(SQLModel):
    user_id: int
    amount: float

class MerchantCreate(SQLModel):
    name: str
    transaction_fee_percent: float

class MerchantRead(SQLModel):
    id: int
    name: str
    transaction_fee_percent: float

    class Config:
        orm_mode = True

class UpdateTransactionFee(SQLModel):
    transaction_fee_percent: float

class TransactionCreate(SQLModel):
    user_name: str
    merchant_name: str
    amount: float
class TransactionRead(SQLModel):
    id: int
    user_id: int
    merchant_id: int
    amount: float
    fee: float

    class Config:
        orm_mode = True

# --- DB Dependency ---
def get_session():
    with Session(engine) as session:
        yield session

# --- User Endpoints ---
@app.post("/users/", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    db_user = User(**user.dict(), credit_limit=5000)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get("/users/{user_id}/dues")
def get_user_dues(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"dues": user.dues}

@app.post("/users/repay")
def repay(repay_data: UserRepay, session: Session = Depends(get_session)):
    user = session.get(User, repay_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    repay_amount = min(repay_data.amount, user.dues)
    user.dues -= repay_amount
    user.credit_limit = min(user.credit_limit + repay_amount, 5000)

    session.add(user)
    session.commit()
    return {"message": f"Repayment of ₹{repay_amount} successful"}

@app.get("/users/credit_limit_reached", response_model=List[UserRead])
def credit_limit_reached_users(session: Session = Depends(get_session)):
    statement = select(User).where(User.credit_limit <= 0)
    results = session.exec(statement).all()
    return results

@app.get("/users/total_dues")
def total_dues(session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    return {"total_dues": sum(user.dues for user in users)}

@app.get("/users/{user_id}/summary", response_model=UserRead)
def user_summary(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# --- Merchant Endpoints ---
@app.post("/merchants/", response_model=MerchantRead)
def create_merchant(merchant: MerchantCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(Merchant).where(Merchant.name == merchant.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Merchant already exists")
    db_merchant = Merchant(**merchant.dict())
    session.add(db_merchant)
    session.commit()
    session.refresh(db_merchant)
    return db_merchant

@app.put("/merchants/{merchant_id}/update_fee")
def update_transaction_fee(merchant_id: int, fee_data: UpdateTransactionFee, session: Session = Depends(get_session)):
    merchant = session.get(Merchant, merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    merchant.transaction_fee_percent = fee_data.transaction_fee_percent
    session.add(merchant)
    session.commit()
    return {"message": "Fee updated"}

@app.get("/merchants/{merchant_id}/fees_collected")
def total_fees_collected(merchant_id: int, session: Session = Depends(get_session)):
    statement = select(Transaction).where(Transaction.merchant_id == merchant_id)
    transactions = session.exec(statement).all()
    total_fees = sum(t.fee for t in transactions)
    return {"total_fees_collected": total_fees}

# --- Transaction Endpoint ---
@app.post("/transactions/", response_model=TransactionRead)
def make_transaction(data: TransactionCreate, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.name == data.user_name)).first()
    merchant = session.exec(select(Merchant).where(Merchant.name == data.merchant_name)).first()

    if not user or not merchant:
        raise HTTPException(status_code=404, detail="User or Merchant not found")

    if user.credit_limit < data.amount:
        raise HTTPException(status_code=400, detail="Insufficient credit limit")

    fee = data.amount * (merchant.transaction_fee_percent / 100)
    transaction = Transaction(
        user_id=user.id,
        merchant_id=merchant.id,
        amount=data.amount,
        fee=fee
    )

    user.dues += data.amount
    user.credit_limit -= data.amount

    session.add(transaction)
    session.add(user)
    session.commit()
    session.refresh(transaction)
    return transaction

# --- Create Tables ---
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)
