from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Buyer, Cart
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi import Form
from models import Product, Cart
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

# Pydantic form model
class PaymentForm(BaseModel):
    email: str
    payment_method: str
    card_number: str = None
    card_cvv: str = None

# GET /payment page
@router.get("/payment", response_class=HTMLResponse)
def get_payment_page(request: Request, db: Session = Depends(get_db)):
    cart_items = db.query(Cart).all()
    total_price = sum(item.total_price for item in cart_items)
    return templates.TemplateResponse("payment.html", {"request": request, "total_price": total_price})

# POST /payment to process the form
@router.post("/payment")
def process_payment(
    request: Request,
    email: str = Form(...),
    payment_method: str = Form(...),
    card_number: str = Form(None),
    card_cvv: str = Form(None),
    db: Session = Depends(get_db),
):
    # Calculate total price from cart
    cart_items = db.query(Cart).all()
    total_price = sum(item.total_price for item in cart_items)

    # Extract last 4 digits of card if applicable
    card_last4 = card_number[-4:] if payment_method in ["Debit Card", "Credit Card"] and card_number else None

    # Insert into Buyer table
    new_buyer = Buyer(
        email=email,
        payment_method=payment_method,
        card_last4=card_last4,
        total_amount=total_price  # Make sure this column exists in the database!
    )
    db.add(new_buyer)

    # Clear cart after payment
    db.query(Cart).delete()

    db.commit()

    # Redirect to success page
    return RedirectResponse(url="/success", status_code=303)

# GET /success page
@router.get("/success", response_class=HTMLResponse)
def success_page(request: Request):
    return templates.TemplateResponse("success.html", {"request": request})

@router.post("/cart/add")
def add_to_cart(
    product_id: int = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"message": "Product not found"}

    cart_item = Cart(product_id=product_id, quantity=quantity)
    db.add(cart_item)
    db.commit()
    return RedirectResponse(url="/cart", status_code=303)
