from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from database import SessionLocal
from models import Product

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin")
def admin_panel(request: Request):
    db = SessionLocal()
    products = db.query(Product).all()
    db.close()
    return templates.TemplateResponse("admin.html", {"request": request, "products": products})

@router.post("/admin/restock")
def restock_product(request: Request, product_id: int = Form(...), quantity: int = Form(...)):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    product.stock += quantity
    db.commit()
    db.close()
    return RedirectResponse(url="/admin", status_code=302)
