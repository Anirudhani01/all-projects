# test/test_all_endpoints.py

import pytest
import json
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

# Import your app and models
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app
from backend.database import get_session
from backend.models import MenuItem, Order, OrderItem, OrderStatus, PaymentMethod

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="function")
def client():
    """Create a test client with fresh database for each test"""
    SQLModel.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a database session for direct database operations"""
    with Session(engine) as session:
        yield session

class TestRootEndpoint:
    """Test cases for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test GET / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Restaurant Management System API"
        assert data["version"] == "1.0.0"

class TestMenuEndpoints:
    """Test cases for menu management endpoints"""
    
    def test_get_menu_items(self, client):
        """Test GET /menu - get all menu items"""
        response = client.get("/menu")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have seeded items
        
        # Check structure of first item
        first_item = data[0]
        assert "id" in first_item
        assert "name" in first_item
        assert "main_category" in first_item
        assert "sub_category" in first_item
        assert "price" in first_item
        assert "description" in first_item
        assert "is_out_of_stock" in first_item
        assert "is_active" in first_item
    
    def test_search_menu_items(self, client):
        """Test GET /menu?search= - search menu items"""
        response = client.get("/menu?search=Chicken")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All returned items should contain "Chicken"
        for item in data:
            assert "Chicken" in item["name"]
    
    def test_search_menu_items_empty(self, client):
        """Test GET /menu?search= - search with no results"""
        response = client.get("/menu?search=NonExistentItem")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_menu_item(self, client):
        """Test POST /menu - create new menu item"""
        new_item = {
            "name": "Test Item",
            "main_category": "veg",
            "sub_category": "test",
            "price": 50.0,
            "description": "Test description"
        }
        response = client.post("/menu", json=new_item)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["main_category"] == "veg"
        assert data["sub_category"] == "test"
        assert data["price"] == 50.0
        assert data["description"] == "Test description"
        assert data["is_out_of_stock"] == False
        assert data["is_active"] == True
    
    def test_get_menu_item_by_id(self, client):
        """Test GET /menu/{menu_item_id} - get specific menu item"""
        # First get all items to get an ID
        response = client.get("/menu")
        items = response.json()
        item_id = items[0]["id"]
        
        response = client.get(f"/menu/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
    
    def test_get_menu_item_not_found(self, client):
        """Test GET /menu/{menu_item_id} - item not found"""
        response = client.get("/menu/99999")
        assert response.status_code == 404
        assert "Menu item not found" in response.json()["detail"]
    
    def test_update_menu_item(self, client):
        """Test PUT /menu/{menu_item_id} - update menu item"""
        # First get all items to get an ID
        response = client.get("/menu")
        items = response.json()
        item_id = items[0]["id"]
        
        update_data = {
            "price": 75.0,
            "description": "Updated description"
        }
        response = client.put(f"/menu/{item_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 75.0
        assert data["description"] == "Updated description"
    
    def test_update_menu_item_not_found(self, client):
        """Test PUT /menu/{menu_item_id} - item not found"""
        update_data = {"price": 75.0}
        response = client.put("/menu/99999", json=update_data)
        assert response.status_code == 404
        assert "Menu item not found" in response.json()["detail"]
    
    def test_delete_menu_item(self, client):
        """Test DELETE /menu/{menu_item_id} - delete menu item"""
        # First get all items to get an ID
        response = client.get("/menu")
        items = response.json()
        item_id = items[0]["id"]
        
        response = client.delete(f"/menu/{item_id}")
        assert response.status_code == 200
        assert response.json()["message"] == "Menu item deleted successfully"
        
        # Verify item is soft deleted (is_active = False)
        response = client.get(f"/menu/{item_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] == False
    
    def test_delete_menu_item_not_found(self, client):
        """Test DELETE /menu/{menu_item_id} - item not found"""
        response = client.delete("/menu/99999")
        assert response.status_code == 404
        assert "Menu item not found" in response.json()["detail"]
    
    def test_set_out_of_stock(self, client):
        """Test PUT /menu/out-of-stock - set items out of stock"""
        # First get all items to get IDs
        response = client.get("/menu")
        items = response.json()
        item_ids = [items[0]["id"], items[1]["id"]]
        
        payload = {"ids": item_ids}
        response = client.put("/menu/out-of-stock", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        # Check that specified items are out of stock
        for item in data:
            if item["id"] in item_ids:
                assert item["is_out_of_stock"] == True
            else:
                assert item["is_out_of_stock"] == False
    
    def test_get_menu_categories(self, client):
        """Test GET /menu/categories - get all categories"""
        response = client.get("/menu/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        
        # Should have main categories
        assert "veg" in data
        assert "non-veg" in data
        assert "beverages" in data
        
        # Should have sub categories
        assert isinstance(data["veg"], list)
        assert isinstance(data["non-veg"], list)
    
    def test_get_menu_by_category(self, client):
        """Test GET /menu/category/{main_category} - get items by main category"""
        response = client.get("/menu/category/veg")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All items should be veg
        for item in data:
            assert item["main_category"] == "veg"
    
    def test_get_menu_by_subcategory(self, client):
        """Test GET /menu/category/{main_category}/{sub_category} - get items by sub category"""
        response = client.get("/menu/category/veg/rice")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All items should be veg rice
        for item in data:
            assert item["main_category"] == "veg"
            assert item["sub_category"] == "rice"

class TestTableEndpoints:
    """Test cases for table management endpoints"""
    
    def test_get_tables(self, client):
        """Test GET /tables - get all tables status"""
        response = client.get("/tables")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 12  # Should have 12 tables
        
        # Check structure of first table
        first_table = data[0]
        assert "table_number" in first_table
        assert "status" in first_table
        assert "items" in first_table
        assert "total_amount" in first_table
        
        # All tables should be idle initially
        for table in data:
            assert table["status"] == "idle"
            assert table["total_amount"] == 0.0
            assert len(table["items"]) == 0
    
    def test_open_order_for_table(self, client):
        """Test POST /tables/{table_number}/order - open order for table"""
        response = client.post("/tables/3/order")
        assert response.status_code == 200
        data = response.json()
        assert data["table_number"] == 3
        assert data["status"] == "open"
        assert data["total_amount"] == 0.0
        assert len(data["items"]) == 0
    
    def test_open_order_for_invalid_table(self, client):
        """Test POST /tables/{table_number}/order - invalid table number"""
        response = client.post("/tables/15/order")
        assert response.status_code == 400
        assert "table_number must be 1..12" in response.json()["detail"]
    
    def test_open_order_for_table_zero(self, client):
        """Test POST /tables/{table_number}/order - table number 0"""
        response = client.post("/tables/0/order")
        assert response.status_code == 400
        assert "table_number must be 1..12" in response.json()["detail"]
    
    def test_get_existing_order_for_table(self, client):
        """Test POST /tables/{table_number}/order - get existing order"""
        # First create an order
        response1 = client.post("/tables/5/order")
        assert response1.status_code == 200
        order_id = response1.json()["id"]
        
        # Try to create another order for same table
        response2 = client.post("/tables/5/order")
        assert response2.status_code == 200
        assert response2.json()["id"] == order_id  # Should return same order

class TestOrderEndpoints:
    """Test cases for order management endpoints"""
    
    def test_get_order(self, client):
        """Test GET /orders/{order_id} - get order details"""
        # First create an order
        response = client.post("/tables/7/order")
        order_id = response.json()["id"]
        
        response = client.get(f"/orders/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["table_number"] == 7
        assert data["status"] == "open"
    
    def test_get_order_not_found(self, client):
        """Test GET /orders/{order_id} - order not found"""
        response = client.get("/orders/99999")
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
    
    def test_add_item_to_order(self, client):
        """Test POST /orders/{order_id}/items - add item to order"""
        # First create an order
        response = client.post("/tables/8/order")
        order_id = response.json()["id"]
        
        # Get menu items to get an ID
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item to order
        payload = {"menu_item_id": menu_item_id, "quantity": 2}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        assert data["total_amount"] > 0
    
    def test_add_item_to_nonexistent_order(self, client):
        """Test POST /orders/{order_id}/items - order not found"""
        payload = {"menu_item_id": 1, "quantity": 1}
        response = client.post("/orders/99999/items", json=payload)
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
    
    def test_add_out_of_stock_item(self, client):
        """Test POST /orders/{order_id}/items - add out of stock item"""
        # First create an order
        response = client.post("/tables/9/order")
        order_id = response.json()["id"]
        
        # Get menu items and set one as out of stock
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Set item as out of stock
        client.put("/menu/out-of-stock", json={"ids": [menu_item_id]})
        
        # Try to add out of stock item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        assert response.status_code == 400
        assert "is out of stock" in response.json()["detail"]
    
    def test_add_same_item_twice(self, client):
        """Test POST /orders/{order_id}/items - add same item twice (should increase quantity)"""
        # First create an order
        response = client.post("/tables/10/order")
        order_id = response.json()["id"]
        
        # Get menu items to get an ID
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item first time
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response1 = client.post(f"/orders/{order_id}/items", json=payload)
        assert response1.status_code == 200
        
        # Add same item second time
        response2 = client.post(f"/orders/{order_id}/items", json=payload)
        assert response2.status_code == 200
        data = response2.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2  # Should be 1 + 1 = 2
    
    def test_update_item_quantity(self, client):
        """Test PATCH /orders/{order_id}/items/{order_item_id} - update item quantity"""
        # First create an order and add an item
        response = client.post("/tables/11/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        order_item_id = response.json()["items"][0]["id"]
        
        # Update quantity
        update_payload = {"quantity": 3}
        response = client.patch(f"/orders/{order_id}/items/{order_item_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["items"][0]["quantity"] == 3
    
    def test_update_item_quantity_to_zero(self, client):
        """Test PATCH /orders/{order_id}/items/{order_item_id} - set quantity to 0 (should remove item)"""
        # First create an order and add an item
        response = client.post("/tables/12/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        order_item_id = response.json()["items"][0]["id"]
        
        # Set quantity to 0
        update_payload = {"quantity": 0}
        response = client.patch(f"/orders/{order_id}/items/{order_item_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0  # Item should be removed
    
    def test_delete_item(self, client):
        """Test DELETE /orders/{order_id}/items/{order_item_id} - delete item from order"""
        # First create an order and add an item
        response = client.post("/tables/1/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        order_item_id = response.json()["items"][0]["id"]
        
        # Delete item
        response = client.delete(f"/orders/{order_id}/items/{order_item_id}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0
    
    def test_pay_order_cash(self, client):
        """Test POST /orders/{order_id}/pay - pay order with cash"""
        # First create an order and add an item
        response = client.post("/tables/2/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        
        # Pay order
        pay_payload = {"payment_method": "cash"}
        response = client.post(f"/orders/{order_id}/pay", json=pay_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert data["payment_method"] == "cash"
        assert data["paid_at"] is not None
    
    def test_pay_order_online(self, client):
        """Test POST /orders/{order_id}/pay - pay order with online"""
        # First create an order and add an item
        response = client.post("/tables/4/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        
        # Pay order
        pay_payload = {"payment_method": "online"}
        response = client.post(f"/orders/{order_id}/pay", json=pay_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "paid"
        assert data["payment_method"] == "online"
        assert data["paid_at"] is not None
    
    def test_pay_empty_order(self, client):
        """Test POST /orders/{order_id}/pay - pay empty order (should fail)"""
        # First create an order (no items)
        response = client.post("/tables/6/order")
        order_id = response.json()["id"]
        
        # Try to pay empty order
        pay_payload = {"payment_method": "cash"}
        response = client.post(f"/orders/{order_id}/pay", json=pay_payload)
        assert response.status_code == 400
        assert "Cannot pay an empty order" in response.json()["detail"]
    
    def test_pay_already_paid_order(self, client):
        """Test POST /orders/{order_id}/pay - pay already paid order (should fail)"""
        # First create an order and add an item
        response = client.post("/tables/8/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        
        # Pay order first time
        pay_payload = {"payment_method": "cash"}
        response = client.post(f"/orders/{order_id}/pay", json=pay_payload)
        assert response.status_code == 200
        
        # Try to pay again
        response = client.post(f"/orders/{order_id}/pay", json=pay_payload)
        assert response.status_code == 400
        assert "Order already paid" in response.json()["detail"]
    
    def test_modify_paid_order(self, client):
        """Test modifying a paid order (should fail)"""
        # First create an order and add an item
        response = client.post("/tables/9/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        order_item_id = response.json()["items"][0]["id"]
        
        # Pay order
        pay_payload = {"payment_method": "cash"}
        response = client.post(f"/orders/{order_id}/pay", json=pay_payload)
        assert response.status_code == 200
        
        # Try to add item to paid order
        payload = {"menu_item_id": menu_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        assert response.status_code == 400
        assert "Cannot modify a paid order" in response.json()["detail"]
        
        # Try to update item in paid order
        update_payload = {"quantity": 2}
        response = client.patch(f"/orders/{order_id}/items/{order_item_id}", json=update_payload)
        assert response.status_code == 400
        assert "Cannot modify a paid order" in response.json()["detail"]

class TestAdminEndpoints:
    """Test cases for admin endpoints"""
    
    def test_get_admin_orders(self, client):
        """Test GET /admin/orders - get all orders"""
        response = client.get("/admin/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_admin_orders_filter_by_status(self, client):
        """Test GET /admin/orders?status= - filter by status"""
        response = client.get("/admin/orders?status=open")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All orders should be open
        for order in data:
            assert order["status"] == "open"
    
    def test_get_admin_orders_filter_by_table(self, client):
        """Test GET /admin/orders?table= - filter by table"""
        # First create an order for table 3
        client.post("/tables/3/order")
        
        response = client.get("/admin/orders?table=3")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All orders should be for table 3
        for order in data:
            assert order["table_number"] == 3
    
    def test_get_admin_orders_filter_by_payment(self, client):
        """Test GET /admin/orders?payment= - filter by payment method"""
        # First create and pay an order
        response = client.post("/tables/5/order")
        order_id = response.json()["id"]
        
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        menu_item_id = menu_items[0]["id"]
        
        # Add item and pay
        client.post(f"/orders/{order_id}/items", json={"menu_item_id": menu_item_id, "quantity": 1})
        client.post(f"/orders/{order_id}/pay", json={"payment_method": "cash"})
        
        # Filter by cash payment
        response = client.get("/admin/orders?payment=cash")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # All orders should be paid with cash
        for order in data:
            assert order["payment_method"] == "cash"
    
    def test_get_admin_metrics(self, client):
        """Test GET /admin/metrics - get admin metrics"""
        response = client.get("/admin/metrics")
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "total_revenue" in data
        assert "cash" in data
        assert "online" in data
        assert "orders_paid" in data
        assert "items_sold" in data
        
        # All should be numbers
        assert isinstance(data["total_revenue"], (int, float))
        assert isinstance(data["cash"], (int, float))
        assert isinstance(data["online"], (int, float))
        assert isinstance(data["orders_paid"], int)
        assert isinstance(data["items_sold"], int)

class TestIntegrationWorkflow:
    """Integration test cases for complete workflows"""
    
    def test_complete_customer_workflow(self, client):
        """Test complete customer workflow: sit, order, pay"""
        # 1. Check tables (should all be idle)
        response = client.get("/tables")
        tables = response.json()
        assert tables[2]["status"] == "idle"  # Table 3
        
        # 2. Customer sits at table 3
        response = client.post("/tables/3/order")
        order = response.json()
        assert order["table_number"] == 3
        assert order["status"] == "open"
        order_id = order["id"]
        
        # 3. Check tables again (table 3 should be open)
        response = client.get("/tables")
        tables = response.json()
        assert tables[2]["status"] == "open"  # Table 3 (index 2)
        
        # 4. Customer orders items
        menu_response = client.get("/menu")
        menu_items = menu_response.json()
        
        # Add first item
        item1_id = menu_items[0]["id"]
        response = client.post(f"/orders/{order_id}/items", json={"menu_item_id": item1_id, "quantity": 2})
        order = response.json()
        assert len(order["items"]) == 1
        assert order["items"][0]["quantity"] == 2
        
        # Add second item
        item2_id = menu_items[1]["id"]
        response = client.post(f"/orders/{order_id}/items", json={"menu_item_id": item2_id, "quantity": 1})
        order = response.json()
        assert len(order["items"]) == 2
        
        # 5. Check order total
        assert order["total_amount"] > 0
        
        # 6. Customer pays with cash
        response = client.post(f"/orders/{order_id}/pay", json={"payment_method": "cash"})
        order = response.json()
        assert order["status"] == "paid"
        assert order["payment_method"] == "cash"
        assert order["paid_at"] is not None
        
        # 7. Check tables again (table 3 should be idle)
        response = client.get("/tables")
        tables = response.json()
        assert tables[2]["status"] == "idle"  # Table 3
        
        # 8. Check admin metrics
        response = client.get("/admin/metrics")
        metrics = response.json()
        assert metrics["orders_paid"] >= 1
        assert metrics["cash"] > 0
    
    def test_menu_management_workflow(self, client):
        """Test complete menu management workflow"""
        # 1. Get initial menu
        response = client.get("/menu")
        initial_count = len(response.json())
        
        # 2. Create new menu item
        new_item = {
            "name": "Test Biryani",
            "main_category": "veg",
            "sub_category": "biryani",
            "price": 160.0,
            "description": "Test biryani description"
        }
        response = client.post("/menu", json=new_item)
        assert response.status_code == 200
        new_item_id = response.json()["id"]
        
        # 3. Verify item was created
        response = client.get(f"/menu/{new_item_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Test Biryani"
        
        # 4. Update item
        update_data = {"price": 170.0, "description": "Updated description"}
        response = client.put(f"/menu/{new_item_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["price"] == 170.0
        
        # 5. Set item as out of stock
        response = client.put("/menu/out-of-stock", json={"ids": [new_item_id]})
        assert response.status_code == 200
        
        # 6. Verify item is out of stock
        response = client.get(f"/menu/{new_item_id}")
        assert response.json()["is_out_of_stock"] == True
        
        # 7. Try to add out of stock item to order (should fail)
        order_response = client.post("/tables/4/order")
        order_id = order_response.json()["id"]
        
        payload = {"menu_item_id": new_item_id, "quantity": 1}
        response = client.post(f"/orders/{order_id}/items", json=payload)
        assert response.status_code == 400
        assert "is out of stock" in response.json()["detail"]
        
        # 8. Remove item from out of stock
        response = client.put("/menu/out-of-stock", json={"ids": []})
        assert response.status_code == 200
        
        # 9. Verify item is back in stock
        response = client.get(f"/menu/{new_item_id}")
        assert response.json()["is_out_of_stock"] == False
        
        # 10. Now should be able to add item to order
        response = client.post(f"/orders/{order_id}/items", json=payload)
        assert response.status_code == 200
        
        # 11. Delete item (soft delete)
        response = client.delete(f"/menu/{new_item_id}")
        assert response.status_code == 200
        
        # 12. Verify item is soft deleted
        response = client.get(f"/menu/{new_item_id}")
        assert response.json()["is_active"] == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])