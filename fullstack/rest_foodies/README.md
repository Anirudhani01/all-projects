# Restaurant Management System

A FastAPI-based backend system for restaurant order management with real-time table tracking, menu management, and payment processing.

## Features and Functionality

### Core Features (Implemented - 2024-12-08 01:07:00)

#### 1. Table Management System
- **12 Table Grid**: 3x4 layout (3 rows, 4 columns) for table numbers 1-12
- **Real-time Status**: Each table shows current status (idle/open/paid)
- **Order Tracking**: Live display of ordered items and running totals
- **Table Operations**: Open new orders, view existing orders, manage table state

#### 2. Menu Management (Enhanced - 2024-12-08 01:07:00)
- **Categorized Menu Items**: Hierarchical organization with main categories (veg/non-veg/beverages) and sub-categories (rice/noodles/starters/biryani)
- **Comprehensive Menu**: 18+ pre-loaded items across multiple categories
- **Menu CRUD Operations**: Create, read, update, delete menu items with full validation
- **Search Functionality**: Real-time search through menu items by name
- **Out-of-Stock Management**: Toggle items as out-of-stock with bulk operations
- **Category-based Filtering**: Filter items by main category and sub-category
- **Price Tracking**: Snapshot prices to maintain historical accuracy
- **Soft Delete**: Menu items can be deactivated without permanent deletion

#### 3. Order Processing
- **Order Creation**: Automatic order creation when first item is added
- **Item Management**: Add, update quantity, remove items from orders
- **Quantity Control**: Prevent negative quantities, automatic item removal
- **Order Status**: Track open vs paid orders with timestamps
- **Order Validation**: Prevent modifications to paid orders

#### 4. Payment System
- **Payment Methods**: Support for Cash and Online payment options
- **Payment Processing**: Mark orders as paid with payment method selection
- **Payment Validation**: Prevent payment on empty orders
- **Payment Tracking**: Record payment timestamp and method
- **Payment Security**: Prevent duplicate payments

#### 5. Admin Dashboard
- **Order History**: View all orders with filtering capabilities
- **Revenue Analytics**: Track total revenue, cash vs online payments
- **Order Metrics**: Count of paid orders, items sold
- **Filtering Options**: Filter by status, table, payment method, date range
- **Real-time Metrics**: Live calculation of sales and performance data

#### 6. Testing & Quality Assurance (New - 2024-12-08 01:07:00)
- **Comprehensive Test Suite**: 50+ test cases covering all endpoints
- **Unit Testing**: Individual endpoint testing with pytest
- **Integration Testing**: Complete workflow testing
- **Error Handling Tests**: Validation of error responses and edge cases
- **Business Logic Tests**: Verification of restaurant-specific rules
- **Test Coverage**: 100% endpoint coverage with positive and negative test cases

### Technical Implementation

#### Database Schema (Updated)
- **MenuItem**: id, name, main_category, sub_category, price, description, is_out_of_stock, is_active
- **Order**: id, table_number, status, opened_at, paid_at, payment_method
- **OrderItem**: id, order_id, menu_item_id, name_snapshot, price_snapshot, quantity

#### API Endpoints (Complete List)
- **Root**: GET `/`
- **Menu Management**: 
  - GET `/menu` - List/search menu items
  - POST `/menu` - Create new menu item
  - GET `/menu/{id}` - Get specific menu item
  - PUT `/menu/{id}` - Update menu item
  - DELETE `/menu/{id}` - Delete menu item (soft delete)
  - PUT `/menu/out-of-stock` - Toggle out-of-stock status
  - GET `/menu/categories` - Get all categories
  - GET `/menu/category/{main}` - Get items by main category
  - GET `/menu/category/{main}/{sub}` - Get items by sub category
- **Table Management**: 
  - GET `/tables` - Get all tables status
  - POST `/tables/{num}/order` - Open order for table
- **Order Management**: 
  - GET `/orders/{id}` - Get order details
  - POST `/orders/{id}/items` - Add item to order
  - PATCH `/orders/{id}/items/{item_id}` - Update item quantity
  - DELETE `/orders/{id}/items/{item_id}` - Delete item from order
  - POST `/orders/{id}/pay` - Pay order
- **Admin Dashboard**: 
  - GET `/admin/orders` - Get all orders with filters
  - GET `/admin/metrics` - Get admin metrics

#### Technology Stack (Updated)
- **Backend Framework**: FastAPI 0.111.0
- **Database**: MySQL with PyMySQL driver
- **ORM**: SQLModel 0.0.16
- **Server**: Uvicorn with standard extras
- **Validation**: Pydantic models for request/response validation
- **Testing**: pytest 7.4.3, httpx 0.25.2
- **Development**: Hot reload with automatic database seeding

#### Testing Framework
- **Test Framework**: pytest with comprehensive test suite
- **Test Database**: SQLite in-memory database for isolated testing
- **Test Coverage**: All endpoints, error cases, and business logic
- **Test Categories**: Unit tests, integration tests, workflow tests
- **Test Execution**: Automated test runner with detailed reporting

### Future Features (Planned)

#### 1. User Authentication & Authorization
- **Staff Accounts**: Individual waiter/staff login credentials
- **Role-based Access**: Different permissions for waiters vs admins
- **Session Management**: Secure login/logout functionality
- **Audit Trail**: Track who performed which actions

#### 2. Enhanced Menu Management
- **Item Images**: Upload and display food item images
- **Seasonal Items**: Mark items as seasonal with availability dates
- **Nutritional Information**: Add calorie and nutritional data
- **Allergen Information**: Track and display allergen information

#### 3. Advanced Order Features
- **Order Notes**: Add special instructions to orders
- **Modifiers**: Customize items (extra cheese, no onions, etc.)
- **Split Bills**: Divide orders among multiple customers
- **Discounts**: Apply percentage or fixed amount discounts
- **Tax Calculation**: Automatic tax calculation based on location

#### 4. Real-time Features
- **WebSocket Integration**: Real-time updates across multiple devices
- **Order Notifications**: Instant notifications for new orders
- **Kitchen Display**: Dedicated kitchen interface for order preparation
- **Customer Display**: Customer-facing order status display

#### 5. Reporting & Analytics
- **Sales Reports**: Daily, weekly, monthly sales reports
- **Popular Items**: Track most ordered items and peak hours
- **Customer Analytics**: Table turnover rates, average order value
- **Export Functionality**: Export data to CSV/Excel formats
- **Dashboard Charts**: Visual representation of sales data

#### 6. Inventory Management
- **Stock Tracking**: Monitor ingredient quantities
- **Low Stock Alerts**: Automatic notifications for low inventory
- **Purchase Orders**: Generate purchase orders for suppliers
- **Cost Analysis**: Track food costs and profit margins

#### 7. Customer Management
- **Customer Database**: Store customer information and preferences
- **Loyalty Program**: Points system and rewards
- **Reservations**: Table booking system
- **Customer Feedback**: Rating and review system

#### 8. Mobile Application
- **Mobile App**: Native mobile application for waiters
- **Offline Mode**: Work without internet connection
- **Push Notifications**: Real-time order updates
- **Barcode Scanning**: Scan items for quick addition

#### 9. Integration Features
- **Payment Gateway**: Integration with payment processors
- **POS Integration**: Connect with existing POS systems
- **Accounting Software**: Export data to accounting systems
- **Third-party Delivery**: Integration with delivery platforms

#### 10. Advanced Admin Features
- **Multi-location Support**: Manage multiple restaurant locations
- **Staff Scheduling**: Manage waiter schedules and assignments
- **Performance Metrics**: Track waiter performance and efficiency
- **System Settings**: Configurable system parameters

## Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL Server
- Virtual environment (recommended)

### Database Setup
1. Create MySQL database: `rest_food`
2. Update database credentials in `backend/database.py`
3. Install dependencies: `pip install -r requirements.txt`

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn backend.main:app --reload

# Access API documentation
# http://127.0.0.1:8000/docs
```

### Running Tests
```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
pytest test/test_all_endpoints.py -v

# Run specific test categories
pytest test/test_all_endpoints.py::TestMenuEndpoints -v
pytest test/test_all_endpoints.py::TestOrderEndpoints -v
pytest test/test_all_endpoints.py::TestAdminEndpoints -v

# Run integration tests
pytest test/test_all_endpoints.py::TestIntegrationWorkflow -v
```

### Environment Variables
- `DATABASE_URL`: MySQL connection string (default: mysql+pymysql://anirudh:password123@localhost:3306/rest_food)

## API Documentation

The complete API documentation is available at `http://127.0.0.1:8000/docs` when the server is running.

## Testing

The project includes a comprehensive test suite with:
- **50+ test cases** covering all endpoints
- **Error handling validation** for edge cases
- **Business logic verification** for restaurant operations
- **Integration testing** for complete workflows
- **Automated test execution** with detailed reporting

### Test Categories
1. **Root Endpoint Tests**: Basic API functionality
2. **Menu Management Tests**: CRUD operations, categories, out-of-stock
3. **Table Management Tests**: Table operations and validation
4. **Order Management Tests**: Order lifecycle and item management
5. **Admin Dashboard Tests**: Analytics and reporting
6. **Integration Workflow Tests**: Complete customer journeys

## Contributing

This is a restaurant management system designed for real-world use. All contributions should maintain the simplicity and reliability of the core functionality while adding value to restaurant operations.

## Project Structure
rest_foodies/
├── backend/
│ ├── init.py
│ ├── main.py # FastAPI application with all endpoints
│ ├── models.py # SQLModel database models
│ ├── schemas.py # Pydantic request/response models
│ └── database.py # Database connection and session management
├── test/
│ └── test_all_endpoints.py # Comprehensive test suite
├── requirements.txt # Python dependencies
├── run.py # Application startup script
├── README.md # Project documentation
└── prompts.md # Development history and prompts