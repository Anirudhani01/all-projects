# Technology Stack Documentation

## Core Technologies

### Backend Framework
- **FastAPI 0.104.1** - Modern, fast web framework for building APIs with Python
  - Automatic API documentation generation
  - Built-in data validation
  - High performance with async support
  - Type hints integration

### Database & ORM
- **MySQL 8.0+** - Relational database management system
  - ACID compliance
  - Transaction support
  - Foreign key constraints
  - Indexing for performance
- **SQLModel 0.0.14** - Modern Python library for SQL databases
  - Pydantic integration for data validation
  - Type-safe ORM operations
  - Automatic relationship management
  - SQLAlchemy compatibility
- **PyMySQL 1.1.0** - Pure Python MySQL client library
  - SQLModel database driver
  - Connection pooling support
  - Session-based transaction management

### Data Validation & Serialization
- **Pydantic 2.5.0** - Data validation using Python type annotations
  - Automatic data validation
  - JSON serialization/deserialization
  - Model generation from JSON schemas
  - Field validation and constraints

### ASGI Server
- **uvicorn[standard] 0.24.0** - Lightning-fast ASGI server
  - HTTP/1.1 and HTTP/2 support
  - WebSocket support
  - Automatic reloading for development
  - Production-ready performance

### Authentication & Security
- **python-jose[cryptography] 3.3.0** - JavaScript Object Signing and Encryption
  - JWT token handling
  - Cryptographic operations
  - Token validation and verification

### Password Security
- **passlib[bcrypt] 1.7.4** - Password hashing library
  - Secure password hashing with bcrypt
  - Password verification
  - Salt generation
  - Multiple hash algorithms support

### Environment Management
- **python-dotenv 1.0.0** - Environment variable management
  - .env file loading
  - Environment variable parsing
  - Configuration management

### File Upload Support
- **python-multipart 0.0.6** - Multipart form data parsing
  - File upload handling
  - Form data processing
  - Multipart request support

## Architecture Components

### Modular Structure
- **Routers** - API endpoint handlers organized by domain
  - `products.py` - Product Catalogue Service (public read-only endpoints)
  - `cart.py` - Cart Service with UPSERT operations and user_id path parameters
  - `orders.py` - Order Service with atomic transactions and Inventory Service integration
  - `payments.py` - Payment processing

### Services Layer
- **Product Catalogue Service** - Public product browsing service
  - Stock availability filtering (stock_quantity > 0)
  - Category-based product filtering
  - Simplified response format for public access
  - Direct ProductResponse model usage
- **Inventory Service** - Internal inventory management functions
  - `check_stock()` - Returns current stock quantity for a product
  - `reduce_stock()` - Decrements stock with concurrency control
  - No public HTTP endpoints (internal service only)
  - Transactional updates to prevent overselling

### Data Models
- **SQLModel ORM Models** - Database table models with relationships
  - User, Category, Product, CartItem, Order, OrderItem, Payment
  - Proper foreign key relationships with back_populates
  - Type-safe field definitions with SQLField
  - Automatic table creation and schema management
- **Pydantic Response Models** - API response validation and serialization
  - User models (UserBase, UserCreate, User, UserLogin)
  - Product models (ProductBase, ProductCreate, Product, ProductUpdate, ProductResponse)
  - Cart models (CartItem, CartItemCreate, CartItemUpdate, CartItemRequest, CartItemResponse, CartResponse)
  - Order models (Order, OrderCreate, OrderUpdate, OrderItemResponse, OrderResponse, OrderSummaryResponse)
  - Payment models (Payment, PaymentCreate, PaymentUpdate)
  - Response models (APIResponse, PaginatedResponse)

### Database Schema
- **7 Core Tables** with proper relationships
  - users - User accounts and authentication
  - categories - Product categorization
  - products - Product catalog with pricing and inventory
  - cart_items - Shopping cart functionality
  - orders - Order management and tracking
  - order_items - Order line items with purchase history
  - payments - Payment processing and transaction records

## Development Tools

### Code Quality
- **Type Hints** - Throughout the codebase for better IDE support
- **Docstrings** - Comprehensive documentation for all functions
- **Error Handling** - Proper exception handling and user-friendly error messages

### API Documentation
- **Swagger UI** - Interactive API documentation at `/docs`
- **ReDoc** - Alternative API documentation at `/redoc`
- **OpenAPI 3.0** - Standard API specification

### Testing Support
- **Interactive Testing** - Built-in API testing through Swagger UI
- **Health Checks** - System health monitoring endpoints
- **Statistics Endpoints** - System metrics and analytics

## Performance Features

### Database Optimization
- **SQLModel Engine** - Efficient database connection management with pooling
- **Type-Safe Queries** - SQLModel select() queries with full type checking
- **Proper Indexing** - Database indexes for fast query execution
- **Session Management** - SQLModel session-based transaction handling
- **Concurrency Control** - ORM-level constraints to prevent overselling
- **Relationship Management** - Automatic foreign key and relationship handling

### API Performance
- **Pagination** - Large dataset handling with pagination support
- **CORS Support** - Cross-origin resource sharing configuration
- **Async Support** - Non-blocking I/O operations
- **Caching Ready** - Architecture supports caching implementation

## Security Features

### Data Protection
- **Input Validation** - Comprehensive Pydantic model validation
- **SQL Injection Protection** - Parameterized queries throughout
- **Error Handling** - Secure error responses without sensitive data exposure
- **Password Hashing** - Secure password storage with bcrypt

### API Security
- **CORS Configuration** - Configurable cross-origin resource sharing
- **Request Validation** - Automatic request data validation
- **Response Sanitization** - Clean response formatting

## Deployment & Operations

### Containerization Support
- **Docker Ready** - Containerization support for easy deployment
- **Environment Variables** - Configuration through environment variables
- **Health Monitoring** - Built-in health check endpoints

### Production Features
- **Connection Pooling** - Optimized database connections
- **Error Logging** - Comprehensive error handling and logging
- **Performance Monitoring** - Built-in statistics and monitoring endpoints

## Future Technology Considerations

### Potential Additions
- **Redis** - Caching layer for improved performance
- **Celery** - Background task processing
- **Elasticsearch** - Advanced search functionality
- **Docker Compose** - Multi-service deployment
- **Kubernetes** - Container orchestration
- **Prometheus** - Metrics collection and monitoring
- **Grafana** - Visualization and alerting

### Scalability Options
- **Microservices Migration** - Architecture supports future microservices split
- **Database Sharding** - Horizontal scaling support
- **Load Balancing** - Multiple instance deployment ready
- **CDN Integration** - Static content delivery optimization
