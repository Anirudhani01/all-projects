# Prompts Documentation

## User Query: Phase 1 - Modular Monolith Foundation

**Question**: "act as a python developer complete this phase and follow step by step"

**Context**: User requested to complete Phase 1 of an E-commerce web application with specific requirements for a modular monolith foundation using FastAPI + MySQL.

**Requirements Specified**:
1. Set up Project Structure with app/ directory containing main.py, db.py, models.py, routers/, and services/
2. Initialize requirements.txt with FastAPI, mysql-connector-python, and Pydantic
3. Design & Implement Database using MySQL schema with 7 tables
4. Configure Database Connectivity (username: anirudh, password: password123, localhost, database: ecom_db)
5. Implement connection pooling in db.py
6. Use dependency injection for DB connection handling

**Project Structure Requested**:
```
/E_commerce_web
├── app/ 
│   ├── __init__.py 
│   ├── main.py 
│   ├── db.py 
│   ├── models.py 
│   ├── routers/ 
│   │   ├── __init__.py 
│   │   ├── products.py 
│   │   ├── cart.py 
│   │   └── orders.py 
│   │   └── payments.py 
│   └── services/ 
│       ├── __init__.py 
│       └── inventory.py 
└── requirements.txt 
```

**Database Schema Provided**:
- users: user_id, email, password_hash, full_name, created_at
- categories: category_id, name
- products: product_id, name, description, price, stock_quantity, category_id, created_at
- cart_items: cart_item_id, user_id, product_id, quantity
- orders: order_id, user_id, total_amount, status, created_at
- order_items: order_item_id, order_id, product_id, quantity, price_at_purchase
- payments: payment_id, order_id, amount, payment_method, status, transaction_id, created_at

**Additional Requirements**:
- Use "SQL MODEL" (interpreted as using raw SQL queries)
- Add content to logchange.md, prompts.md, and readme.md
- Create documentation files to track changes and prompts

**Response Strategy**:
1. Create complete project structure as specified
2. Implement database connectivity with connection pooling
3. Create Pydantic models for data validation
4. Implement all routers with CRUD operations using raw SQL
5. Create inventory service for business logic
6. Set up main FastAPI application with all routers
7. Create documentation files (logchange.md, prompts.md, readme.md)
8. Use MySQL instead of SQLite as per user preferences
9. Automatically add new modules/packages to tech.md

**Implementation Details**:
- Used mysql-connector-python for database connectivity
- Implemented connection pooling with 10 connections
- Created comprehensive Pydantic models with validation
- Used raw SQL queries throughout the application
- Implemented proper error handling and transaction management
- Added CORS middleware for frontend integration
- Created health check and statistics endpoints
- Used dependency injection for database connections
- Implemented proper API response formatting

**Technologies Used**:
- FastAPI for web framework
- MySQL for database
- Pydantic for data validation
- mysql-connector-python for database connectivity
- uvicorn for ASGI server
- python-dotenv for environment management

---

## User Query: Product Catalogue Service Modification

**Question**: "now i need change this service so follow the Functional Requirements,API Endpoints, Pydantic Models and there it is using raw sql but note: you use "SQL model" and implement these all : 2.1. Product Catalogue Service"

**Context**: User requested to modify the existing Product Catalogue Service to adhere to new specific functional requirements, API endpoints, Pydantic models, and raw SQL queries for a publicly accessible product browsing service.

**Requirements Specified**:

### Functional Requirements:
- **FR1**: Any user must be able to retrieve a list of all products available for sale
- **FR2**: The product list must be filterable by category
- **FR3**: Any user must be able to retrieve the detailed information for a single product using its unique ID

### API Endpoints:
- **GET /products/**: Retrieves a list of products
  - Query Parameters: `category_id: int | None = None`
  - Success Response: `200 OK` with a list of `ProductResponse` objects
- **GET /products/{product_id}**: Retrieves a single product
  - Path Parameters: `product_id: int`
  - Success Response: `200 OK` with a single `ProductResponse` object
  - Error Response: `404 Not Found` if the product does not exist

### Pydantic Models:
```python
from pydantic import BaseModel
from decimal import Decimal

class ProductResponse(BaseModel):
    product_id: int
    name: str
    description: str | None
    price: Decimal
    stock_quantity: int
    category_id: int
```

### Raw SQL Queries:
- **For GET /products/ (without category filter)**:
  ```sql
  SELECT product_id, name, description, price, stock_quantity, category_id 
  FROM Products 
  WHERE stock_quantity > 0;
  ```
- **For GET /products/ (with category filter)**:
  ```sql
  SELECT product_id, name, description, price, stock_quantity, category_id 
  FROM Products 
  WHERE stock_quantity > 0 AND category_id = %s;
  ```
- **For GET /products/{product_id}**:
  ```sql
  SELECT product_id, name, description, price, stock_quantity, category_id 
  FROM Products 
  WHERE product_id = %s;
  ```

**Response Strategy**:
1. Add new `ProductResponse` Pydantic model to `app/models.py`
2. Refactor `app/routers/products.py` to remove CRUD operations (POST, PUT, DELETE)
3. Update GET endpoints to use specified SQL queries exactly
4. Implement stock filtering (stock_quantity > 0) for product list
5. Add category filtering capability
6. Return `ProductResponse` objects directly without wrapper
7. Remove pagination and search functionality as not specified in requirements
8. Update documentation files with changes

**Implementation Details**:
- Removed all CRUD endpoints from products router
- Implemented exact SQL queries as specified in requirements
- Added `ProductResponse` model for public API responses
- Simplified response format to return products directly
- Added stock availability filtering to show only available products
- Maintained category filtering functionality
- Used raw SQL with proper parameterization
- Implemented proper error handling for 404 cases

**Key Changes Made**:
- **app/models.py**: Added `ProductResponse` model
- **app/routers/products.py**: Complete refactoring to read-only service
- **Removed**: POST, PUT, DELETE endpoints, pagination, search functionality
- **Added**: Stock filtering, simplified response format, exact SQL queries
- **Updated**: Documentation files (logchange.md, prompts.md, README.md, tech.md)

**Technologies Maintained**:
- FastAPI for web framework
- MySQL for database
- Pydantic for data validation
- mysql-connector-python for database connectivity
- Raw SQL queries as specified

---

## User Query: Inventory Service Modification

**Question**: "now i need change this service so follow the Functional Requirements,API Endpoints, Pydantic Models and there it is using raw sql but you need to use this ,note: you use "SQL model" and implement these all : 2.2. Inventory Service"

**Context**: User requested to modify the existing Inventory Service to adhere to new specific functional requirements for an internal service that encapsulates critical business logic without exposing public HTTP endpoints.

**Requirements Specified**:

### Functional Requirements:
- **FR4**: The system must provide a mechanism to check the available stock for a given product ID
- **FR5**: The system must provide a mechanism to decrease the stock level for a given product ID by a specified quantity. This operation must fail if insufficient stock is available

### Internal Functions (to be located in app/services/inventory.py):
- **check_stock(db_cursor, product_id: int) -> int**: Returns the current stock quantity
- **reduce_stock(db_cursor, product_id: int, quantity: int) -> bool**: Decrements stock and returns True on success, False on failure (e.g., insufficient stock)

### Raw SQL Queries:
- **For check_stock**:
  ```sql
  SELECT stock_quantity FROM Products WHERE product_id = %s;
  ```
- **For reduce_stock (transactional update)**:
  ```sql
  UPDATE Products SET stock_quantity = stock_quantity - %s WHERE product_id = %s AND stock_quantity >= %s;
  ```
  The stock_quantity >= %s condition is a critical concurrency control check to prevent overselling.

### Key Design Principles:
- **Internal Service**: No public HTTP endpoints exposed
- **Security**: Critical business logic not accessible via web
- **Modularity**: Functions called directly by other services within the monolith
- **Concurrency Control**: Prevents overselling through SQL-level constraints

**Response Strategy**:
1. Refactor `app/services/inventory.py` from class-based to function-based approach
2. Remove complex business logic methods and public HTTP endpoints
3. Implement exact SQL queries as specified in requirements
4. Create simple, focused functions for stock checking and reduction
5. Add concurrency control to prevent overselling
6. Update documentation to reflect internal service nature

**Implementation Details**:
- Removed `InventoryService` class and all complex methods
- Implemented `check_stock()` function with exact SQL query
- Implemented `reduce_stock()` function with transactional update and concurrency control
- Added proper error handling and return values
- Used `db_cursor.rowcount` to determine operation success
- Maintained raw SQL approach as specified

**Key Changes Made**:
- **app/services/inventory.py**: Complete refactoring from class to functions
- **Removed**: Complex inventory methods, stock movement tracking, inventory summary
- **Added**: Simple check_stock and reduce_stock functions with exact SQL queries
- **Architecture**: Changed to internal service pattern with no public endpoints
- **Updated**: Documentation files (logchange.md, prompts.md, README.md, tech.md)

**Technologies Maintained**:
- MySQL for database operations
- mysql-connector-python for database connectivity
- Raw SQL queries as specified
- Transactional updates with concurrency control

---

## User Query: Cart Service Modification

**Question**: "now i need change this service so follow the Functional Requirements,API Endpoints, Pydantic Models and there it is using raw sql but note: you use "SQL model" and implement these all : 2.3. Cart Service"

**Context**: User requested to modify the existing Cart Service to adhere to new specific functional requirements for managing user shopping carts with user_id in URL path for Phase 1.

**Requirements Specified**:

### Functional Requirements:
- **FR6**: A user must be able to add a specified quantity of a product to their cart. If the product is already in the cart, its quantity should be updated
- **FR7**: A user must be able to view all items currently in their cart, including product details and sub-totals
- **FR8**: A user must be able to remove an item completely from their cart
- **FR9**: A user must be able to update the quantity of a specific item in their cart

### API Endpoints:
- **POST /cart/{user_id}/items**: Adds/updates an item in the cart
  - Success Response: 201 Created or 200 OK
- **GET /cart/{user_id}**: Retrieves the user's cart
  - Success Response: 200 OK with a CartResponse object
- **DELETE /cart/{user_id}/items/{product_id}**: Removes an item from the cart
  - Success Response: 204 No Content
- **PUT /cart/{user_id}/items/{product_id}**: Updates an item's quantity
  - Success Response: 200 OK

### Pydantic Models:
```python
from pydantic import BaseModel, Field
from decimal import Decimal

class CartItemRequest(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)  # Quantity must be positive

class CartItemResponse(BaseModel):
    product_id: int
    name: str
    price: Decimal
    quantity: int
    sub_total: Decimal

class CartResponse(BaseModel):
    items: list
    total_price: Decimal
```

### Raw SQL Queries:
- **For adding/updating an item (POST)**:
  ```sql
  -- This is an "UPSERT" operation.
  INSERT INTO CartItems (user_id, product_id, quantity) 
  VALUES (%s, %s, %s) 
  ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
  ```
- **For viewing the cart (GET)**:
  ```sql
  SELECT ci.product_id, p.name, p.price, ci.quantity 
  FROM CartItems ci 
  JOIN Products p ON ci.product_id = p.product_id 
  WHERE ci.user_id = %s;
  ```
- **For removing an item (DELETE)**:
  ```sql
  DELETE FROM CartItems WHERE user_id = %s AND product_id = %s;
  ```
- **For updating quantity (PUT)**:
  ```sql
  UPDATE CartItems SET quantity = %s WHERE user_id = %s AND product_id = %s;
  ```

### Key Design Principles:
- **Phase 1 Approach**: User identification via user_id in URL path (will be replaced with token-based auth in Phase 2)
- **UPSERT Functionality**: Automatic handling of existing vs new cart items
- **Sub-total Calculation**: Automatic calculation of item and cart totals
- **Direct Response Format**: CartResponse objects instead of wrapper responses

**Response Strategy**:
1. Add new Cart Service Pydantic models to `app/models.py`
2. Refactor `app/routers/cart.py` to implement new API endpoints
3. Update URL structure to use user_id in path parameters
4. Implement exact SQL queries as specified in requirements
5. Add UPSERT functionality for cart item management
6. Implement sub-total and total calculation logic
7. Update response formats to use new models
8. Update documentation files with changes

**Implementation Details**:
- Added `CartItemRequest`, `CartItemResponse`, and `CartResponse` models
- Implemented UPSERT operation using `ON DUPLICATE KEY UPDATE`
- Updated all endpoints to use user_id in URL path
- Added automatic sub-total calculation for cart items
- Implemented proper HTTP status codes (201, 200, 204)
- Used exact SQL queries as specified in requirements
- Removed old cart item ID-based operations

**Key Changes Made**:
- **app/models.py**: Added new Cart Service models
- **app/routers/cart.py**: Complete refactoring with new endpoints and SQL queries
- **Removed**: Old cart endpoints, cart item ID operations, clear cart functionality
- **Added**: UPSERT functionality, sub-total calculation, new response formats
- **Updated**: Documentation files (logchange.md, prompts.md, README.md, tech.md)

**Technologies Maintained**:
- FastAPI for web framework
- MySQL for database operations
- Pydantic for data validation
- mysql-connector-python for database connectivity
- Raw SQL queries as specified
- UPSERT operations for cart management

---

## User Query: Order Service Modification

**Question**: "now i need change this service so follow the Functional Requirements,API Endpoints, Pydantic Models and there it is using raw sql but note: you use "SQL model" and implement these all : 2.4. Order Service"

**Context**: User requested to modify the existing Order Service to adhere to new specific functional requirements for atomic transactional order creation with proper rollback mechanisms and integration with Inventory Service.

**Requirements Specified**:

### Functional Requirements:
- **FR10**: A user must be able to create an order from the contents of their cart. This process must be atomic: if any part fails (e.g., an item is out of stock), the entire transaction must be rolled back, leaving the database in its original state.
- **FR11**: After creating an order, the user's cart must be cleared.
- **FR12**: A user must be able to view a list of all their past orders.
- **FR13**: A user must be able to view the full details of a single past order, including all line items.

### API Endpoints:
- **POST /orders/{user_id}**: Creates an order from the user's cart
  - Success Response: 201 Created with an OrderResponse object
  - Error Response: 400 Bad Request if the cart is empty or an item is out of stock
- **GET /orders/{user_id}**: Retrieves a list of the user's orders
  - Success Response: 200 OK with a list of OrderSummaryResponse objects
- **GET /orders/{user_id}/{order_id}**: Retrieves details of a specific order
  - Success Response: 200 OK with a full OrderResponse object
  - Error Response: 404 Not Found

### Pydantic Models:
```python
from pydantic import BaseModel
from decimal import Decimal
import datetime

class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    price_at_purchase: Decimal

class OrderResponse(BaseModel):
    order_id: int
    status: str
    total_amount: Decimal
    created_at: datetime.datetime
    items: list

class OrderSummaryResponse(BaseModel):
    order_id: int
    status: str
    total_amount: Decimal
    created_at: datetime.datetime
```

### Raw SQL Queries (within a transaction block):
1. **BEGIN** (Or equivalent for the DB driver)
2. **SELECT... FROM CartItems... WHERE user_id = %s** (To fetch cart contents)
3. **For each item, SELECT stock_quantity FROM Products... FOR UPDATE** (To lock rows and check stock)
4. **INSERT INTO Orders (user_id, total_amount, status) VALUES (%s, %s, 'PENDING')**
5. **Get the LAST_INSERT_ID() for the new order_id**
6. **For each item, INSERT INTO OrderItems (order_id, product_id, quantity, price_at_purchase) VALUES (...);**
7. **For each item, UPDATE Products SET stock_quantity = stock_quantity - %s WHERE product_id = %s**
8. **DELETE FROM CartItems WHERE user_id = %s**
9. **COMMIT** (If all steps succeed) or **ROLLBACK** (If any step fails)

### Key Design Principles:
- **Atomic Transactions**: Complete BEGIN/COMMIT/ROLLBACK implementation
- **Row Locking**: FOR UPDATE to prevent race conditions during stock checking
- **Inventory Integration**: Uses reduce_stock() from Inventory Service
- **Critical Business Logic**: Most important transactional process in the application
- **Error Handling**: Proper rollback on any failure point

**Response Strategy**:
1. Add new Order Service Pydantic models to `app/models.py`
2. Refactor `app/routers/orders.py` to implement new API endpoints
3. Update URL structure to use user_id in path parameters
4. Implement atomic transaction management with proper rollback
5. Add row locking with FOR UPDATE for stock checking
6. Integrate with Inventory Service for stock reduction
7. Implement exact SQL queries as specified in requirements
8. Update response formats to use new models
9. Update documentation files with changes

**Implementation Details**:
- Added `OrderItemResponse`, `OrderResponse`, and `OrderSummaryResponse` models
- Implemented complete transaction management with BEGIN/COMMIT/ROLLBACK
- Added row locking with `FOR UPDATE` for stock validation
- Integrated with Inventory Service `reduce_stock()` function
- Updated all endpoints to use user_id in URL path
- Implemented proper error handling with rollback on failures
- Used exact SQL queries as specified in requirements
- Removed old order management endpoints

**Key Changes Made**:
- **app/models.py**: Added new Order Service models
- **app/routers/orders.py**: Complete refactoring with atomic transactions
- **Removed**: Old order endpoints, status updates, cancellation, pagination
- **Added**: Transactional order creation, row locking, Inventory Service integration
- **Updated**: Documentation files (logchange.md, prompts.md, README.md, tech.md)

**Critical Transaction Sequence**:
1. **BEGIN** transaction
2. Fetch cart contents with product details
3. Lock rows and check stock for all items
4. Calculate total amount
5. Create Orders record
6. Create OrderItems records
7. Reduce stock via Inventory Service
8. Clear cart
9. **COMMIT** (success) or **ROLLBACK** (failure)

**Technologies Maintained**:
- FastAPI for web framework
- MySQL for database operations with transaction support
- Pydantic for data validation
- mysql-connector-python for database connectivity
- Raw SQL queries as specified
- Transactional operations with proper rollback
- Row locking for concurrency control

---

## User Query: SQLModel ORM Refactoring

**Question**: "i said to there it used raw sql ,but use SQLModel ORM (not plain SQLAlchemy)in every services instead of raw sql for all these services: 2.1. Product Catalogue Service, 2.2. Inventory Service, 2.3. Cart Service, 2.4. Order Service, 2.5. Payment Service (Dummy)"

**Context**: User requested to refactor all services from raw SQL to SQLModel ORM while maintaining the same functionality and API endpoints.

**Requirements Specified**:
- Replace raw SQL queries with SQLModel ORM operations
- Use SQLModel (not plain SQLAlchemy) for all database operations
- Maintain all existing API endpoints and response models
- Keep the same business logic and error handling
- Update database configuration to use SQLModel engine

**Response Strategy**:
1. **Database Configuration Update**: Replace mysql-connector-python with SQLModel engine using PyMySQL
2. **ORM Models Creation**: Create complete SQLModel table models for all entities
3. **Service Refactoring**: Update each service to use SQLModel patterns:
   - Replace raw SQL with `select()` queries
   - Use session dependency injection
   - Implement ORM-based transaction management
4. **Dependencies Update**: Add SQLModel and PyMySQL to requirements.txt
5. **Maintain Functionality**: Ensure all existing features work with ORM

**Implementation Details**:
- **Database Setup**: SQLModel engine with connection pooling
- **Session Management**: Dependency injection with SQLModel Session
- **Query Patterns**: Type-safe ORM queries with `select()` function
- **Relationship Handling**: Automatic foreign key and relationship management
- **Transaction Management**: Simplified session-based transactions
- **Type Safety**: Full type checking with Python type hints

**Benefits Achieved**:
- **Type Safety**: Full type checking throughout the application
- **Code Maintainability**: More readable and maintainable ORM-based code
- **Relationship Management**: Automatic handling of database relationships
- **Query Safety**: Type-safe query construction
- **Pydantic Integration**: Seamless integration with FastAPI models
- **Development Experience**: Better IDE support and error detection

**Technologies Updated**:
- **Added**: `sqlmodel==0.0.14` for ORM functionality
- **Added**: `pymysql==1.1.0` for MySQL database driver
- **Replaced**: Raw SQL queries with SQLModel ORM operations
- **Enhanced**: Database session management and transaction handling
