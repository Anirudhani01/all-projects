from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from app.modules.transactions.models import Transaction, IdempotencyKey
from app.modules.transactions.repository import TransactionRepository
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
from app.modules.users.service import UserService
from app.modules.merchants.service import MerchantService
from app.common.exceptions import (
    UserNotFound, 
    MerchantNotFound, 
    CreditLimitExceeded, 
    InsufficientBalance,
    DuplicateRequest,
    InvalidAmount
)
from app.common.validators import validate_amount, calculate_fee_amount, calculate_merchant_payout
from app.common.types import TransactionType, TransactionStatus, Currency
import structlog

logger = structlog.get_logger(__name__)


class TransactionService:
    """Service for transaction operations."""
    
    def __init__(
        self, 
        transaction_repository: TransactionRepository,
        user_service: UserService,
        merchant_service: MerchantService
    ):
        self.transaction_repository = transaction_repository
        self.user_service = user_service
        self.merchant_service = merchant_service
    
    async def process_purchase(
        self, 
        request: PurchaseRequest
    ) -> PurchaseResponse:
        """Process a purchase transaction with idempotency."""
        # Validate and normalize input
        amount = validate_amount(request.amount, "purchase_amount")
        
        # Use custom IDs directly
        custom_user_id = request.user_id
        custom_merchant_id = request.merchant_id
        
        # Check idempotency first
        idempotency_scope = f"user:{custom_user_id}"
        cached_response = await self.transaction_repository.check_idempotency_key(
            idempotency_scope, 
            request.idempotency_key or ""
        )
        
        if cached_response:
            logger.info("Returning cached response for idempotency key", 
                       key=request.idempotency_key)
            raise DuplicateRequest(request.idempotency_key or "unknown")
        
        # Validate user and merchant using custom IDs
        user = await self.user_service.check_user_status_by_custom_id(custom_user_id)
        merchant = await self.merchant_service.check_merchant_exists_by_custom_id(custom_merchant_id)
        
        # Get current fee percentage using custom merchant ID
        fee_percentage = await self.merchant_service.get_current_fee_for_transaction_by_custom_id(custom_merchant_id)
        
        # Calculate fee and payout amounts
        fee_amount = calculate_fee_amount(amount, fee_percentage)
        merchant_payout = calculate_merchant_payout(amount, fee_amount)
        
        # Get current user balance using custom user ID
        user_balance = await self.user_service.get_user_balance_for_transaction_by_custom_id(custom_user_id)
        
        # Check credit limit
        available_credit = max(0, user.credit_limit - user_balance.outstanding_amount)
        if amount > available_credit:
            # Create rejected transaction record
            rejected_transaction = Transaction(
                type=TransactionType.PURCHASE,
                user_id=user._id,  # Use MongoDB ObjectId for storage
                merchant_id=merchant._id,  # Use MongoDB ObjectId for storage
                amount=amount,
                currency=request.currency,
                status=TransactionStatus.REJECTED,
                applied_fee_pct=fee_percentage,
                fee_amount=fee_amount,
                merchant_payout_amount=merchant_payout,
                balance_before=user_balance.outstanding_amount,
                balance_after=user_balance.outstanding_amount,
                idempotency_key=request.idempotency_key,
                reason="Credit limit exceeded",
                metadata=request.metadata
            )
            
            await self.transaction_repository.create_transaction(rejected_transaction)
            
            # Create idempotency key for rejected transaction
            if request.idempotency_key:
                idempotency_key = IdempotencyKey(
                    scope=idempotency_scope,
                    key=request.idempotency_key,
                    ttl_expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                await self.transaction_repository.create_idempotency_key(idempotency_key)
            
            raise CreditLimitExceeded(
                str(custom_user_id), 
                amount, 
                available_credit
            )
        
        # Update user balance using custom user ID
        updated_balance = await self.user_service.update_user_balance_for_purchase_by_custom_id(
            custom_user_id, 
            amount, 
            user_balance.version
        )
        
        # Create approved transaction
        transaction = Transaction(
            type=TransactionType.PURCHASE,
            user_id=user._id,  # Use MongoDB ObjectId for storage
            merchant_id=merchant._id,  # Use MongoDB ObjectId for storage
            amount=amount,
            currency=request.currency,
            status=TransactionStatus.APPROVED,
            applied_fee_pct=fee_percentage,
            fee_amount=fee_amount,
            merchant_payout_amount=merchant_payout,
            balance_before=user_balance.outstanding_amount,
            balance_after=updated_balance.outstanding_amount,
            idempotency_key=request.idempotency_key,
            metadata=request.metadata
        )
        
        await self.transaction_repository.create_transaction(transaction)
        
        # Create idempotency key
        if request.idempotency_key:
            idempotency_key = IdempotencyKey(
                scope=idempotency_scope,
                key=request.idempotency_key,
                ttl_expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            await self.transaction_repository.create_idempotency_key(idempotency_key)
        
        logger.info("Purchase transaction processed successfully",
                   transaction_id=str(transaction._id),
                   user_id=custom_user_id,
                   merchant_id=custom_merchant_id,
                   amount=amount,
                   fee_amount=fee_amount)
        
        return PurchaseResponse(
            transaction=self._to_transaction_response_with_custom_ids(transaction, custom_user_id, custom_merchant_id),
            message="Purchase transaction processed successfully"
        )
    
    async def process_payment(
        self, 
        request: PaymentRequest
    ) -> PaymentResponse:
        """Process a payment transaction with idempotency."""
        # Validate and normalize input
        amount = validate_amount(request.amount, "payment_amount")
        
        # Use custom user ID directly
        custom_user_id = request.user_id
        
        # Check idempotency first
        idempotency_scope = f"user:{custom_user_id}"
        cached_response = await self.transaction_repository.check_idempotency_key(
            idempotency_scope, 
            request.idempotency_key or ""
        )
        
        if cached_response:
            logger.info("Returning cached response for idempotency key", 
                       key=request.idempotency_key)
            raise DuplicateRequest(request.idempotency_key or "unknown")
        
        # Validate user using custom ID
        user = await self.user_service.check_user_status_by_custom_id(custom_user_id)
        
        # Get current user balance using custom ID
        user_balance = await self.user_service.get_user_balance_for_transaction_by_custom_id(custom_user_id)
        
        # Validate payment amount
        if amount > user_balance.outstanding_amount:
            # Create rejected transaction record
            rejected_transaction = Transaction(
                type=TransactionType.PAYMENT,
                user_id=user._id,  # Use MongoDB ObjectId for storage
                amount=amount,
                currency=request.currency,
                status=TransactionStatus.REJECTED,
                balance_before=user_balance.outstanding_amount,
                balance_after=user_balance.outstanding_amount,
                idempotency_key=request.idempotency_key,
                reason="Payment amount exceeds outstanding balance",
                metadata=request.metadata
            )
            
            await self.transaction_repository.create_transaction(rejected_transaction)
            
            # Create idempotency key for rejected transaction
            if request.idempotency_key:
                idempotency_key = IdempotencyKey(
                    scope=idempotency_scope,
                    key=request.idempotency_key,
                    ttl_expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                await self.transaction_repository.create_idempotency_key(idempotency_key)
            
            raise InsufficientBalance(
                str(custom_user_id), 
                amount, 
                user_balance.outstanding_amount
            )
        
        # Update user balance using custom ID
        updated_balance = await self.user_service.update_user_balance_for_payment_by_custom_id(
            custom_user_id, 
            amount, 
            user_balance.version
        )
        
        # Create approved transaction
        transaction = Transaction(
            type=TransactionType.PAYMENT,
            user_id=user._id,  # Use MongoDB ObjectId for storage
            amount=amount,
            currency=request.currency,
            status=TransactionStatus.APPROVED,
            balance_before=user_balance.outstanding_amount,
            balance_after=updated_balance.outstanding_amount,
            idempotency_key=request.idempotency_key,
            metadata=request.metadata
        )
        
        await self.transaction_repository.create_transaction(transaction)
        
        # Create idempotency key
        if request.idempotency_key:
            idempotency_key = IdempotencyKey(
                scope=idempotency_scope,
                key=request.idempotency_key,
                ttl_expires_at=datetime.utcnow() + timedelta(hours=24)
            )
            await self.transaction_repository.create_idempotency_key(idempotency_key)
        
        logger.info("Payment transaction processed successfully",
                   transaction_id=str(transaction._id),
                   user_id=custom_user_id,
                   amount=amount)
        
        return PaymentResponse(
            transaction=self._to_transaction_response_with_custom_ids(transaction, custom_user_id, None),
            message="Payment transaction processed successfully"
        )
    
    async def get_transaction(
        self, 
        transaction_id: str
    ) -> TransactionResponse:
        """Get transaction by ID."""
        try:
            transaction_obj_id = ObjectId(transaction_id)
        except Exception:
            raise ValueError(f"Invalid transaction ID: {transaction_id}")
        
        transaction = await self.transaction_repository.get_transaction_by_id(transaction_obj_id)
        if not transaction:
            raise ValueError(f"Transaction not found: {transaction_id}")
        
        return self._to_transaction_response(transaction)
    
    async def get_transactions_with_filters(
        self, 
        filters: TransactionFilter
    ) -> TransactionListResponse:
        """Get transactions with filters and pagination."""
        # Convert filters to dictionary
        filter_dict = {}
        
        if filters.user_id:
            # Get user by custom ID to find the MongoDB ObjectId
            user = await self.user_service.check_user_status_by_custom_id(filters.user_id)
            filter_dict["user_id"] = user._id
        
        if filters.merchant_id:
            # Get merchant by custom ID to find the MongoDB ObjectId
            merchant = await self.merchant_service.check_merchant_exists_by_custom_id(filters.merchant_id)
            filter_dict["merchant_id"] = merchant._id
        
        if filters.type:
            filter_dict["type"] = filters.type
        
        if filters.status:
            filter_dict["status"] = filters.status
        
        if filters.from_date:
            filter_dict["from_date"] = filters.from_date
        
        if filters.to_date:
            filter_dict["to_date"] = filters.to_date
        
        transactions, total = await self.transaction_repository.get_transactions_with_filters(
            filter_dict,
            page=filters.page,
            size=filters.size
        )
        
        # Convert transactions to responses with custom IDs
        transaction_responses = []
        for transaction in transactions:
            # Get custom IDs for the transaction
            custom_user_id = None
            custom_merchant_id = None
            
            if transaction.user_id:
                try:
                    user = await self.user_service.check_user_status(transaction.user_id)
                    custom_user_id = user.user_id
                except UserNotFound:
                    # User no longer exists, skip this transaction or use None
                    custom_user_id = None
                    logger.warning("User not found for transaction", user_id=str(transaction.user_id))
            
            if transaction.merchant_id:
                try:
                    merchant = await self.merchant_service.check_merchant_exists(transaction.merchant_id)
                    custom_merchant_id = merchant.custom_merchant_id
                except MerchantNotFound:
                    # Merchant no longer exists, skip this transaction or use None
                    custom_merchant_id = None
                    logger.warning("Merchant not found for transaction", merchant_id=str(transaction.merchant_id))
            
            transaction_responses.append(
                self._to_transaction_response_with_custom_ids(
                    transaction, custom_user_id, custom_merchant_id
                )
            )
        
        has_next = (filters.page * filters.size) < total
        
        return TransactionListResponse(
            transactions=transaction_responses,
            total=total,
            page=filters.page,
            size=filters.size,
            has_next=has_next
        )
    
    async def get_transaction_summary(
        self,
        user_id: Optional[int] = None,
        merchant_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> TransactionSummary:
        """Get transaction summary statistics."""
        user_obj_id = None
        merchant_obj_id = None
        
        if user_id:
            # Get user by custom ID to find the MongoDB ObjectId
            user = await self.user_service.check_user_status_by_custom_id(user_id)
            user_obj_id = user._id
        
        if merchant_id:
            # Get merchant by custom ID to find the MongoDB ObjectId
            merchant = await self.merchant_service.check_merchant_exists_by_custom_id(merchant_id)
            merchant_obj_id = merchant._id
        
        summary_data = await self.transaction_repository.get_transaction_summary(
            user_id=user_obj_id,
            merchant_id=merchant_obj_id,
            from_date=from_date,
            to_date=to_date
        )
        
        return TransactionSummary(**summary_data)
    
    def _to_transaction_response(self, transaction: Transaction) -> TransactionResponse:
        """Convert Transaction model to TransactionResponse."""
        return TransactionResponse(
            id=str(transaction._id),
            type=transaction.type,
            user_id=str(transaction.user_id),
            merchant_id=str(transaction.merchant_id) if transaction.merchant_id else None,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            applied_fee_pct=transaction.applied_fee_pct,
            fee_amount=transaction.fee_amount,
            merchant_payout_amount=transaction.merchant_payout_amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
            reason=transaction.reason,
            metadata=transaction.metadata,
            created_at=transaction.created_at
        )
    
    def _to_transaction_response_with_custom_ids(
        self, 
        transaction: Transaction, 
        custom_user_id: Optional[int], 
        custom_merchant_id: Optional[int]
    ) -> TransactionResponse:
        """Convert Transaction model to TransactionResponse using custom IDs."""
        return TransactionResponse(
            id=str(transaction._id),
            type=transaction.type,
            user_id=custom_user_id,
            merchant_id=custom_merchant_id,
            amount=transaction.amount,
            currency=transaction.currency,
            status=transaction.status,
            applied_fee_pct=transaction.applied_fee_pct,
            fee_amount=transaction.fee_amount,
            merchant_payout_amount=transaction.merchant_payout_amount,
            balance_before=transaction.balance_before,
            balance_after=transaction.balance_after,
            reason=transaction.reason,
            metadata=transaction.metadata,
            created_at=transaction.created_at
        ) 