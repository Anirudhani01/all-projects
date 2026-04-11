from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException, status
from app.modules.merchants.service import MerchantService
from app.modules.merchants.schemas import (
    CreateMerchantRequest,
    UpdateFeeRequest,
    MerchantResponse,
    MerchantListResponse,
    FeeHistoryResponse
)
from app.modules.wallet.schemas import MerchantWalletBalanceResponse, MerchantWalletSummaryResponse
from app.api.dependencies import get_merchant_service
from app.auth.dependencies import get_current_active_user
from app.auth.models import UserAuth
from app.rbac.middleware import (
    require_merchants_write, require_merchants_read, require_admin_role, require_merchant_role
)
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/merchants", tags=["merchants"])


@router.post("/", response_model=MerchantResponse, status_code=201)
async def create_merchant(
    request: CreateMerchantRequest,
    current_user: UserAuth = Depends(require_merchants_write),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantResponse:
    """Create a new merchant. Requires merchants:write permission."""
    logger.info("Creating merchant", name=request.name, fee_pct=request.fee_pct, created_by=current_user.email)
    return await merchant_service.onboard_merchant(request)


@router.get("/", response_model=MerchantListResponse)
async def get_all_merchants(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: UserAuth = Depends(require_merchants_read),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantListResponse:
    """Get all merchants with pagination. Requires merchants:read permission."""
    logger.info("Getting all merchants", page=page, size=size, requested_by=current_user.email)
    return await merchant_service.get_all_merchants(page=page, size=size)


@router.get("/me", response_model=MerchantResponse)
async def get_my_merchant_profile(
    current_user: UserAuth = Depends(require_merchant_role),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantResponse:
    """Get current merchant's profile. Requires merchant role."""
    logger.info("Getting merchant profile", requested_by=current_user.email)
    return await merchant_service.get_merchant_by_email(current_user.email)


@router.patch("/me", response_model=MerchantResponse)
async def update_my_merchant_profile(
    request: UpdateFeeRequest,
    current_user: UserAuth = Depends(require_merchant_role),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantResponse:
    """Update current merchant's fee. Requires merchant role."""
    logger.info("Updating merchant fee", 
               new_fee_pct=request.fee_pct,
               updated_by=current_user.email)
    merchant = await merchant_service.get_merchant_by_email(current_user.email)
    return await merchant_service.update_merchant_fee(str(merchant.id), request)


@router.get("/{merchant_id}", response_model=MerchantResponse)
async def get_merchant(
    merchant_id: str,
    current_user: UserAuth = Depends(require_merchants_read),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantResponse:
    """Get merchant details. Requires merchants:read permission."""
    logger.info("Getting merchant", merchant_id=merchant_id, requested_by=current_user.email)
    return await merchant_service.get_merchant(merchant_id)


@router.patch("/{merchant_id}/fee", response_model=MerchantResponse)
async def update_merchant_fee(
    merchant_id: str,
    request: UpdateFeeRequest,
    current_user: UserAuth = Depends(require_merchants_write),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantResponse:
    """Update merchant fee percentage. Requires merchants:write permission."""
    logger.info("Updating merchant fee", 
               merchant_id=merchant_id, 
               new_fee_pct=request.fee_pct,
               updated_by=current_user.email)
    return await merchant_service.update_merchant_fee(merchant_id, request)


@router.get("/{merchant_id}/fee-history", response_model=FeeHistoryResponse)
async def get_merchant_fee_history(
    merchant_id: str,
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: UserAuth = Depends(require_merchants_read),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> FeeHistoryResponse:
    """Get merchant fee history. Requires merchants:read permission."""
    logger.info("Getting merchant fee history", 
               merchant_id=merchant_id,
               from_date=from_date,
               to_date=to_date,
               page=page,
               size=size,
               requested_by=current_user.email)
    return await merchant_service.get_fee_history(
        merchant_id=merchant_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        size=size
    )


@router.get("/{merchant_id}/wallet-balance", response_model=MerchantWalletBalanceResponse)
async def get_merchant_wallet_balance(
    merchant_id: str,
    current_user: UserAuth = Depends(require_merchants_read),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantWalletBalanceResponse:
    """Get merchant's wallet balance. Requires merchants:read permission."""
    # Additional check: Merchants can only see their own balance unless admin
    if current_user.role == "merchant" and str(current_user.user_id) != merchant_id:
        # Check if user has admin role for accessing other merchants
        from app.rbac.service import RBACService
        from app.api.dependencies import get_rbac_service
        
        rbac_service = get_rbac_service()
        is_admin = await rbac_service.check_user_role(str(current_user.user_id), "admin")
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only access your own wallet balance."
            )
    
    logger.info("Getting merchant wallet balance", merchant_id=merchant_id, requested_by=current_user.email)
    
    # Get wallet balance using wallet service
    from app.modules.wallet.repository import WalletRepository
    from app.modules.wallet.service import WalletService
    from app.db.mongo import mongodb
    
    wallet_repo = WalletRepository(mongodb.get_database())
    wallet_service = WalletService(wallet_repo)
    
    from bson import ObjectId
    merchant_obj_id = ObjectId(merchant_id)
    
    # Get merchant info and balance
    merchant_info = await wallet_service.wallet_repo.get_merchant_by_id(merchant_obj_id)
    if not merchant_info:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    balance = await wallet_service.get_merchant_wallet_balance(merchant_obj_id)
    
    return MerchantWalletBalanceResponse(
        merchant_id=merchant_id,
        merchant_name=merchant_info.get("name", "Unknown"),
        wallet_balance=balance,
        total_received=merchant_info.get("total_received", 0.0),
        fee_percentage=merchant_info.get("current_fee_pct", 0.0)
    )


@router.get("/{merchant_id}/wallet-summary", response_model=MerchantWalletSummaryResponse)
async def get_merchant_wallet_summary(
    merchant_id: str,
    current_user: UserAuth = Depends(require_merchants_read),
    merchant_service: MerchantService = Depends(get_merchant_service)
) -> MerchantWalletSummaryResponse:
    """Get merchant wallet summary. Requires merchants:read permission."""
    # Additional check: Merchants can only see their own summary unless admin
    if current_user.role == "merchant" and str(current_user.user_id) != merchant_id:
        # Check if user has admin role for accessing other merchants
        from app.rbac.service import RBACService
        from app.api.dependencies import get_rbac_service
        
        rbac_service = get_rbac_service()
        is_admin = await rbac_service.check_user_role(str(current_user.user_id), "admin")
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. You can only access your own wallet summary."
            )
    
    logger.info("Getting merchant wallet summary", merchant_id=merchant_id, requested_by=current_user.email)
    
    # Get wallet summary using wallet service
    from app.modules.wallet.repository import WalletRepository
    from app.modules.wallet.service import WalletService
    from app.db.mongo import mongodb
    
    wallet_repo = WalletRepository(mongodb.get_database())
    wallet_service = WalletService(wallet_repo)
    
    from bson import ObjectId
    merchant_obj_id = ObjectId(merchant_id)
    summary = await wallet_service.get_merchant_wallet_summary(merchant_obj_id)
    
    return MerchantWalletSummaryResponse(
        merchant_id=summary["merchant_id"],
        merchant_name=summary["merchant_name"],
        current_balance=summary["current_balance"],
        total_received=summary["total_received"],
        total_fees=summary["total_fees"],
        transaction_count=summary["transaction_count"],
        fee_percentage=summary["fee_percentage"]
    )
