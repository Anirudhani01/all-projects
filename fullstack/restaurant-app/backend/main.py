from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import Order
from schemas import OrderCreate, Order
from datetime import datetime, timezone, timedelta
from fastapi.responses import FileResponse
from nlp_router import router as nlp_router
import json

print("Starting main.py")
app = FastAPI()
print("FastAPI app created")
app.include_router(nlp_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # frontend port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Creating database tables")
Base.metadata.create_all(bind=engine)
print("Database tables created")

OWNER_CREDENTIALS = {"owner_id": "anirudh", "password": "password123"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/login")
async def login(owner_id: str, password: str):
    if owner_id != OWNER_CREDENTIALS["owner_id"] or password != OWNER_CREDENTIALS["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"access_token": "mock_token", "token_type": "bearer"}

@app.post("/orders/", response_model=Order)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(
        table_number=order.table_number,
        items=json.dumps(order.items),
        total_bill=order.total_bill,
        entry_time=datetime.now(timezone(timedelta(hours=5.5)))  # IST
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.put("/orders/{order_id}/paid", response_model=Order)
async def mark_paid(order_id: int, db: Session = Depends(get_db)):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    db_order.closing_time = datetime.now(timezone(timedelta(hours=5.5)))  # IST
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/orders/", response_model=list[Order])
async def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()

@app.get("/")
def read_root():
    return {"message": "Welcome to the restaurant app!"}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

