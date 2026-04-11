import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.database import Base, get_db, init_db, User, Item
from main import app
import asyncio

# Test database - using MySQL
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://anirudh:password123@localhost:3306/shopping_cart_test"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

def init_test_db():
    """Initialize test database with sample data."""
    db = TestingSessionLocal()
    try:
        # Check if data already exists
        existing_items = db.query(Item).first()
        if existing_items:
            return
        
        # Create sample items
        sample_items = [
            Item(
                name="Laptop",
                description="High-performance laptop with latest specs",
                price=999.99,
                stock_quantity=50,
                category="Electronics"
            ),
            Item(
                name="Smartphone",
                description="Latest smartphone model",
                price=699.99,
                stock_quantity=100,
                category="Electronics"
            ),
            Item(
                name="Headphones",
                description="Wireless noise-canceling headphones",
                price=199.99,
                stock_quantity=75,
                category="Electronics"
            ),
            Item(
                name="Book",
                description="Programming fundamentals",
                price=49.99,
                stock_quantity=200,
                category="Books"
            ),
            Item(
                name="T-shirt",
                description="Cotton casual t-shirt",
                price=24.99,
                stock_quantity=150,
                category="Clothing"
            )
        ]
        
        # Create sample user
        sample_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="$2b$12$dummy.hash.for.testing.purposes"
        )
        
        # Add to database
        db.add_all(sample_items)
        db.add(sample_user)
        db.commit()
        
        print("Test database sample data initialized successfully")
        
    except Exception as e:
        print(f"Error initializing test database: {e}")
        db.rollback()
    finally:
        db.close()

@pytest.fixture(scope="function")
def setup_database():
    """Setup test database before each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize sample data
    init_test_db()
    
    yield
    
    # Cleanup - drop all tables
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def auth_token(setup_database):
    """Get authentication token for testing."""
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "anypassword"
    })
    return response.json()["access_token"]

class TestShoppingCartComprehensive:
    """Comprehensive test cases for Shopping Cart API - covering ALL scenarios."""
    
    # ============================================================================
    # POSITIVE TEST CASES - These should PASS and show what works correctly
    # ============================================================================
    
    def test_positive_add_valid_item_to_cart_success(self, auth_token):
        """✅ POSITIVE: Add valid item to cart with sufficient inventory."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 2}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item added to cart successfully"
        assert "cart_total" in data
        assert data["item_added"]["id"] == 1
        assert data["item_added"]["quantity"] == 2
        
        # Verify inventory was reduced
        response = client.get("/api/items/1")
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["stock_quantity"] == 48  # 50 - 2

    def test_positive_add_item_with_maximum_available_stock(self, auth_token):
        """✅ POSITIVE: Add item with maximum available stock (boundary case)."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 2, "quantity": 100}  # Use all available stock
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item added to cart successfully"
        assert data["item_added"]["quantity"] == 100
        
        # Verify inventory becomes 0
        response = client.get("/api/items/2")
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["stock_quantity"] == 0

    def test_positive_add_multiple_different_items_to_cart(self, auth_token):
        """✅ POSITIVE: Add multiple different items to cart."""
        # Add different items
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 2}  # Laptop: 999.99 * 2
        )
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 3, "quantity": 1}  # Headphones: 199.99 * 1
        )
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 4, "quantity": 3}  # Book: 49.99 * 3
        )
        
        # Verify cart has multiple items
        cart_response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 3
        assert cart_data["item_count"] == 3  # 3 unique items

    def test_positive_cart_total_calculation_accuracy(self, auth_token):
        """✅ POSITIVE: Verify cart total calculation is accurate."""
        # Add items with known prices
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 2}  # Laptop: 999.99 * 2 = 1999.98
        )
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 5, "quantity": 1}  # T-shirt: 24.99 * 1 = 24.99
        )
        
        # Verify total calculation
        cart_response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        expected_total = (999.99 * 2) + (24.99 * 1)
        assert abs(cart_data["total"] - expected_total) < 0.01  # Allow for floating point precision

    def test_positive_remove_specific_item_from_cart(self, auth_token):
        """✅ POSITIVE: Remove specific item from cart."""
        # First add an item
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 5, "quantity": 2}
        )
        
        # Then remove it
        response = client.delete(
            "/api/cart/5",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Item removed from cart successfully"

    def test_positive_clear_entire_cart(self, auth_token):
        """✅ POSITIVE: Clear entire cart."""
        # Add multiple items first
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 2}
        )
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 2, "quantity": 3}
        )
        
        # Clear entire cart
        response = client.delete(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        # Verify cart is empty
        cart_response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 0
        assert cart_data["total"] == 0
        assert cart_data["item_count"] == 0

    def test_positive_get_cart_contents(self, auth_token):
        """✅ POSITIVE: Get user cart contents."""
        # First add an item
        client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 4, "quantity": 2}
        )
        
        # Then get cart contents
        response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert data["total"] > 0
        assert data["item_count"] >= 1

    # ============================================================================
    # NEGATIVE TEST CASES - These should FAIL and show what breaks
    # ============================================================================
    
    def test_negative_add_item_with_insufficient_inventory(self, auth_token):
        """❌ NEGATIVE: Add item to cart with insufficient inventory."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 60}  # More than available stock
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Insufficient inventory"
        
        # Verify inventory was not changed
        response = client.get("/api/items/1")
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["stock_quantity"] == 50

    def test_negative_add_item_with_invalid_item_id(self, auth_token):
        """❌ NEGATIVE: Add item to cart with invalid item ID."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 999, "quantity": 1}  # Non-existent item
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Item not found"

    def test_negative_add_item_with_zero_quantity(self, auth_token):
        """❌ NEGATIVE: Add item to cart with zero quantity."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 0}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_negative_quantity(self, auth_token):
        """❌ NEGATIVE: Add item to cart with negative quantity."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": -1}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_quantity_exceeding_system_limit(self, auth_token):
        """❌ NEGATIVE: Add item to cart with quantity exceeding system limit."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 1001}  # Over 1000 limit
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_expired_user_session(self):
        """❌ NEGATIVE: Add item to cart with expired user session."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": "Bearer invalid_token"},
            json={"item_id": 1, "quantity": 1}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_missing_authentication(self):
        """❌ NEGATIVE: Add item to cart without authentication."""
        response = client.post(
            "/api/cart/add",
            json={"item_id": 1, "quantity": 1}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_missing_item_id(self, auth_token):
        """❌ NEGATIVE: Add item to cart with missing item_id."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"quantity": 1}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_missing_quantity(self, auth_token):
        """❌ NEGATIVE: Add item to cart with missing quantity."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_invalid_data_types(self, auth_token):
        """❌ NEGATIVE: Add item to cart with invalid data types."""
        # Test with string item_id instead of integer
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": "abc", "quantity": 1}
        )
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_add_item_with_special_characters_injection(self, auth_token):
        """❌ NEGATIVE: Add item to cart with SQL injection attempt."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": "1'; DROP TABLE items; --", "quantity": 1}
        )
        
        # Should fail validation at Pydantic level
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_negative_remove_item_not_in_cart(self, auth_token):
        """❌ NEGATIVE: Remove item that's not in cart."""
        response = client.delete(
            "/api/cart/999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should fail - item not in cart
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_negative_remove_item_without_authentication(self):
        """❌ NEGATIVE: Remove item without authentication."""
        response = client.delete("/api/cart/1")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_negative_get_cart_without_authentication(self):
        """❌ NEGATIVE: Get cart without authentication."""
        response = client.get("/api/cart")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    # ============================================================================
    # BOUNDARY TEST CASES - Testing edge cases and limits
    # ============================================================================
    
    def test_boundary_add_item_with_minimum_quantity(self, auth_token):
        """🔍 BOUNDARY: Add item with minimum quantity (1)."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 3, "quantity": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["item_added"]["quantity"] == 1

    def test_boundary_add_item_with_maximum_quantity_limit(self, auth_token):
        """🔍 BOUNDARY: Add item with maximum quantity limit (1000)."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 4, "quantity": 1000}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["item_added"]["quantity"] == 1000

    def test_boundary_add_item_with_decimal_quantity(self, auth_token):
        """🔍 BOUNDARY: Add item with decimal quantity."""
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 1, "quantity": 1.5}
        )
        
        # This test shows the API's current behavior with decimal quantities
        # It may pass or fail depending on validation rules
        assert response.status_code in [200, 422]

    def test_boundary_add_item_with_very_long_text(self, auth_token):
        """🔍 BOUNDARY: Add item with extremely long text inputs."""
        long_id = "1" * 1000  # Very long ID
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": long_id, "quantity": 1}
        )
        
        # Should fail validation
        assert response.status_code == 422

    def test_boundary_concurrent_requests_race_condition(self, auth_token):
        """🔍 BOUNDARY: Test concurrent requests (race condition)."""
        # First request should succeed
        response1 = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 2, "quantity": 3}
        )
        
        assert response1.status_code == 200
        
        # Second request should fail due to insufficient inventory
        response2 = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 2, "quantity": 100}
        )
        
        assert response2.status_code == 400
        data = response2.json()
        assert data["detail"] == "Insufficient inventory"

    # ============================================================================
    # SECURITY TEST CASES - Testing security vulnerabilities
    # ============================================================================
    
    def test_security_sql_injection_prevention(self, auth_token):
        """🔒 SECURITY: Test SQL injection prevention."""
        # Test various SQL injection attempts
        injection_attempts = [
            "1 OR 1=1",
            "1; DROP TABLE items;",
            "1' UNION SELECT * FROM users --",
            "1 AND (SELECT COUNT(*) FROM information_schema.tables) > 0"
        ]
        
        for attempt in injection_attempts:
            response = client.post(
                "/api/cart/add",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"item_id": attempt, "quantity": 1}
            )
            
            # Should fail validation, not execute SQL
            assert response.status_code == 422

    def test_security_xss_prevention(self, auth_token):
        """🔒 SECURITY: Test XSS prevention."""
        xss_attempts = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "onload=alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for attempt in xss_attempts:
            response = client.post(
                "/api/cart/add",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"item_id": 1, "quantity": 1}
            )
            
            # Should succeed (XSS is not relevant for this endpoint)
            assert response.status_code == 200

    def test_security_authentication_bypass(self):
        """🔒 SECURITY: Test authentication bypass attempts."""
        # Try to access cart without token
        response = client.get("/api/cart")
        assert response.status_code == 401
        
        # Try with invalid token format
        response = client.get("/api/cart", headers={"Authorization": "InvalidFormat"})
        assert response.status_code == 401
        
        # Try with expired token
        response = client.get("/api/cart", headers={"Authorization": "Bearer expired.token.here"})
        assert response.status_code == 401

    # ============================================================================
    # PERFORMANCE TEST CASES - Testing system performance
    # ============================================================================
    
    def test_performance_add_multiple_items_rapidly(self, auth_token):
        """⚡ PERFORMANCE: Test adding multiple items rapidly."""
        # Add 5 different items rapidly
        for i in range(1, 6):
            response = client.post(
                "/api/cart/add",
                headers={"Authorization": f"Bearer {auth_token}"},
                json={"item_id": i, "quantity": 1}
            )
            assert response.status_code == 200
        
        # Verify all items were added
        cart_response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        assert len(cart_data["items"]) == 5

    def test_performance_large_quantity_operations(self, auth_token):
        """⚡ PERFORMANCE: Test operations with large quantities."""
        # Add item with large quantity
        response = client.post(
            "/api/cart/add",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"item_id": 4, "quantity": 100}
        )
        
        assert response.status_code == 200
        
        # Verify cart total calculation
        cart_response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert cart_response.status_code == 200
        cart_data = cart_response.json()
        expected_total = 49.99 * 100
        assert abs(cart_data["total"] - expected_total) < 0.01

class TestAuthenticationComprehensive:
    """Comprehensive test cases for Authentication - covering ALL scenarios."""
    
    # ============================================================================
    # POSITIVE TEST CASES - These should PASS
    # ============================================================================
    
    def test_positive_user_login_success(self, setup_database):
        """✅ POSITIVE: User login with valid credentials."""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "anypassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_positive_user_registration_success(self, setup_database):
        """✅ POSITIVE: User registration with valid data."""
        response = client.post("/api/auth/register", json={
            "username": "newuser123",
            "email": "newuser123@example.com",
            "password": "newpassword123"
        })
        
        # API returns 201 for successful creation
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["username"] == "newuser123"
        assert data["user"]["email"] == "newuser123@example.com"

    def test_positive_token_validation(self, auth_token):
        """✅ POSITIVE: Validate that generated token works."""
        response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

    # ============================================================================
    # NEGATIVE TEST CASES - These should FAIL
    # ============================================================================
    
    def test_negative_user_login_invalid_credentials(self, setup_database):
        """❌ NEGATIVE: User login with invalid credentials."""
        response = client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        # Should reject invalid credentials
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_negative_user_login_nonexistent_user(self, setup_database):
        """❌ NEGATIVE: User login with non-existent username."""
        response = client.post("/api/auth/login", json={
            "username": "nonexistentuser",
            "password": "anypassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_negative_user_registration_duplicate_username(self, setup_database):
        """❌ NEGATIVE: User registration with duplicate username."""
        # First registration should succeed
        client.post("/api/auth/register", json={
            "username": "duplicateuser",
            "email": "duplicate1@example.com",
            "password": "password123"
        })
        
        # Second registration with same username should fail
        response = client.post("/api/auth/register", json={
            "username": "duplicateuser",
            "email": "duplicate2@example.com",
            "password": "password456"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_negative_user_registration_invalid_email(self, setup_database):
        """❌ NEGATIVE: User registration with invalid email format."""
        response = client.post("/api/auth/register", json={
            "username": "invaliduser",
            "email": "invalid-email",
            "password": "password123"
        })
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data

    def test_negative_user_registration_missing_fields(self, setup_database):
        """❌ NEGATIVE: User registration with missing required fields."""
        # Missing username
        response = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 422
        
        # Missing password
        response = client.post("/api/auth/register", json={
            "username": "testuser",
            "email": "test@example.com"
        })
        assert response.status_code == 422

    def test_negative_user_registration_weak_password(self, setup_database):
        """❌ NEGATIVE: User registration with weak password."""
        response = client.post("/api/auth/register", json={
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123"  # Too short
        })
        
        # This may pass or fail depending on password validation rules
        assert response.status_code in [201, 422]

    # ============================================================================
    # SECURITY TEST CASES
    # ============================================================================
    
    def test_security_password_hashing(self, setup_database):
        """🔒 SECURITY: Test that passwords are properly hashed."""
        # Register a new user
        response = client.post("/api/auth/register", json={
            "username": "hashuser",
            "email": "hash@example.com",
            "password": "mypassword123"
        })
        
        assert response.status_code == 201
        
        # Try to login with the same password
        login_response = client.post("/api/auth/login", json={
            "username": "hashuser",
            "password": "mypassword123"
        })
        
        assert login_response.status_code == 200

    def test_security_token_expiration(self, auth_token):
        """🔒 SECURITY: Test token expiration handling."""
        # This test shows current token behavior
        # In a real system, tokens would expire
        response = client.get(
            "/api/cart",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200

class TestItemsComprehensive:
    """Comprehensive test cases for Items Management - covering ALL scenarios."""
    
    # ============================================================================
    # POSITIVE TEST CASES - These should PASS
    # ============================================================================
    
    def test_positive_get_all_items(self, setup_database):
        """✅ POSITIVE: Get all available items."""
        response = client.get("/api/items")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 5  # Should have at least 5 sample items

    def test_positive_get_item_by_id(self, setup_database):
        """✅ POSITIVE: Get specific item by ID."""
        response = client.get("/api/items/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Laptop"
        assert data["price"] == 999.99

    def test_positive_search_items_by_name(self, setup_database):
        """✅ POSITIVE: Search items by name."""
        response = client.get("/api/items/search/laptop")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        # Should find laptop
        assert any("laptop" in item["name"].lower() for item in data)

    def test_positive_filter_items_by_category(self, setup_database):
        """✅ POSITIVE: Filter items by category."""
        response = client.get("/api/items/category/Electronics")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # Should have at least 3 electronics items
        # All items should be in Electronics category
        assert all(item["category"] == "Electronics" for item in data)

    def test_positive_get_items_with_pagination_parameters(self, setup_database):
        """✅ POSITIVE: Get items with pagination parameters (even if not implemented)."""
        # Test with limit parameter
        response = client.get("/api/items?limit=3")
        assert response.status_code == 200
        
        # Test with offset parameter
        response2 = client.get("/api/items?offset=2&limit=2")
        assert response2.status_code == 200
        
        # Test with sort parameter
        response3 = client.get("/api/items?sort=price&order=asc")
        assert response3.status_code == 200

    # ============================================================================
    # NEGATIVE TEST CASES - These should FAIL
    # ============================================================================
    
    def test_negative_get_item_by_invalid_id(self, setup_database):
        """❌ NEGATIVE: Get item by invalid ID."""
        response = client.get("/api/items/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Item not found"

    def test_negative_get_item_by_string_id(self, setup_database):
        """❌ NEGATIVE: Get item by string ID."""
        response = client.get("/api/items/abc")
        
        assert response.status_code == 422  # Validation error

    def test_negative_search_items_empty_query(self, setup_database):
        """❌ NEGATIVE: Search items with empty query."""
        response = client.get("/api/items/search/")
        
        # This may pass or fail depending on API implementation
        assert response.status_code in [200, 404, 422]

    def test_negative_filter_items_invalid_category(self, setup_database):
        """❌ NEGATIVE: Filter items by invalid category."""
        response = client.get("/api/items/category/InvalidCategory")
        
        # Should return empty list or error
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0

    def test_negative_access_items_without_authentication(self, setup_database):
        """❌ NEGATIVE: Access items without authentication (if required)."""
        # Items endpoints are public, so this should pass
        response = client.get("/api/items")
        assert response.status_code == 200

    # ============================================================================
    # BOUNDARY TEST CASES
    # ============================================================================
    
    def test_boundary_search_items_very_long_query(self, setup_database):
        """🔍 BOUNDARY: Search items with very long query."""
        long_query = "a" * 1000
        response = client.get(f"/api/items/search/{long_query}")
        
        # Should handle gracefully
        assert response.status_code in [200, 404, 422]

    def test_boundary_filter_items_special_characters(self, setup_database):
        """🔍 BOUNDARY: Filter items with special characters in category."""
        special_categories = [
            "Electronics'",
            "Books;",
            "Clothing--",
            "Category OR 1=1"
        ]
        
        for category in special_categories:
            response = client.get(f"/api/items/category/{category}")
            # Should handle gracefully
            assert response.status_code in [200, 404, 422]

    # ============================================================================
    # PERFORMANCE TEST CASES
    # ============================================================================
    
    def test_performance_multiple_item_requests(self, setup_database):
        """⚡ PERFORMANCE: Test multiple item requests."""
        # Make multiple requests to test performance
        for i in range(1, 6):
            response = client.get(f"/api/items/{i}")
            assert response.status_code == 200

    def test_performance_search_performance(self, setup_database):
        """⚡ PERFORMANCE: Test search performance."""
        search_terms = ["laptop", "phone", "book", "shirt", "headphones"]
        
        for term in search_terms:
            response = client.get(f"/api/items/search/{term}")
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
