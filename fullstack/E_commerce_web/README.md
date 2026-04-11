# E-Commerce Web Application

A modern, scalable e-commerce backend built with FastAPI and MySQL, following a modular monolith architecture.

## 🚀 Features

- **Product Catalogue Service**: Public product browsing with category filtering and stock availability
- **Shopping Cart**: Add, update, and remove items with stock validation
- **Order Processing**: Complete order lifecycle management
- **Payment Processing**: Payment handling with transaction tracking
- **Inventory Management**: Internal stock checking and reduction functions
- **RESTful API**: Comprehensive API with automatic documentation
- **Database**: MySQL with connection pooling for optimal performance

## 🏗️ Architecture

This project follows a **Modular Monolith** pattern with clear separation of concerns:

```
/E_commerce_web
├── app/ 
│   ├── __init__.py 
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # SQLModel database engine and session management
│   ├── models.py            # SQLModel ORM models and Pydantic response models
│   ├── routers/             # API route handlers
│   │   ├── __init__.py 
│   │   ├── products.py      # Product catalogue service (public read-only)
│   │   ├── cart.py          # Cart service with UPSERT operations
│   │   ├── orders.py        # Order service with atomic transactions
│   │   └── payments.py      # Payment service (dummy payment processing)
│   └── services/            # Business logic services
│       ├── __init__.py 
│       └── inventory.py     # Internal inventory functions
└── requirements.txt         # Python dependencies
```

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 0.104.1
- **Database**: MySQL 8.0+
- **ORM**: SQLModel 0.0.14 with PyMySQL 1.1.0
- **Data Validation**: Pydantic 2.5.0
- **ASGI Server**: Uvicorn 0.24.0
- **Authentication**: python-jose[cryptography] 3.3.0
- **Password Hashing**: passlib[bcrypt] 1.7.4
- **Environment Management**: python-dotenv 1.0.0

## 📊 Database Schema

The application uses a comprehensive MySQL schema with 7 main tables:

### Core Tables
- **users**: User accounts and authentication
- **categories**: Product categorization
- **products**: Product catalog with pricing and inventory
- **cart_items**: Shopping cart functionality
- **orders**: Order management and tracking
- **order_items**: Order line items with purchase history
- **payments**: Payment processing and transaction records

### Key Features
- Foreign key relationships for data integrity
- Timestamps for audit trails
- Proper indexing for performance
- Stock quantity tracking
- Order status management

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **MySQL 8.0+**
3. **Virtual Environment**

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd E_commerce_web
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```sql
   -- Create database
   CREATE DATABASE ecom_db;
   
   -- Create user (if needed)
   CREATE USER 'anirudh'@'localhost' IDENTIFIED BY 'password123';
   GRANT ALL PRIVILEGES ON ecom_db.* TO 'anirudh'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Run the application**
   ```bash
   python -m app.main
   ```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Core Endpoints

#### Products (Public Catalogue Service)
- `GET /api/v1/products/` - List all available products (stock > 0)
- `GET /api/v1/products/?category_id={id}` - Filter products by category
- `GET /api/v1/products/{product_id}` - Get specific product details

#### Cart
- `POST /api/v1/cart/{user_id}/items` - Add/update item in cart (UPSERT)
- `GET /api/v1/cart/{user_id}` - Get cart contents with sub-totals
- `PUT /api/v1/cart/{user_id}/items/{product_id}` - Update item quantity
- `DELETE /api/v1/cart/{user_id}/items/{product_id}` - Remove item from cart

#### Orders
- `POST /api/v1/orders/{user_id}` - Create order from cart (atomic transaction)
- `GET /api/v1/orders/{user_id}` - List user's orders
- `GET /api/v1/orders/{user_id}/{order_id}` - Get specific order details

#### Payments
- `POST /api/v1/payments/process` - Process payment
- `GET /api/v1/payments/{payment_id}` - Get payment details
- `GET /api/v1/payments/order/{order_id}` - Get payment by order
- `PUT /api/v1/payments/{payment_id}/status` - Update payment status
- `POST /api/v1/payments/refund/{payment_id}` - Process refund

### Health & Monitoring
- `GET /health` - Health check
- `GET /api/v1/stats` - System statistics

## 🔧 Configuration

### Database Configuration
The application is configured to connect to MySQL with these default settings:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'anirudh',
    'password': 'password123',
    'database': 'ecom_db',
    'charset': 'utf8mb4',
    'autocommit': True
}
```

### Connection Pooling
- Pool size: 10 connections
- Automatic connection reset
- Connection reuse for optimal performance

## 🧪 Testing

### Manual Testing
You can test the API using the interactive documentation at `http://localhost:8000/docs`

### Example API Calls

1. **Browse Products (Public)**
   ```bash
   # Get all available products
   curl -X GET "http://localhost:8000/api/v1/products/"
   
   # Get products by category
   curl -X GET "http://localhost:8000/api/v1/products/?category_id=1"
   
   # Get specific product
   curl -X GET "http://localhost:8000/api/v1/products/1"
   ```

2. **Cart Operations**
   ```bash
   # Add item to cart (UPSERT)
   curl -X POST "http://localhost:8000/api/v1/cart/1/items" \
        -H "Content-Type: application/json" \
        -d '{
          "product_id": 1,
          "quantity": 2
        }'
   
   # View cart with sub-totals
   curl -X GET "http://localhost:8000/api/v1/cart/1"
   
   # Update item quantity
   curl -X PUT "http://localhost:8000/api/v1/cart/1/items/1" \
        -H "Content-Type: application/json" \
        -d '{
          "product_id": 1,
          "quantity": 3
        }'
   
   # Remove item from cart
   curl -X DELETE "http://localhost:8000/api/v1/cart/1/items/1"
   ```

3. **Order Operations**
   ```bash
   # Create order from cart (atomic transaction)
   curl -X POST "http://localhost:8000/api/v1/orders/1"
   
   # View user's order list
   curl -X GET "http://localhost:8000/api/v1/orders/1"
   
   # Get specific order details
   curl -X GET "http://localhost:8000/api/v1/orders/1/123"
   ```

## 🔒 Security Features

- **Input Validation**: Comprehensive Pydantic model validation
- **SQL Injection Protection**: Parameterized queries
- **Error Handling**: Proper error responses without sensitive data exposure
- **CORS Configuration**: Configurable cross-origin resource sharing

## 📈 Performance Features

- **Connection Pooling**: Efficient database connection management
- **Pagination**: Large dataset handling
- **Indexing**: Optimized database queries
- **Caching Ready**: Architecture supports caching implementation

## 🔄 Development Workflow

### Adding New Features
1. Create Pydantic models in `models.py`
2. Implement business logic in `services/` (internal functions)
3. Add API endpoints in `routers/` (public services)
4. Update database schema if needed
5. Test thoroughly using the interactive docs

### Code Style
- Follow PEP 8 guidelines
- Use type hints throughout
- Document all functions and classes
- Implement proper error handling

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Use `.env` files for configuration
2. **Database**: Use production MySQL instance
3. **Security**: Implement proper authentication and authorization
4. **Monitoring**: Add logging and monitoring
5. **SSL**: Configure HTTPS in production

### Docker Support
The application can be containerized for easy deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the code comments
- Open an issue in the repository

## 🔄 Version History

See [CHANGELOG.md](logchange.md) for detailed version history and updates.
