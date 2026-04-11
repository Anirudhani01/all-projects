# Change Log

## [1.5.0] - 2024-12-19

### Changed
- **Complete SQLModel ORM Refactoring**
  - Refactored all services from raw SQL to SQLModel ORM
  - Updated database configuration to use SQLModel engine with PyMySQL
  - Replaced mysql-connector-python with SQLModel session management
  - Updated all routers and services to use ORM patterns

### Added
- **SQLModel ORM Models**
  - Complete SQLModel table models for all entities (User, Category, Product, CartItem, Order, OrderItem, Payment)
  - Proper relationship definitions with back_populates
  - Type-safe field definitions with SQLField
- **New Dependencies**
  - `sqlmodel==0.0.14` for ORM functionality
  - `pymysql==1.1.0` for MySQL database driver

### Technical Improvements
- **Type Safety**: Full type checking with Python type hints throughout
- **Relationship Management**: Automatic handling of foreign keys and relationships
- **Query Building**: Type-safe query construction with `select()` function
- **Transaction Management**: Simplified transaction handling with session management
- **Code Maintainability**: More readable and maintainable ORM-based code
- **Pydantic Integration**: Seamless integration with FastAPI's Pydantic models

### Services Refactored
- **Product Catalogue Service**: Updated to use SQLModel `select()` queries
- **Inventory Service**: Refactored to use SQLModel session instead of cursor
- **Cart Service**: Replaced raw SQL with SQLModel ORM operations and UPSERT logic
- **Order Service**: Updated to use SQLModel transactions for atomic operations
- **Payment Service**: Refactored to use SQLModel session management

### Database Changes
- **Engine Configuration**: SQLModel engine with connection pooling
- **Session Management**: Dependency injection with SQLModel Session
- **Table Creation**: SQLModel metadata-based table initialization
- **Query Patterns**: Replaced raw SQL with type-safe ORM queries

## [1.4.0] - 2024-12-19

### Changed
- **Order Service Refactoring**
  - Refactored orders router to implement new Order Service requirements
  - Updated API endpoints to use user_id in URL path (Phase 1 approach)
  - Implemented atomic transactional order creation with proper rollback
  - Added integration with Inventory Service for stock management
  - Implemented exact SQL queries as specified in requirements

### Added
- **New Order Service Models**
  - `OrderItemResponse`: For individual order items with product details
  - `OrderResponse`: For complete order details with all line items
  - `OrderSummaryResponse`: For order list summaries

### API Endpoint Changes
- **POST /orders/{user_id}**: Create order from cart with atomic transaction (201 Created)
- **GET /orders/{user_id}**: Retrieve user's order list (200 OK)
- **GET /orders/{user_id}/{order_id}**: Retrieve specific order details (200 OK)

### Removed
- **Old Order Endpoints**
  - Removed `/orders/create` with query parameter approach
  - Removed `/orders/{order_id}` with query parameters
  - Removed order status update and cancellation endpoints
  - Removed pagination and complex filtering

### SQL Query Updates
- **Cart Contents**: `SELECT ci.product_id, ci.quantity, p.name, p.price, p.stock_quantity FROM CartItems ci JOIN Products p ON ci.product_id = p.product_id WHERE ci.user_id = %s`
- **Stock Locking**: `SELECT stock_quantity FROM Products WHERE product_id = %s FOR UPDATE`
- **Order Creation**: `INSERT INTO Orders (user_id, total_amount, status) VALUES (%s, %s, 'PENDING')`
- **Order Items**: `INSERT INTO OrderItems (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s)`
- **Cart Clearing**: `DELETE FROM CartItems WHERE user_id = %s`
- **Order List**: `SELECT order_id, status, total_amount, created_at FROM Orders WHERE user_id = %s ORDER BY created_at DESC`
- **Order Details**: `SELECT order_id, status, total_amount, created_at FROM Orders WHERE order_id = %s AND user_id = %s`
- **Order Items**: `SELECT product_id, quantity, price_at_purchase FROM OrderItems WHERE order_id = %s`

### Functional Requirements Met
- ✅ FR10: User can create atomic order from cart with rollback on failure
- ✅ FR11: Cart is automatically cleared after successful order creation
- ✅ FR12: User can view list of all past orders
- ✅ FR13: User can view detailed order information with all line items

### Architecture Changes
- **Transactional Management**: Complete BEGIN/COMMIT/ROLLBACK implementation
- **Row Locking**: FOR UPDATE to prevent race conditions during stock checking
- **Inventory Integration**: Uses reduce_stock() from Inventory Service
- **Atomic Operations**: All-or-nothing order creation process
- **URL Structure**: user_id now in path instead of query parameters
- **Response Format**: Direct OrderResponse objects instead of APIResponse wrapper

### Critical Transaction Sequence
1. **BEGIN** transaction
2. Fetch cart contents with product details
3. Lock rows and check stock for all items
4. Calculate total amount
5. Create Orders record
6. Create OrderItems records
7. Reduce stock via Inventory Service
8. Clear cart
9. **COMMIT** (success) or **ROLLBACK** (failure)

## [1.3.0] - 2024-12-19

### Changed
- **Cart Service Refactoring**
  - Refactored cart router to implement new Cart Service requirements
  - Updated API endpoints to use user_id in URL path (Phase 1 approach)
  - Implemented exact SQL queries as specified in requirements
  - Added UPSERT functionality for adding/updating cart items

### Added
- **New Cart Service Models**
  - `CartItemRequest`: For adding/updating cart items with positive quantity validation
  - `CartItemResponse`: For cart item details with sub_total calculation
  - `CartResponse`: For complete cart view with items and total_price

### API Endpoint Changes
- **POST /cart/{user_id}/items**: Add/update item with UPSERT operation (201/200 responses)
- **GET /cart/{user_id}**: Retrieve cart with CartResponse format
- **DELETE /cart/{user_id}/items/{product_id}**: Remove item (204 No Content)
- **PUT /cart/{user_id}/items/{product_id}**: Update item quantity (200 OK)

### Removed
- **Old Cart Endpoints**
  - Removed `/cart/add` with query parameter approach
  - Removed `/cart/{cart_item_id}` update endpoint
  - Removed `/cart/clear` endpoint
  - Removed complex cart item ID-based operations

### SQL Query Updates
- **UPSERT Operation**: `INSERT INTO CartItems ... ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)`
- **Cart View**: `SELECT ci.product_id, p.name, p.price, ci.quantity FROM CartItems ci JOIN Products p ON ci.product_id = p.product_id WHERE ci.user_id = %s`
- **Remove Item**: `DELETE FROM CartItems WHERE user_id = %s AND product_id = %s`
- **Update Quantity**: `UPDATE CartItems SET quantity = %s WHERE user_id = %s AND product_id = %s`

### Functional Requirements Met
- ✅ FR6: User can add/update product quantity in cart with UPSERT functionality
- ✅ FR7: User can view cart with product details and sub-totals
- ✅ FR8: User can remove items completely from cart
- ✅ FR9: User can update specific item quantities in cart

### Architecture Changes
- **URL Structure**: user_id now in path instead of query parameters
- **Response Format**: Direct CartResponse objects instead of APIResponse wrapper
- **UPSERT Logic**: Automatic handling of existing items vs new items
- **Sub-total Calculation**: Automatic calculation of item and cart totals

## [1.2.0] - 2024-12-19

### Changed
- **Inventory Service Refactoring**
  - Refactored from class-based to function-based approach
  - Removed complex business logic methods in favor of simple, focused functions
  - Implemented exact SQL queries as specified in requirements
  - Made service internal-only (no public HTTP endpoints)

### Added
- **Internal Inventory Functions**
  - `check_stock(db_cursor, product_id: int) -> int`: Returns current stock quantity
  - `reduce_stock(db_cursor, product_id: int, quantity: int) -> bool`: Decrements stock with concurrency control

### Removed
- **Complex Inventory Methods**
  - Removed `InventoryService` class and all its methods
  - Removed stock movement tracking, low stock monitoring, inventory summary
  - Removed public HTTP endpoints for inventory operations

### SQL Query Updates
- **check_stock**: `SELECT stock_quantity FROM Products WHERE product_id = %s`
- **reduce_stock**: `UPDATE Products SET stock_quantity = stock_quantity - %s WHERE product_id = %s AND stock_quantity >= %s`
- Added concurrency control to prevent overselling

### Functional Requirements Met
- ✅ FR4: System provides mechanism to check available stock for a given product ID
- ✅ FR5: System provides mechanism to decrease stock level with failure on insufficient stock

### Architecture Changes
- **Internal Service**: Inventory Service now functions as internal service called by other services
- **Security**: No public HTTP endpoints for inventory operations
- **Modularity**: Simplified functions for direct integration with Order Service and other internal components

## [1.1.0] - 2024-12-19

### Changed
- **Product Catalogue Service Refactoring**
  - Refactored products router from full CRUD to read-only public service
  - Removed POST, PUT, DELETE endpoints for public product browsing
  - Implemented new ProductResponse model for public API responses
  - Added stock_quantity > 0 filter to show only available products

### Added
- **ProductResponse Model**
  - New Pydantic model for public product API responses
  - Simplified response structure: product_id, name, description, price, stock_quantity, category_id
  - Direct response format without wrapper objects

### API Changes
- **GET /products/** - Now returns List[ProductResponse] with optional category filtering
- **GET /products/{product_id}** - Now returns ProductResponse directly
- **Removed endpoints**: POST /products/, PUT /products/{product_id}, DELETE /products/{product_id}

### SQL Query Updates
- Implemented exact SQL queries as specified in requirements
- Added stock availability filtering (WHERE stock_quantity > 0)
- Simplified queries to return only required fields for public browsing

### Functional Requirements Met
- ✅ FR1: Any user can retrieve a list of all products available for sale
- ✅ FR2: Product list is filterable by category
- ✅ FR3: Any user can retrieve detailed information for a single product using its unique ID

## [1.0.0] - 2024-12-19

### Added
- **Phase 1 - Modular Monolith Foundation**
  - Complete FastAPI + MySQL backend implementation
  - Modular project structure with routers and services
  - Database schema with 7 tables: users, categories, products, cart_items, orders, order_items, payments
  - Connection pooling for MySQL database
  - Pydantic models for data validation
  - Raw SQL implementation for all database operations

### Features Implemented
- **Products Module**
  - CRUD operations for products
  - Pagination and filtering support
  - Category association
  - Stock quantity management

- **Cart Module**
  - Add/remove items from cart
  - Update cart item quantities
  - Stock validation
  - Cart clearing functionality

- **Orders Module**
  - Create orders from cart items
  - Order status management
  - Order cancellation with stock restoration
  - Order history with pagination

- **Payments Module**
  - Payment processing simulation
  - Payment status tracking
  - Refund functionality
  - Transaction ID generation

- **Inventory Service**
  - Stock availability checking
  - Stock reservation and restoration
  - Low stock monitoring
  - Inventory statistics

### Technical Details
- **Database**: MySQL with connection pooling
- **Framework**: FastAPI with automatic API documentation
- **Validation**: Pydantic models with comprehensive validation
- **Architecture**: Modular monolith with clear separation of concerns
- **API**: RESTful endpoints with consistent response format

### Database Schema
- **users**: User management with email and password hash
- **categories**: Product categorization
- **products**: Product catalog with pricing and stock
- **cart_items**: Shopping cart functionality
- **orders**: Order management with status tracking
- **order_items**: Order line items with purchase price
- **payments**: Payment processing and tracking

### API Endpoints
- `/api/v1/products/*` - Product management
- `/api/v1/cart/*` - Shopping cart operations
- `/api/v1/orders/*` - Order management
- `/api/v1/payments/*` - Payment processing
- `/health` - Health check
- `/api/v1/stats` - System statistics

### Dependencies
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- mysql-connector-python==8.2.0
- pydantic==2.5.0
- python-multipart==0.0.6
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- python-dotenv==1.0.0
