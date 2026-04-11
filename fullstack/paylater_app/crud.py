from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Merchant, Transaction
from schemas import UserCreate, MerchantCreate, TransactionCreate, Repayment
from fastapi import HTTPException
import models
import schemas


def create_user(db: Session, user: UserCreate):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def create_merchant(db: Session, merchant: MerchantCreate):
    new_merchant = Merchant(**merchant.dict())
    db.add(new_merchant)
    db.commit()
    db.refresh(new_merchant)
    return new_merchant


def update_fee(db: Session, merchant_id: int, new_fee: float):
    merchant = db.query(Merchant).filter(Merchant.id == merchant_id).first()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    merchant.transaction_fee_percent = new_fee
    db.commit()
    return merchant


def create_transaction(db: Session, txn: schemas.TransactionCreate):
    user = db.query(models.User).filter(models.User.id == txn.user_id).first()
    merchant = db.query(models.Merchant).filter(models.Merchant.id == txn.merchant_id).first()

    if not user or not merchant:
        raise HTTPException(status_code=404, detail="User or Merchant not found")

    if user.dues + txn.amount > user.credit_limit:
        raise HTTPException(status_code=400, detail="Credit limit exceeded")

    fee = txn.amount * merchant.transaction_fee_percent / 100

    transaction = models.Transaction(
        user_id=txn.user_id,
        merchant_id=txn.merchant_id,
        amount=txn.amount,
        fee=fee
        # ❌ Removed payable_amount since it's not in the DB model
    )

    user.dues += txn.amount

    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def repay(db: Session, payment: schemas.Repayment):
    user = db.query(models.User).filter(models.User.id == payment.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.dues -= min(payment.amount, user.dues)

    db.commit()
    db.refresh(user)
    return user


def get_total_fee_by_merchant(db: Session, merchant_id: int):
    return db.query(Transaction).filter(Transaction.merchant_id == merchant_id).with_entities(
        Transaction.merchant_id, func.sum(Transaction.fee)
    ).first()


def get_user_dues(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user_id": user_id, "dues": user.dues}


def users_at_credit_limit(db: Session):
    return db.query(User).filter(User.dues >= User.credit_limit).all()


def total_dues_all_users(db: Session):
    return db.query(User).with_entities(func.sum(User.dues)).scalar()


def get_user_summary(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "name": user.name,
        "email": user.email,
        "dues": user.dues,
        "credit_limit": user.credit_limit,
        "balance": user.balance
    }
