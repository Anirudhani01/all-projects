# Pay-Later Backend

FastAPI backend for the Pay-Later application.

## Features

- FastAPI with async support
- MongoDB with Motor driver
- JWT authentication
- Pydantic data validation
- Comprehensive testing with Pytest
- Enterprise-grade security

## Setup

### Prerequisites

- Python 3.11+
- MongoDB 6.0+

### Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. For development:
```bash
pip install -r requirements-dev.txt
```

4. Copy environment file:
```bash
cp env.example .env
```

5. Update `.env` with your configuration.

### Running the Application

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_health.py
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration and core utilities
│   ├── models/         # MongoDB document models
│   ├── schemas/        # Pydantic validation schemas
│   ├── api/            # API endpoints
│   ├── services/       # Business logic
│   ├── utils/          # Utility functions
│   └── middleware/     # Custom middleware
├── tests/              # Test files
├── requirements.txt    # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Development

### Code Quality

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

### Database

The application uses MongoDB with Motor for async operations. Make sure MongoDB is running and accessible.

### Environment Variables

Key environment variables:
- `MONGODB_URL`: MongoDB connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `SECRET_KEY`: Application secret key
- `DEBUG`: Enable debug mode
- `ENVIRONMENT`: Environment (development/production)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile

### Credit Limits
- `GET /api/v1/credit-limits/me` - Get user's credit limit
- `POST /api/v1/credit-limits/apply` - Apply for credit limit

### Transactions
- `GET /api/v1/transactions` - Get user's transactions
- `POST /api/v1/transactions` - Create new transaction

### Merchants
- `GET /api/v1/merchants` - Get merchants list
- `POST /api/v1/merchants` - Register new merchant

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Input validation with Pydantic
- CORS configuration
- Rate limiting
- Security headers

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass
