from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session, select
from ..models import Order, OrderItem, CartItem, Product, OrderResponse, OrderSummaryResponse, OrderItemResponse
from ..db import get_session
from ..services.inventory import check_stock, reduce_stock

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/{user_id}", response_model=OrderResponse)
def create_order(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Create an order from the user's cart with atomic transaction"""
    try:
        # Get cart items with product details
        cart_items = session.exec(
            select(CartItem).where(CartItem.user_id == user_id)
        ).all()
        
        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Check stock for all items
        total_amount = 0
        for cart_item in cart_items:
            # Get product details
            product = session.get(Product, cart_item.product_id)
            if not product:
                raise HTTPException(status_code=400, detail=f"Product {cart_item.product_id} not found")
            
            current_stock = check_stock(session, product.product_id)
            if current_stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for product {product.name}. Available: {current_stock}, Requested: {cart_item.quantity}"
                )
            
            # Calculate item total
            item_total = product.price * cart_item.quantity
            total_amount += item_total
        
        # Create order
        new_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status='PENDING'
        )
        session.add(new_order)
        session.flush()  # Get the order_id
        
        # Create order items and reduce stock
        order_items = []
        for cart_item in cart_items:
            # Get product details
            product = session.get(Product, cart_item.product_id)
            
            # Create order item
            new_order_item = OrderItem(
                order_id=new_order.order_id,
                product_id=product.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=product.price
            )
            session.add(new_order_item)
            
            # Reduce stock using inventory service
            if not reduce_stock(session, product.product_id, cart_item.quantity):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to reduce stock for product {product.name}"
                )
            
            # Add to order items list
            order_items.append(OrderItemResponse(
                product_id=product.product_id,
                quantity=cart_item.quantity,
                price_at_purchase=product.price
            ))
        
        # Clear the cart
        for cart_item in cart_items:
            session.delete(cart_item)
        
        session.commit()
        
        return OrderResponse(
            order_id=new_order.order_id,
            status='PENDING',
            total_amount=total_amount,
            created_at=new_order.created_at,
            items=order_items
        )
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Order creation failed: {str(e)}")

@router.get("/{user_id}", response_model=List[OrderSummaryResponse])
def get_user_orders(
    user_id: int,
    session: Session = Depends(get_session)
):
    """Retrieve a list of the user's orders"""
    try:
        orders = session.exec(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
        ).all()
        
        return [
            OrderSummaryResponse(
                order_id=order.order_id,
                status=order.status,
                total_amount=order.total_amount,
                created_at=order.created_at
            )
            for order in orders
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{user_id}/{order_id}", response_model=OrderResponse)
def get_order_details(
    user_id: int,
    order_id: int,
    session: Session = Depends(get_session)
):
    """Retrieve details of a specific order"""
    try:
        # Get order details
        order = session.exec(
            select(Order).where(
                Order.order_id == order_id,
                Order.user_id == user_id
            )
        ).first()
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get order items
        order_items = session.exec(
            select(OrderItem).where(OrderItem.order_id == order_id)
        ).all()
        
        # Convert to OrderItemResponse objects
        items = [
            OrderItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                price_at_purchase=item.price_at_purchase
            )
            for item in order_items
        ]
        
        return OrderResponse(
            order_id=order.order_id,
            status=order.status,
            total_amount=order.total_amount,
            created_at=order.created_at,
            items=items
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
