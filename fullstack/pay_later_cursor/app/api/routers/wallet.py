from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from bson import ObjectId
import structlog

from app.db.mongo import get_database
from app.modules.wallet.repository import WalletRepository
from app.modules.wallet.service import WalletService
from app.modules.wallet.schemas import (
    AddToWalletRequest,
    WalletPaymentRequest,
    WalletTransactionFilter,
    WalletAddResponse,
    WalletPaymentResponse,
    UserCreditInfoResponse,
    MerchantWalletBalanceResponse,
    WalletTransactionResponse,
    UserMerchantUsageResponse,
    MerchantWalletSummaryResponse,
    WalletTransactionsResponse,
    WalletErrorResponse,
    WalletSummaryResponse,
    WalletHealthResponse
)
from app.common.exceptions import UserNotFound, MerchantNotFound, InsufficientBalance
from app.common.types import UserRole

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/wallet", tags=["Wallet"])


async def get_wallet_service() -> WalletService:
    """Dependency to get wallet service instance."""
    database = await get_database()
    wallet_repo = WalletRepository(database)
    return WalletService(wallet_repo)


def get_current_user_dependency():
    """Local dependency to avoid circular import."""
    from app.auth.dependencies import get_current_user
    return get_current_user


@router.post("/add-to-merchant", response_model=WalletAddResponse)
async def add_to_merchant_wallet(
    request: AddToWalletRequest,
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Add money to merchant wallet from user's credit."""
    try:
        # Validate user role
        if current_user.role != UserRole.USER:
            raise HTTPException(status_code=403, detail="Only users can add money to merchant wallets")
        
        # Convert user_id to ObjectId
        try:
            user_id = ObjectId(current_user.user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        
        # Handle merchant_id - it could be either ObjectId or custom_merchant_id
        try:
            # First try to convert as ObjectId
            merchant_id = ObjectId(request.merchant_id)
        except:
            # If that fails, treat it as custom_merchant_id and look up the ObjectId
            try:
                custom_merchant_id = int(request.merchant_id)
                # Get the merchant ObjectId from custom_merchant_id
                database = await get_database()
                merchant_doc = await database.merchants.find_one({"custom_merchant_id": custom_merchant_id})
                if not merchant_doc:
                    raise HTTPException(status_code=404, detail=f"Merchant not found with custom ID: {custom_merchant_id}")
                merchant_id = merchant_doc["_id"]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid merchant ID format: {request.merchant_id}")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing merchant ID: {str(e)}")
        
        # Process wallet add operation
        result = await wallet_service.add_to_merchant_wallet(
            user_id=user_id,
            merchant_id=merchant_id,
            amount=request.amount,
            idempotency_key=request.idempotency_key
        )
        
        logger.info("Wallet add operation completed", 
                   user_id=str(user_id),
                   merchant_id=str(merchant_id),
                   amount=request.amount,
                   transaction_id=result["transaction_id"])
        
        return WalletAddResponse(
            transaction_id=result["transaction_id"],
            amount=result["amount"],
            fee_amount=result["fee_amount"],
            total_amount=result["total_amount"],
            merchant_name=result["merchant_name"],
            merchant_balance_before=result["merchant_balance_before"],
            merchant_balance_after=result["merchant_balance_after"],
            user_credit_before=result["user_credit_before"],
            user_credit_after=result["user_credit_after"]
        )
        
    except ValueError as e:
        logger.error("Validation error in wallet add", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except InsufficientBalance as e:
        logger.error("Insufficient balance for wallet add", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in wallet add", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/process-payment", response_model=WalletPaymentResponse)
async def process_wallet_payment(
    request: WalletPaymentRequest,
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Process payment from user to PayLater."""
    try:
        # Validate user role
        if current_user.role != UserRole.USER:
            raise HTTPException(status_code=403, detail="Only users can make payments")
        
        # Convert string ID to ObjectId
        try:
            user_id = ObjectId(current_user.user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        
        # Process payment
        result = await wallet_service.process_wallet_payment(
            user_id=user_id,
            amount=request.amount,
            idempotency_key=request.idempotency_key
        )
        
        logger.info("Wallet payment processed", 
                   user_id=str(user_id),
                   amount=request.amount,
                   transaction_id=result["transaction_id"])
        
        return WalletPaymentResponse(
            transaction_id=result["transaction_id"],
            amount=result["amount"],
            outstanding_before=result["outstanding_before"],
            outstanding_after=result["outstanding_after"],
            available_credit_before=result["available_credit_before"],
            available_credit_after=result["available_credit_after"]
        )
        
    except ValueError as e:
        logger.error("Validation error in wallet payment", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in wallet payment", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user-credit/{user_id}", response_model=UserCreditInfoResponse)
async def get_user_credit_info(
    user_id: str = Path(..., description="User ID"),
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Get user's credit information."""
    try:
        # Validate access - users can only see their own credit info, admins can see all
        if (current_user.role == UserRole.USER and 
            str(current_user.user_id) != user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert string ID to ObjectId
        try:
            user_obj_id = ObjectId(user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        
        # Get credit info
        credit_info = await wallet_service.get_user_credit_info(user_obj_id)
        if not credit_info:
            raise HTTPException(status_code=404, detail="User credit info not found")
        
        logger.info("Retrieved user credit info", 
                   user_id=user_id,
                   available_credit=credit_info["available_credit"])
        
        return UserCreditInfoResponse(
            user_id=user_id,
            credit_limit=credit_info["credit_limit"],
            outstanding_amount=credit_info["outstanding_amount"],
            available_credit=credit_info["available_credit"],
            total_merchant_usage=credit_info["total_merchant_usage"],
            reached_limit=credit_info["available_credit"] <= 0
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user credit info", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/merchant-balance/{merchant_id}", response_model=MerchantWalletBalanceResponse)
async def get_merchant_wallet_balance(
    merchant_id: str = Path(..., description="Merchant ID"),
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Get merchant's wallet balance."""
    try:
        # Validate access - merchants can only see their own balance, admins can see all
        if (current_user.role == UserRole.MERCHANT and 
            str(current_user.user_id) != merchant_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert string ID to ObjectId
        try:
            merchant_obj_id = ObjectId(merchant_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid merchant ID format: {str(e)}")
        
        # Get merchant info and balance
        merchant_info = await wallet_service.wallet_repo.get_merchant_by_id(merchant_obj_id)
        if not merchant_info:
            raise HTTPException(status_code=404, detail="Merchant not found")
        
        balance = await wallet_service.get_merchant_wallet_balance(merchant_obj_id)
        
        logger.info("Retrieved merchant wallet balance", 
                   merchant_id=merchant_id,
                   balance=balance)
        
        return MerchantWalletBalanceResponse(
            merchant_id=merchant_id,
            merchant_name=merchant_info.get("name", "Unknown"),
            wallet_balance=balance,
            total_received=merchant_info.get("total_received", 0.0),
            fee_percentage=merchant_info.get("current_fee_pct", 0.0)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting merchant wallet balance", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/transactions", response_model=WalletTransactionsResponse)
async def get_wallet_transactions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    merchant_id: Optional[str] = Query(None, description="Filter by merchant ID"),
    limit: int = Query(50, ge=1, le=1000, description="Number of transactions to return"),
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Get wallet transactions with optional filters."""
    try:
        # Validate access based on role
        if current_user.role == UserRole.USER:
            # Users can only see their own transactions
            if user_id and str(current_user.user_id) != user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            user_id = str(current_user.user_id)
        elif current_user.role == UserRole.MERCHANT:
            # Merchants can only see transactions involving them
            if merchant_id and str(current_user.user_id) != merchant_id:
                raise HTTPException(status_code=403, detail="Access denied")
            merchant_id = str(current_user.user_id)
        # Admins can see all transactions
        
        # Convert string IDs to ObjectId
        user_obj_id = None
        merchant_obj_id = None
        
        if user_id:
            try:
                user_obj_id = ObjectId(user_id)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        
        if merchant_id:
            try:
                merchant_obj_id = ObjectId(merchant_id)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid merchant ID format: {str(e)}")
        
        # Get transactions
        transactions = await wallet_service.get_wallet_transactions(
            user_id=user_obj_id,
            merchant_id=merchant_obj_id,
            limit=limit
        )
        
        # Convert to response format
        transaction_responses = []
        for transaction in transactions:
            transaction_responses.append(WalletTransactionResponse(
                transaction_id=str(transaction["_id"]),
                type=transaction["type"],
                user_id=str(transaction["user_id"]),
                merchant_id=str(transaction["merchant_id"]) if transaction.get("merchant_id") else None,
                amount=transaction["amount"],
                fee_amount=transaction.get("fee_amount", 0.0),
                total_amount=transaction.get("total_amount", transaction["amount"]),
                currency=transaction.get("currency", "INR"),
                status=transaction["status"],
                merchant_wallet_balance_before=transaction.get("merchant_wallet_balance_before"),
                merchant_wallet_balance_after=transaction.get("merchant_wallet_balance_after"),
                user_credit_before=transaction.get("user_credit_before"),
                user_credit_after=transaction.get("user_credit_after"),
                reason=transaction.get("reason"),
                created_at=transaction["created_at"]
            ))
        
        logger.info("Retrieved wallet transactions", 
                   count=len(transaction_responses),
                   user_id=user_id,
                   merchant_id=merchant_id)
        
        return WalletTransactionsResponse(
            transactions=transaction_responses,
            total_count=len(transaction_responses),
            limit=limit,
            has_more=len(transaction_responses) == limit
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting wallet transactions", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user-merchant-usage/{user_id}", response_model=UserMerchantUsageResponse)
async def get_user_merchant_usage(
    user_id: str = Path(..., description="User ID"),
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Get user's usage across all merchants."""
    try:
        # Validate access - users can only see their own usage, admins can see all
        if (current_user.role == UserRole.USER and 
            str(current_user.user_id) != user_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert string ID to ObjectId
        try:
            user_obj_id = ObjectId(user_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid user ID format: {str(e)}")
        
        # Get usage info
        usage_info = await wallet_service.get_user_merchant_usage(user_obj_id)
        
        logger.info("Retrieved user merchant usage", 
                   user_id=user_id,
                   total_usage=usage_info["total_usage"])
        
        return UserMerchantUsageResponse(
            user_id=user_id,
            total_usage=usage_info["total_usage"],
            merchant_breakdown=usage_info["merchant_breakdown"],
            credit_limit=usage_info["credit_limit"],
            available_credit=usage_info["available_credit"],
            outstanding_amount=usage_info["outstanding_amount"],
            merchant_count=usage_info["merchant_count"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting user merchant usage", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/merchant-summary/{merchant_id}", response_model=MerchantWalletSummaryResponse)
async def get_merchant_wallet_summary(
    merchant_id: str = Path(..., description="Merchant ID"),
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Get merchant wallet summary."""
    try:
        # Validate access - merchants can only see their own summary, admins can see all
        if (current_user.role == UserRole.MERCHANT and 
            str(current_user.user_id) != merchant_id):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Convert string ID to ObjectId
        try:
            merchant_obj_id = ObjectId(merchant_id)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid merchant ID format: {str(e)}")
        
        # Get summary
        summary = await wallet_service.get_merchant_wallet_summary(merchant_obj_id)
        
        logger.info("Retrieved merchant wallet summary", 
                   merchant_id=merchant_id,
                   current_balance=summary["current_balance"])
        
        return MerchantWalletSummaryResponse(
            merchant_id=summary["merchant_id"],
            merchant_name=summary["merchant_name"],
            current_balance=summary["current_balance"],
            total_received=summary["total_received"],
            total_fees=summary["total_fees"],
            transaction_count=summary["transaction_count"],
            fee_percentage=summary["fee_percentage"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting merchant wallet summary", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary", response_model=WalletSummaryResponse)
async def get_wallet_summary(
    wallet_service: WalletService = Depends(get_wallet_service),
    current_user = Depends(get_current_user_dependency())
):
    """Get overall wallet system summary (admin only)."""
    try:
        # Only admins can access system summary
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get summary data from database
        database = await get_database()
        
        # Count users with credit limits
        total_users = await database.user_balances.count_documents({})
        
        # Count merchants with wallets
        total_merchants = await database.merchants.count_documents({})
        
        # Count wallet transactions
        total_transactions = await database.transactions.count_documents({
            "type": {"$in": ["wallet_add", "wallet_payment"]}
        })
        
        # Calculate total outstanding amount
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$outstanding_amount"}}}
        ]
        result = list(await database.user_balances.aggregate(pipeline))
        total_outstanding = result[0]["total"] if result else 0.0
        
        # Calculate total fees collected
        pipeline = [
            {"$match": {"type": "wallet_add"}},
            {"$group": {"_id": None, "total": {"$sum": "$fee_amount"}}}
        ]
        result = list(await database.transactions.aggregate(pipeline))
        total_fees_collected = result[0]["total"] if result else 0.0
        
        # Count active wallets (merchants with balance > 0)
        active_wallets = await database.merchants.count_documents({
            "wallet_balance": {"$gt": 0}
        })
        
        logger.info("Retrieved wallet system summary", 
                   total_users=total_users,
                   total_merchants=total_merchants,
                   total_transactions=total_transactions)
        
        return WalletSummaryResponse(
            total_users=total_users,
            total_merchants=total_merchants,
            total_transactions=total_transactions,
            total_outstanding=total_outstanding,
            total_fees_collected=total_fees_collected,
            active_wallets=active_wallets
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting wallet summary", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health", response_model=WalletHealthResponse)
async def get_wallet_health(
    wallet_service: WalletService = Depends(get_wallet_service)
):
    """Get wallet system health status."""
    try:
        from datetime import datetime
        
        # Check database connection
        database = await get_database()
        await database.command("ping")
        database_connected = True
        
        # Check services health
        services_healthy = True
        
        logger.info("Wallet system health check completed", 
                   database_connected=database_connected,
                   services_healthy=services_healthy)
        
        return WalletHealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database_connected=database_connected,
            services_healthy=services_healthy
        )
        
    except Exception as e:
        logger.error("Wallet system health check failed", error=str(e))
        return WalletHealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database_connected=False,
            services_healthy=False
        )
