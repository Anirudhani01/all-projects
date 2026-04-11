from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ..models import Payment, Order, PaymentRequest, PaymentResponse
from ..db import get_session
import uuid

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/process", response_model=PaymentResponse)
def process_payment(
    payment_request: PaymentRequest,
    session: Session = Depends(get_session)
):
    """Simulate payment processing for an order"""
    try:
        # Check if order exists and get its details
        order = session.get(Order, payment_request.order_id)
        
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if order.status != 'PENDING':
            raise HTTPException(status_code=400, detail=f"Order status is {order.status}, cannot process payment")
        
        # Simulate payment processing based on payment token
        # This is a dummy implementation - in real scenario, this would call external payment gateway
        if payment_request.payment_token.startswith("tok_visa_4242"):
            # Successful payment simulation
            payment_status = "COMPLETED"
            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
        elif payment_request.payment_token.startswith("tok_visa_declined"):
            # Failed payment simulation
            raise HTTPException(status_code=400, detail="Payment declined by bank")
        else:
            # Default successful payment
            payment_status = "COMPLETED"
            transaction_id = f"txn_{uuid.uuid4().hex[:16]}"
        
        # Update order status to PROCESSING
        order.status = 'PROCESSING'
        session.add(order)
        
        # Create payment record
        new_payment = Payment(
            order_id=payment_request.order_id,
            amount=order.total_amount,
            payment_method='credit_card',
            status=payment_status,
            transaction_id=transaction_id
        )
        session.add(new_payment)
        
        session.commit()
        
        return PaymentResponse(
            status=payment_status,
            transaction_id=transaction_id
        )
        
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Payment processing failed: {str(e)}")
