# Shopping Cart Backend API (Python/FastAPI)

A comprehensive backend API for an online shopping cart system built with Python, FastAPI, and SQLAlchemy. Features include inventory validation, user authentication, and robust error handling.

## Features

- **Shopping Cart Management**: Add, remove, and view cart items
- **Inventory Validation**: Real-time stock checking and updates
- **User Authentication**: JWT-based authentication system
- **Input Validation**: Comprehensive validation using Pydantic models
- **Security**: SQL injection prevention and secure authentication
- **Database**: SQLite database with SQLAlchemy ORM
- **Testing**: Comprehensive pytest test suite with coverage reporting

## Technology Stack

- **Framework**: FastAPI (modern, fast web framework for Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Authentication**: JWT tokens with python-jose
- **Validation**: Pydantic models with automatic validation
- **Testing**: pytest with FastAPI TestClient
- **Documentation**: Automatic API docs with Swagger UI

## Project Structure

```
shopping-cart-backend/
├── database/
│   └── database.py           # Database models and configuration
├── middleware/
│   └── auth.py               # JWT authentication middleware
├── routes/
│   ├── auth.py               # Authentication routes (login/register)
│   ├── cart.py               # Shopping cart operations
│   └── items.py              # Item management and retrieval
├── schemas/
│   └── schemas.py            # Pydantic models for validation
├── tests/
│   └── test_cart.py          # Comprehensive test suite
├── main.py                   # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── pytest.ini               # pytest configuration
└── README.md                 # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Shopping Cart
- `POST /api/cart/add` - Add item to cart
- `GET /api/cart` - Get user's cart contents
- `DELETE /api/cart/{item_id}` - Remove item from cart
- `DELETE /api/cart` - Clear entire cart

### Items
- `GET /api/items` - Get all items
- `GET /api/items/{id}` - Get item by ID
- `GET /api/items/category/{category}` - Get items by category
- `GET /api/items/search/{query}` - Search items
- `GET /api/items/inventory/low-stock` - Get low stock items

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd shopping-cart-backend
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

4. **Start the server**
   ```bash
   python main.py
   ```

   Or for development with auto-reload:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Database Setup

The application automatically creates a SQLite database with sample data on first run:

- **Users table**: User accounts and authentication
- **Items table**: Product catalog with inventory
- **Cart table**: Shopping cart items for each user

Sample data includes:
- Test user: `testuser` / `anypassword`
- Sample products: Laptop, Smartphone, Headphones, Book, T-shirt

## Testing

The project includes comprehensive test cases covering all the scenarios from the test plan:

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_cart.py

# Run specific test class
pytest tests/test_cart.py::TestShoppingCartAPI

# Run specific test method
pytest tests/test_cart.py::TestShoppingCartAPI::test_tc001_add_valid_item_to_cart_with_sufficient_inventory
```

### Test Coverage

The test suite covers all 12 test cases (TC001-TC012):

- **TC001**: Add valid item to cart with sufficient inventory
- **TC002**: Add item to cart with insufficient inventory
- **TC003**: Add item to cart with invalid item ID
- **TC004**: Add item to cart with zero quantity
- **TC005**: Add item to cart with negative quantity
- **TC006**: Add item to cart with maximum quantity (boundary)
- **TC007**: Add item to cart with quantity exceeding system limit
- **TC008**: Add item to cart with decimal quantity
- **TC009**: Add item to cart with special characters in item ID
- **TC010**: Add item to cart with expired user session
- **TC011**: Add item to cart with concurrent requests (race condition)
- **TC012**: Add item to cart with database connection failure

## API Usage Examples

### 1. User Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "anypassword"}'
```

### 2. Add Item to Cart
```bash
curl -X POST "http://localhost:8000/api/cart/add" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 2}'
```

### 3. View Cart
```bash
curl -X GET "http://localhost:8000/api/cart" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 4. Get All Items
```bash
curl -X GET "http://localhost:8000/api/items"
```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Comprehensive validation using Pydantic
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **Password Hashing**: bcrypt password hashing
- **CORS**: Configurable cross-origin resource sharing

## Error Handling

The API provides consistent error responses:
- **400**: Bad Request (validation errors, insufficient inventory)
- **401**: Unauthorized (missing authentication)
- **404**: Not Found (item not found)
- **422**: Validation Error (Pydantic validation failures)
- **500**: Internal Server Error (database errors, system failures)

## Development

### Environment Variables
- `SECRET_KEY`: Secret key for JWT tokens
- `DATABASE_URL`: Database connection string

### Adding New Features
1. Create route handlers in the appropriate route file
2. Add Pydantic models in schemas.py if needed
3. Update the test suite with new test cases
4. Update this README with new endpoints

## Dependencies

### Production
- `fastapi`: Modern web framework for building APIs
- `uvicorn`: ASGI server for running FastAPI
- `sqlalchemy`: SQL toolkit and ORM
- `pydantic`: Data validation using Python type annotations
- `python-jose`: JWT implementation
- `passlib`: Password hashing library
- `python-multipart`: Form data parsing

### Development & Testing
- `pytest`: Testing framework
- `pytest-asyncio`: Async support for pytest
- `httpx`: HTTP client for testing
- `pytest-cov`: Coverage reporting

## Performance Features

- **Async Support**: Built-in async/await support for high performance
- **Automatic Validation**: Pydantic models provide automatic request/response validation
- **Type Hints**: Full Python type hints for better development experience
- **OpenAPI**: Automatic API documentation generation

## License

MIT License - see LICENSE file for details.
