"""
API endpoint tests for wallet functionality.
"""

import pytest
from httpx import AsyncClient
from bson import ObjectId

from app.main import app


class TestWalletEndpoints:
    """Test wallet API endpoints."""
    
    @pytest.mark.asyncio
    async def test_wallet_health_endpoint(self):
        """Test wallet health endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/wallet/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "timestamp" in data
            assert data["version"] == "1.0.0"
            assert data["database_connected"] is True
            assert data["services_healthy"] is True
    
    @pytest.mark.asyncio
    async def test_wallet_summary_endpoint_unauthorized(self):
        """Test wallet summary endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/wallet/summary")
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_add_to_merchant_wallet_unauthorized(self):
        """Test add to merchant wallet endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "merchant_id": str(ObjectId()),
                "amount": 100.0,
                "idempotency_key": "test_key"
            }
            
            response = await client.post("/api/v1/wallet/add-to-merchant", json=payload)
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_process_payment_unauthorized(self):
        """Test process payment endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "amount": 100.0,
                "idempotency_key": "test_key"
            }
            
            response = await client.post("/api/v1/wallet/process-payment", json=payload)
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_credit_info_unauthorized(self):
        """Test get user credit info endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_id = str(ObjectId())
            response = await client.get(f"/api/v1/wallet/user-credit/{user_id}")
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_merchant_wallet_balance_unauthorized(self):
        """Test get merchant wallet balance endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            merchant_id = str(ObjectId())
            response = await client.get(f"/api/v1/wallet/merchant-balance/{merchant_id}")
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_wallet_transactions_unauthorized(self):
        """Test get wallet transactions endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/wallet/transactions")
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_user_merchant_usage_unauthorized(self):
        """Test get user merchant usage endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_id = str(ObjectId())
            response = await client.get(f"/api/v1/wallet/user-merchant-usage/{user_id}")
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_merchant_wallet_summary_unauthorized(self):
        """Test get merchant wallet summary endpoint without authentication."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            merchant_id = str(ObjectId())
            response = await client.get(f"/api/v1/wallet/merchant-summary/{merchant_id}")
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_add_to_merchant_wallet_invalid_amount(self):
        """Test add to merchant wallet with invalid amount."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "merchant_id": str(ObjectId()),
                "amount": -100.0,  # Invalid negative amount
                "idempotency_key": "test_key"
            }
            
            response = await client.post("/api/v1/wallet/add-to-merchant", json=payload)
            
            # Should return 401 Unauthorized without auth, but if we had auth, it would be 422
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_add_to_merchant_wallet_missing_fields(self):
        """Test add to merchant wallet with missing required fields."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "amount": 100.0
                # Missing merchant_id
            }
            
            response = await client.post("/api/v1/wallet/add-to-merchant", json=payload)
            
            # Should return 401 Unauthorized without auth, but if we had auth, it would be 422
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_process_payment_invalid_amount(self):
        """Test process payment with invalid amount."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            payload = {
                "amount": 0.0,  # Invalid zero amount
                "idempotency_key": "test_key"
            }
            
            response = await client.post("/api/v1/wallet/process-payment", json=payload)
            
            # Should return 401 Unauthorized without auth, but if we had auth, it would be 422
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_wallet_transactions_with_filters(self):
        """Test get wallet transactions with query parameters."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            params = {
                "user_id": str(ObjectId()),
                "merchant_id": str(ObjectId()),
                "limit": 10
            }
            
            response = await client.get("/api/v1/wallet/transactions", params=params)
            
            # Should return 401 Unauthorized without auth
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_wallet_transactions_invalid_limit(self):
        """Test get wallet transactions with invalid limit."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            params = {
                "limit": 0  # Invalid limit
            }
            
            response = await client.get("/api/v1/wallet/transactions", params=params)
            
            # Should return 401 Unauthorized without auth, but if we had auth, it would be 422
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_user_id_format(self):
        """Test endpoints with invalid user ID format."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test with invalid ObjectId format
            response = await client.get("/api/v1/wallet/user-credit/invalid_id")
            
            # Should return 401 Unauthorized without auth, but if we had auth, it would be 400
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_invalid_merchant_id_format(self):
        """Test endpoints with invalid merchant ID format."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test with invalid ObjectId format
            response = await client.get("/api/v1/wallet/merchant-balance/invalid_id")
            
            # Should return 401 Unauthorized without auth, but if we had auth, it would be 400
            assert response.status_code == 401
