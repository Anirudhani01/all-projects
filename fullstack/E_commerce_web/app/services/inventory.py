from sqlmodel import Session, select
from ..models import Product

def check_stock(session: Session, product_id: int) -> int:
    """Returns the current stock quantity for a given product ID"""
    try:
        product = session.get(Product, product_id)
        if not product:
            return 0
        return product.stock_quantity
    except Exception:
        return 0

def reduce_stock(session: Session, product_id: int, quantity: int) -> bool:
    """Decrements stock and returns True on success, False on failure (e.g., insufficient stock)"""
    try:
        product = session.get(Product, product_id)
        if not product:
            return False
        
        if product.stock_quantity < quantity:
            return False
        
        # Update stock quantity
        product.stock_quantity -= quantity
        session.add(product)
        session.commit()
        
        return True
    except Exception:
        session.rollback()
        return False
