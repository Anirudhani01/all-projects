from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductOut
from database import get_db
from database import SessionLocal

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Render laptop info page
@router.get("/products/laptops")
def get_laptops(request: Request, db: Session = Depends(get_db)):
    laptops = db.query(Product).filter(Product.category == "laptops").all()
    print("Laptops:", laptops)  # Add debug print
    return templates.TemplateResponse("laptops_info.html", {
        "request": request,
        "laptops": laptops
    })
# Search endpoint
@router.get("/search", response_model=list[ProductOut])
def search_products(query: str, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.name.ilike(f"%{query}%")).all()

# Get product by ID
@router.get("/product/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == product_id).first()
