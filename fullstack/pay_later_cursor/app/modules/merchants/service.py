from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.modules.merchants.models import Merchant, MerchantFeeHistory
from app.modules.merchants.repository import MerchantRepository
from app.modules.merchants.schemas import (
    CreateMerchantRequest, 
    UpdateFeeRequest, 
    MerchantResponse, 
    MerchantListResponse,
    FeeHistoryResponse,
    FeeHistoryEntry
)
from app.common.exceptions import MerchantNotFound, DuplicateEntity, InvalidFeePercentage
from app.common.validators import normalize_string, validate_fee_percentage
import structlog

logger = structlog.get_logger(__name__)


class MerchantService:
    """Service for merchant operations."""
    
    def __init__(self, merchant_repository: MerchantRepository):
        self.merchant_repository = merchant_repository
    
    async def onboard_merchant(self, request: CreateMerchantRequest) -> MerchantResponse:
        """Onboard a new merchant with initial fee."""
        # Normalize and validate input
        name = normalize_string(request.name, "name")
        fee_pct = validate_fee_percentage(request.fee_pct)
        
        # Check if merchant already exists
        existing_merchant = await self.merchant_repository.get_merchant_by_name(name)
        if existing_merchant:
            raise DuplicateEntity("Merchant", "name", name)
        
        # Create merchant
        merchant = Merchant(
            name=name,
            email=request.email,
            current_fee_pct=fee_pct
        )
        
        created_merchant = await self.merchant_repository.create_merchant(merchant)
        
        # Create initial fee history entry
        fee_history = MerchantFeeHistory(
            merchant_id=created_merchant._id,
            fee_pct=fee_pct,
            effective_from=created_merchant.created_at,
            changed_by="system"
        )
        
        await self.merchant_repository.create_fee_history_entry(fee_history)
        
        logger.info("Merchant onboarded successfully", 
                   merchant_id=str(created_merchant._id), 
                   custom_merchant_id=created_merchant.custom_merchant_id,
                   name=name,
                   fee_pct=fee_pct)
        
        return MerchantResponse(
            id=str(created_merchant._id),
            merchant_id=created_merchant.custom_merchant_id,
            name=created_merchant.name,
            email=created_merchant.email,
            current_fee_pct=created_merchant.current_fee_pct,
            created_at=created_merchant.created_at,
            updated_at=created_merchant.updated_at
        )
    
    async def get_merchant(self, merchant_id: str) -> MerchantResponse:
        """Get merchant by ID."""
        try:
            merchant_obj_id = ObjectId(merchant_id)
        except Exception:
            raise MerchantNotFound(f"Invalid merchant ID: {merchant_id}")
        
        merchant = await self.merchant_repository.get_merchant_by_id(merchant_obj_id)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found: {merchant_id}")
        
        return MerchantResponse(
            id=str(merchant._id),
            merchant_id=merchant.custom_merchant_id,
            name=merchant.name,
            email=merchant.email,
            current_fee_pct=merchant.current_fee_pct,
            created_at=merchant.created_at,
            updated_at=merchant.updated_at
        )
    
    async def get_all_merchants(
        self, 
        page: int = 1,
        size: int = 10
    ) -> MerchantListResponse:
        """Get all merchants with pagination."""
        merchants, total = await self.merchant_repository.get_all_merchants(
            page=page,
            size=size
        )
        
        merchant_responses = [
            MerchantResponse(
                id=str(merchant._id),
                merchant_id=merchant.custom_merchant_id,
                name=merchant.name,
                current_fee_pct=merchant.current_fee_pct,
                created_at=merchant.created_at,
                updated_at=merchant.updated_at
            )
            for merchant in merchants
        ]
        
        has_next = (page * size) < total
        
        return MerchantListResponse(
            merchants=merchant_responses,
            total=total,
            page=page,
            size=size,
            has_next=has_next
        )
    
    async def update_merchant_fee(
        self, 
        merchant_id: str, 
        request: UpdateFeeRequest,
        changed_by: str = "system"
    ) -> MerchantResponse:
        """Update merchant fee percentage."""
        try:
            merchant_obj_id = ObjectId(merchant_id)
        except Exception:
            raise MerchantNotFound(f"Invalid merchant ID: {merchant_id}")
        
        # Validate fee percentage
        new_fee_pct = validate_fee_percentage(request.fee_pct)
        
        # Get current merchant
        merchant = await self.merchant_repository.get_merchant_by_id(merchant_obj_id)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found: {merchant_id}")
        
        old_fee_pct = merchant.current_fee_pct
        
        # Update merchant fee
        updated_merchant = await self.merchant_repository.update_merchant_fee(
            merchant_obj_id, new_fee_pct
        )
        
        if not updated_merchant:
            raise MerchantNotFound(f"Merchant not found: {merchant_id}")
        
        # Create fee history entry
        fee_history = MerchantFeeHistory(
            merchant_id=merchant_obj_id,
            fee_pct=new_fee_pct,
            effective_from=datetime.utcnow(),
            changed_by=changed_by
        )
        
        await self.merchant_repository.create_fee_history_entry(fee_history)
        
        logger.info("Merchant fee updated", 
                   merchant_id=merchant_id,
                   old_fee=old_fee_pct,
                   new_fee=new_fee_pct,
                   changed_by=changed_by)
        
        return MerchantResponse(
            id=str(updated_merchant._id),
            merchant_id=updated_merchant.custom_merchant_id,
            name=updated_merchant.name,
            email=updated_merchant.email,
            current_fee_pct=updated_merchant.current_fee_pct,
            created_at=updated_merchant.created_at,
            updated_at=updated_merchant.updated_at
        )
    
    async def get_fee_history(
        self, 
        merchant_id: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 10
    ) -> FeeHistoryResponse:
        """Get fee history for a merchant."""
        try:
            merchant_obj_id = ObjectId(merchant_id)
        except Exception:
            raise MerchantNotFound(f"Invalid merchant ID: {merchant_id}")
        
        # Verify merchant exists
        merchant = await self.merchant_repository.get_merchant_by_id(merchant_obj_id)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found: {merchant_id}")
        
        # Get fee history
        entries, total = await self.merchant_repository.get_fee_history(
            merchant_obj_id,
            from_date=from_date,
            to_date=to_date,
            page=page,
            size=size
        )
        
        # Convert to response format
        history_entries = [
            FeeHistoryEntry(
                id=str(entry._id),
                fee_pct=entry.fee_pct,
                effective_from=entry.effective_from,
                changed_by=entry.changed_by,
                created_at=entry.created_at
            )
            for entry in entries
        ]
        
        return FeeHistoryResponse(
            merchant_id=merchant_id,
            history=history_entries,
            total=total
        )
    
    async def check_merchant_exists(self, merchant_id: ObjectId) -> Merchant:
        """Check if merchant exists and return merchant object."""
        merchant = await self.merchant_repository.get_merchant_by_id(merchant_id)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found: {merchant_id}")
        return merchant
    
    async def get_current_fee_for_transaction(self, merchant_id: ObjectId) -> float:
        """Get current fee percentage for transaction processing."""
        fee_pct = await self.merchant_repository.get_current_fee(merchant_id)
        if fee_pct is None:
            raise MerchantNotFound(f"Merchant not found: {merchant_id}")
        return fee_pct
    
    # Methods for working with custom merchant IDs
    async def check_merchant_exists_by_custom_id(self, custom_merchant_id: int) -> Merchant:
        """Check if merchant exists and return merchant object using custom merchant ID."""
        merchant = await self.merchant_repository.get_merchant_by_custom_id(custom_merchant_id)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found with custom ID: {custom_merchant_id}")
        return merchant
    
    async def get_current_fee_for_transaction_by_custom_id(self, custom_merchant_id: int) -> float:
        """Get current fee percentage for transaction processing using custom merchant ID."""
        merchant = await self.merchant_repository.get_merchant_by_custom_id(custom_merchant_id)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found with custom ID: {custom_merchant_id}")
        return merchant.current_fee_pct

    async def get_merchant_by_email(self, email: str) -> MerchantResponse:
        """Get merchant by email address."""
        merchant = await self.merchant_repository.get_merchant_by_email(email)
        if not merchant:
            raise MerchantNotFound(f"Merchant not found with email: {email}")
        
        return MerchantResponse(
            id=str(merchant._id),
            merchant_id=merchant.custom_merchant_id,
            name=merchant.name,
            email=merchant.email,
            current_fee_pct=merchant.current_fee_pct,
            created_at=merchant.created_at,
            updated_at=merchant.updated_at
        )
