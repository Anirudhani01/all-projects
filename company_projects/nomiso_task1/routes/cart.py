from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.database import get_db, User, Item, CartItem
from schemas.schemas import CartItemCreate, CartResponse, AddToCartResponse
from middleware.auth import get_current_user
from typing import List
import re

router = APIRouter()

def validate_item_id_format(item_id: str) -> bool:
    """Validate item ID format to prevent SQL injection."""
    # Check if itemId contains potentially dangerous characters
    dangerous_chars = r'[<>\'";]'
    return not bool(re.search(dangerous_chars, str(item_id)))

@router.post("/add", response_model=AddToCartResponse)
async def add_to_cart(
    cart_item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart - Main endpoint for test cases."""
    
    # Validate item ID format
    if not validate_item_id_format(cart_item.item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    # Check if item exists and has sufficient stock
    item = db.query(Item).filter(Item.id == cart_item.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )
    
    if item.stock_quantity < cart_item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient inventory"
        )
    
    # Check if item already exists in user's cart
    existing_cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.item_id == cart_item.item_id
    ).first()
    
    if existing_cart_item:
        # Update existing cart item
        new_quantity = existing_cart_item.quantity + cart_item.quantity
        
        if new_quantity > item.stock_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient inventory"
            )
        
        existing_cart_item.quantity = new_quantity
        db.commit()
    else:
        # Add new item to cart
        new_cart_item = CartItem(
            user_id=current_user.id,
            item_id=cart_item.item_id,
            quantity=cart_item.quantity
        )
        db.add(new_cart_item)
        db.commit()
    
    # Update inventory
    item.stock_quantity -= cart_item.quantity
    db.commit()
    
    # Get updated cart total
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    cart_total = sum(cart_item.quantity * cart_item.item.price for cart_item in cart_items)
    
    return AddToCartResponse(
        message="Item added to cart successfully",
        cart_total=round(cart_total, 2),
        item_added={
            "id": item.id,
            "name": item.name,
            "quantity": cart_item.quantity,
            "price": item.price
        }
    )

@router.get("/", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's cart contents."""
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    # Calculate total
    cart_total = sum(cart_item.quantity * cart_item.item.price for cart_item in cart_items)
    
    return CartResponse(
        items=cart_items,
        total=round(cart_total, 2),
        item_count=len(cart_items)
    )

@router.delete("/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart."""
    # Validate item ID format
    if not validate_item_id_format(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item ID format"
        )
    
    # Get current quantity in cart
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.item_id == item_id
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )
    
    # Remove from cart
    db.delete(cart_item)
    
    # Restore inventory
    item = db.query(Item).filter(Item.id == item_id).first()
    if item:
        item.stock_quantity += cart_item.quantity
    
    db.commit()
    
    return {"message": "Item removed from cart successfully"}

@router.delete("/")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart."""
    # Get all items in cart to restore inventory
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    
    # Clear cart
    for cart_item in cart_items:
        # Restore inventory
        item = db.query(Item).filter(Item.id == cart_item.item_id).first()
        if item:
            item.stock_quantity += cart_item.quantity
        db.delete(cart_item)
    
    db.commit()
    
    return {"message": "Cart cleared successfully"}
