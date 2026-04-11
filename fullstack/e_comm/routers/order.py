from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Order
from schemas import OrderOut
from database import SessionLocal

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return db.query(Order).filter(Order.id == order_id).first()
