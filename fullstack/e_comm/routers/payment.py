from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Buyer, Cart
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), "templates"))

# GET /payment
@router.get("/payment", response_class=HTMLResponse)
def get_payment_page(request: Request, db: Session = Depends(get_db)):
    cart_items = db.query(Cart).all()
    if not cart_items:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Cart is empty"})
    total_price = sum(item.total_price for item in cart_items)
    return templates.TemplateResponse("payment.html", {
        "request": request,
        "total_price": total_price
    })

# POST /payment
@router.post("/payment")
def process_payment(
    request: Request,
    email: str = Form(...),
    payment_method: str = Form(...),
    card_number: str = Form(None),
    card_cvv: str = Form(None),
    db: Session = Depends(get_db),
):
    cart_items = db.query(Cart).all()
    total_price = sum(item.total_price for item in cart_items)
    card_last4 = card_number[-4:] if card_number else None

    new_buyer = Buyer(
        email=email,
        payment_method=payment_method,
        card_number=card_number,
        cvv=card_cvv,
        card_last4=card_last4,
        total_amount=total_price,
        amount_paid=total_price
    )
    db.add(new_buyer)
    db.commit()

    db.query(Cart).delete()
    db.commit()

    return RedirectResponse(url="/success", status_code=303)
