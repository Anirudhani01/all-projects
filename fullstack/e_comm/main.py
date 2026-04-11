from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from routers import products, cart, payment, order
from models import Base
from database import engine
from routers import admin

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

app.include_router(products.router)
app.include_router(cart.router)
app.include_router(payment.router)
app.include_router(order.router)
app.include_router(admin.router)

@app.get("/")
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
# ✅ Include product router
app.include_router(products.router)