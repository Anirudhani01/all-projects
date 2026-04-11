from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.modules.transactions.service import TransactionService
from app.modules.transactions.schemas import (
    PurchaseRequest,
    PaymentRequest,
    TransactionResponse,
    PurchaseResponse,
    PaymentResponse,
    TransactionListResponse,
    TransactionFilter,
    TransactionSummary
)
from app.api.dependencies import get_transaction_service
from app.auth.dependencies import get_current_active_user
from app.auth.models import UserAuth
from app.rbac.middleware import (
    require_transactions_write, require_transactions_read, require_transactions_approve
)
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/purchase", response_model=PurchaseResponse, status_code=201)
async def process_purchase(
    request: PurchaseRequest,
    current_user: UserAuth = Depends(require_transactions_write),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> PurchaseResponse:
    """Process a purchase transaction. Requires transactions:write permission."""
    logger.info("Processing purchase transaction",
               user_id=request.user_id,
               merchant_id=request.merchant_id,
               amount=request.amount,
               idempotency_key=request.idempotency_key,
               requested_by=current_user.email)
    
    return await transaction_service.process_purchase(request)


@router.post("/payment", response_model=PaymentResponse, status_code=201)
async def process_payment(
    request: PaymentRequest,
    current_user: UserAuth = Depends(require_transactions_write),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> PaymentResponse:
    """Process a payment transaction. Requires transactions:write permission."""
    logger.info("Processing payment transaction",
               user_id=request.user_id,
               amount=request.amount,
               idempotency_key=request.idempotency_key,
               requested_by=current_user.email)
    
    return await transaction_service.process_payment(request)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: UserAuth = Depends(require_transactions_read),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> TransactionResponse:
    """Get transaction by ID. Requires transactions:read permission."""
    logger.info("Getting transaction", transaction_id=transaction_id, requested_by=current_user.email)
    
    try:
        return await transaction_service.get_transaction(transaction_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=TransactionListResponse)
async def get_transactions(
    user_id: Optional[int] = Query(None, description="Filter by user ID (custom auto-increment)"),
    merchant_id: Optional[int] = Query(None, description="Filter by merchant ID (custom auto-increment)"),
    type: Optional[str] = Query(None, description="Filter by transaction type (PURCHASE/PAYMENT)"),
    status: Optional[str] = Query(None, description="Filter by transaction status (APPROVED/REJECTED)"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: UserAuth = Depends(require_transactions_read),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> TransactionListResponse:
    """Get transactions with filters and pagination. Requires transactions:read permission."""
    logger.info("Getting transactions with filters",
               user_id=user_id,
               merchant_id=merchant_id,
               type=type,
               status=status,
               from_date=from_date,
               to_date=to_date,
               page=page,
               size=size,
               requested_by=current_user.email)
    
    # Convert string filters to enums if provided
    from app.common.types import TransactionType, TransactionStatus
    
    transaction_type = None
    if type:
        try:
            transaction_type = TransactionType(type.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid transaction type: {type}")
    
    transaction_status = None
    if status:
        try:
            transaction_status = TransactionStatus(status.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid transaction status: {status}")
    
    filters = TransactionFilter(
        user_id=user_id,
        merchant_id=merchant_id,
        type=transaction_type,
        status=transaction_status,
        from_date=from_date,
        to_date=to_date,
        page=page,
        size=size
    )
    
    return await transaction_service.get_transactions_with_filters(filters)


@router.get("/summary", response_model=TransactionSummary)
async def get_transaction_summary(
    user_id: Optional[int] = Query(None, description="Filter by user ID (custom auto-increment)"),
    merchant_id: Optional[int] = Query(None, description="Filter by merchant ID (custom auto-increment)"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    transaction_service: TransactionService = Depends(get_transaction_service)
) -> TransactionSummary:
    """Get transaction summary statistics."""
    logger.info("Getting transaction summary",
               user_id=user_id,
               merchant_id=merchant_id,
               from_date=from_date,
               to_date=to_date)
    
    try:
        return await transaction_service.get_transaction_summary(
            user_id=user_id,
            merchant_id=merchant_id,
            from_date=from_date,
            to_date=to_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
