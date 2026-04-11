from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
import crud, schemas
from sqlalchemy import func

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pay Later Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "Pay Later Service is running"}
@app.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)


@app.post("/users/")
def onboard_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db, user)

@app.get("/users/{user_id}/summary")
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_summary(db, user_id)


@app.post("/merchants/")
def onboard_merchant(merchant: schemas.MerchantCreate, db: Session = Depends(get_db)):
    return crud.create_merchant(db, merchant)

@app.put("/merchants/{merchant_id}/fee")
def change_fee(merchant_id: int, fee: schemas.FeeUpdate, db: Session = Depends(get_db)):
    return crud.update_fee(db, merchant_id, fee.transaction_fee_percent)
@app.get("/merchants/{merchant_id}/fees_collected")
def get_total_fees(merchant_id: int, db: Session = Depends(get_db)):
    result = crud.get_total_fee_by_merchant(db, merchant_id)
    if result is None:
        return {"merchant_id": merchant_id, "total_fees_collected": 0}
    return {"merchant_id": merchant_id, "total_fees_collected": float(result[1])}

@app.post("/transactions/")
def make_transaction(txn: schemas.TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db, txn)

@app.post("/repay/")
def repay_dues(payment: schemas.Repayment, db: Session = Depends(get_db)):
    return crud.repay(db, payment)

@app.get("/merchant/{merchant_id}/fees-collected")
def fee_collected(merchant_id: int, db: Session = Depends(get_db)):
    return crud.get_total_fee_by_merchant(db, merchant_id)

@app.get("/user/{user_id}/dues")
def get_dues(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_dues(db, user_id)

@app.get("/users/at-credit-limit")
def credit_limit_users(db: Session = Depends(get_db)):
    return crud.users_at_credit_limit(db)

@app.get("/users/credit_limit_reached")
def get_users_at_credit_limit(db: Session = Depends(get_db)):
    users = crud.users_at_credit_limit(db)
    return [{"user_id": user.id, "name": user.name, "dues": user.dues, "credit_limit": user.credit_limit} for user in users]

@app.get("/users/total_dues")
def get_total_dues(db: Session = Depends(get_db)):
    total_dues = crud.total_dues_all_users(db)
    return {"total_dues": total_dues or 0.0}