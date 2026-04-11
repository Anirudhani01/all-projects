from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from ..models import CartItem, Product, CartItemRequest, CartItemResponse, CartResponse
from ..db import get_session

router = APIRouter(prefix="/cart", tags=["cart"])

@router.post("/{user_id}/items")
def add_cart_item(
    user_id: int,
    cart_item: CartItemRequest,
    session: Session = Depends(get_session)
):
    """Add/update an item in the cart"""
    try:
        # Check if product exists
        product = session.get(Product, cart_item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if item already exists in cart
        existing_item = session.exec(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == cart_item.product_id
            )
        ).first()
        
        if existing_item:
            # Update existing item quantity
            existing_item.quantity += cart_item.quantity
            session.add(existing_item)
            session.commit()
            return {"message": "Item quantity updated in cart"}, 200
        else:
            # Create new cart item
            new_cart_item = CartItem(
                user_id=user_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity
            )
            session.add(new_cart_item)
            session.commit()
            return {"message": "Item added to cart"}, 201
            
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{user_id}", response_model=CartResponse)
def get_cart(user_id: int, session: Session = Depends(get_session)):
    """Retrieve the user's cart"""
    try:
        # Get cart items with product details
        cart_items = session.exec(
            select(CartItem).where(CartItem.user_id == user_id)
        ).all()
        
        # Convert to CartItemResponse objects with sub_total calculation
        items = []
        total_price = 0
        
        for cart_item in cart_items:
            # Get product details
            product = session.get(Product, cart_item.product_id)
            if product:
                sub_total = product.price * cart_item.quantity
                total_price += sub_total
                
                items.append(CartItemResponse(
                    product_id=product.product_id,
                    name=product.name,
                    price=product.price,
                    quantity=cart_item.quantity,
                    sub_total=sub_total
                ))
        
        return CartResponse(items=items, total_price=total_price)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.delete("/{user_id}/items/{product_id}")
def remove_cart_item(
    user_id: int,
    product_id: int,
    session: Session = Depends(get_session)
):
    """Remove an item from the cart"""
    try:
        cart_item = session.exec(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
        ).first()
        
        if not cart_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        session.delete(cart_item)
        session.commit()
        
        return None, 204  # 204 No Content
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.put("/{user_id}/items/{product_id}")
def update_cart_item_quantity(
    user_id: int,
    product_id: int,
    cart_item: CartItemRequest,
    session: Session = Depends(get_session)
):
    """Update an item's quantity in the cart"""
    try:
        # Check if product exists
        product = session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Find cart item
        cart_item_obj = session.exec(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id
            )
        ).first()
        
        if not cart_item_obj:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        # Update quantity
        cart_item_obj.quantity = cart_item.quantity
        session.add(cart_item_obj)
        session.commit()
        
        return {"message": "Cart item quantity updated"}, 200
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
