# Ecommerce Application Knowledge Base

## Application Overview
This is a comprehensive ecommerce CLI application with the following key components:

### Core Entities

#### Products
- **Model**: Product with fields like name, description, price, category, stock_quantity, SKU, brand
- **Categories**: electronics, clothing, books, home_garden, sports, beauty, automotive
- **Operations**: Create, read, update, delete, search by name/description/tags
- **Validation**: SKU format validation, price constraints, stock management
- **Business Rules**: 
  - SKU must be alphanumeric with hyphens/underscores
  - Price must be positive decimal with 2 decimal places
  - Stock quantity cannot be negative
  - Products can be soft-deleted (is_active flag)

#### Users  
- **Model**: User with username, email, name, phone, role, address
- **Roles**: Admin, Customer, Seller
- **Operations**: Registration, authentication, profile management
- **Validation**: 
  - Email format validation with regex
  - Username must be 3-50 characters, alphanumeric with hyphens/underscores
  - Phone number validation for international formats
  - Unique username and email constraints

#### Orders
- **Model**: Order with items, status, totals, addresses, payment info
- **Statuses**: Pending, Confirmed, Shipped, Delivered, Cancelled
- **Operations**: Create from cart, update status, track progress
- **Business Rules**: 
  - Stock reservation during order creation
  - Price calculation: subtotal + shipping + tax - discounts
  - Order total validation against item totals
  - Status transition validation

#### Shopping Cart
- **Model**: Cart with items, quantities, totals
- **Operations**: Add/remove items, update quantities, checkout
- **Features**: 
  - Session persistence with expiration
  - Real-time total calculation
  - Stock availability checking
  - Item quantity validation

#### Inventory
- **Model**: Inventory tracking with available/reserved quantities
- **Features**: 
  - Stock checks and reservations
  - Reorder level monitoring
  - Low stock alerts
  - Concurrent access handling
- **Calculations**:
  - quantity_in_stock = quantity_available - quantity_reserved
  - needs_restock = quantity_available <= reorder_level

#### Reviews
- **Model**: Product reviews with ratings, comments, verification
- **Features**: 
  - Rating scale 1-5 validation
  - Verified purchase validation
  - Helpful votes tracking
  - Content length validation (1-2000 characters)

### API Endpoints (CLI Commands)

#### Product Management
- `products list [--category] [--search]` - List/search products
  - Supports category filtering and text search
  - Returns active products by default
- `products show <id>` - Get product details with inventory and reviews
- `products add` - Create new product with validation

#### Order Management  
- `orders list [--user] [--status]` - List orders with filtering
- `orders show <id>` - Get order details with items and user info
- `orders create --user <username>` - Create order from user's cart
  - Validates stock availability
  - Calculates totals with tax and shipping
  - Reserves inventory

#### User Management
- `users list` - List all users with role information

#### Inventory Management
- `inventory status` - Check inventory levels and low stock alerts
- `stats <product_id>` - Get comprehensive product statistics

### Business Rules

1. **Stock Management**: 
   - Products must have sufficient inventory before order creation
   - Stock is reserved during order processing
   - Fulfilled orders reduce available inventory

2. **Price Calculations**: 
   - Subtotal = sum of (quantity × unit_price) for all items
   - Shipping = $10.00 for orders under $100, free for $100+
   - Tax = 8% of subtotal
   - Total = subtotal + shipping + tax - discounts

3. **Order Workflow**: 
   - Cart → Stock Check → Order Creation → Payment → Fulfillment → Delivery
   - Status transitions: pending → confirmed → shipped → delivered
   - Cancellation allowed only in pending/confirmed states

4. **User Permissions**: 
   - Admin: Full access to all operations
   - Customer: Access to own orders and cart
   - Seller: Product management capabilities

5. **Data Integrity**: 
   - Referential integrity between orders, products, users
   - UUID-based primary keys
   - Timestamp tracking for all entities

### Error Scenarios

1. **Insufficient Stock**: 
   - Orders fail if product stock is unavailable
   - Cart items become invalid if stock decreases
   - Proper error messages for out-of-stock conditions

2. **Invalid User Data**: 
   - Registration fails with invalid email/username formats
   - Duplicate username/email validation
   - Password strength requirements

3. **Payment Processing**: 
   - Orders can fail during payment processing
   - Stock reservations need cleanup on payment failure
   - Retry mechanisms for transient failures

4. **System Limits**: 
   - File size limits for product images
   - Rate limiting for API endpoints
   - Concurrent access controls

### Performance Considerations

1. **Database Operations**: 
   - Efficient querying with proper indexing
   - Pagination for large result sets
   - Optimized search operations

2. **Search Operations**: 
   - Full-text search across product names, descriptions, tags
   - Category-based filtering
   - Brand and SKU search capabilities

3. **Inventory Updates**: 
   - Atomic operations for stock management
   - Concurrent stock reservation handling
   - Real-time stock level updates

4. **Large Datasets**: 
   - Pagination for product listings
   - Lazy loading for product details
   - Efficient JSON serialization

### Security Aspects

1. **Authentication**: 
   - User login and session management
   - Password hashing and validation
   - Session timeout handling

2. **Authorization**: 
   - Role-based access control
   - Operation-level permissions
   - Data ownership validation

3. **Data Validation**: 
   - Input sanitization and validation
   - SQL injection prevention
   - XSS protection for text fields

4. **PII Protection**: 
   - Secure handling of customer data
   - Address and payment information protection
   - Data anonymization for analytics

### Integration Points

1. **Payment Processing**: 
   - External payment gateway integration
   - Multiple payment method support
   - Secure transaction handling

2. **Shipping**: 
   - Shipping provider APIs
   - Real-time shipping calculations
   - Tracking number integration

3. **Notifications**: 
   - Email/SMS notification services
   - Order status updates
   - Marketing communications

4. **Analytics**: 
   - Reporting and business intelligence
   - Sales performance metrics
   - Customer behavior analysis

### Testing Considerations

1. **Unit Testing**: 
   - Model validation logic
   - Business rule implementations
   - Calculation accuracy

2. **Integration Testing**: 
   - API endpoint functionality
   - Database operations
   - Service integrations

3. **End-to-End Testing**: 
   - Complete user workflows
   - Order processing pipelines
   - Error handling scenarios

4. **Performance Testing**: 
   - Load testing for concurrent users
   - Stress testing for peak loads
   - Database performance under load

5. **Security Testing**: 
   - Input validation testing
   - Authentication bypass attempts
   - Authorization boundary testing

### Data Model Relationships

```
User (1) ←→ (N) Order
User (1) ←→ (1) Cart
Order (1) ←→ (N) OrderItem
Product (1) ←→ (N) OrderItem
Product (1) ←→ (1) Inventory
Product (1) ←→ (N) Review
User (1) ←→ (N) Review
```

### Sample Data Patterns

#### Valid Test Data:
- **Email**: user@example.com, test.user+tag@domain.co.uk
- **Phone**: +1234567890, +44-20-7946-0958
- **SKU**: PROD-001, IPHONE-15-PRO-256GB
- **Price**: 99.99, 1999.00, 0.01

#### Invalid Test Data:
- **Email**: invalid-email, @domain.com, user@
- **Phone**: 123, +invalid, phone-number
- **SKU**: prod@001, sku with spaces, special#chars
- **Price**: -10.00, 0.00, 999999999.99

This knowledge base should be used to generate realistic test scenarios that cover all aspects of the ecommerce application, including edge cases, error conditions, and performance requirements.
