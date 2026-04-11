"""
Merchant management endpoints.
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_merchants():
    """Get merchants list."""
    # TODO: Implement get merchants list
    return {"message": "Get merchants list endpoint - to be implemented"}


@router.post("/")
async def register_merchant():
    """Register new merchant."""
    # TODO: Implement merchant registration
    return {"message": "Register merchant endpoint - to be implemented"}


@router.get("/{merchant_id}")
async def get_merchant_details(merchant_id: str):
    """Get merchant details."""
    # TODO: Implement get merchant details
    return {"message": f"Get merchant details endpoint - to be implemented for merchant {merchant_id}"}
