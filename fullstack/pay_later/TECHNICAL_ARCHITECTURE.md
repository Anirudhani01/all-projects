# Pay-Later Application - Technical Architecture

## System Overview

The pay-later application is designed as a modern web application with a focus on scalability, security, and maintainability. The system handles user registration, credit assessment, transaction management, and credit limit operations.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   Mobile App    │    │   Admin Panel   │
│   (JavaScript)  │    │   (Future)      │    │   (React)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      FastAPI Backend      │
                    │    (RESTful API)          │
                    │  ┌─────────────────────┐  │
                    │  │   Authentication    │  │
                    │  │   User Management   │  │
                    │  │   Credit Limits     │  │
                    │  │   Transactions      │  │
                    │  │   Merchants         │  │
                    │  └─────────────────────┘  │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      MongoDB Database     │
                    │   (Document Store)        │
                    │  ┌─────────────────────┐  │
                    │  │   Users Collection  │  │
                    │  │   Credit Limits     │  │
                    │  │   Transactions      │  │
                    │  │   Merchants         │  │
                    │  └─────────────────────┘  │
                    └───────────────────────────┘
```

## Technology Stack Details

### Backend Services

#### 1. FastAPI Application
```python
# Main application structure
pay_later/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py           # Configuration management
│   │   │   ├── security.py         # JWT and security utilities
│   │   │   └── database.py         # MongoDB connection with Motor
│   │   ├── models/
│   │   │   ├── user.py             # User model
│   │   │   ├── transaction.py      # Transaction model
│   │   │   ├── credit_limit.py     # Credit limit model
│   │   │   └── merchant.py         # Merchant model
│   │   ├── schemas/
│   │   │   ├── user.py             # Pydantic schemas
│   │   │   ├── transaction.py      # Transaction schemas
│   │   │   ├── credit_limit.py     # Credit limit schemas
│   │   │   └── merchant.py         # Merchant schemas
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py         # Authentication endpoints
│   │   │   │   ├── users.py        # User management
│   │   │   │   ├── transactions.py # Transaction endpoints
│   │   │   │   ├── credit_limits.py # Credit limit endpoints
│   │   │   │   └── merchants.py    # Merchant endpoints
│   │   │   └── deps.py             # Dependencies
│   │   ├── services/
│   │   │   ├── auth_service.py     # Authentication logic
│   │   │   ├── credit_service.py   # Credit assessment
│   │   │   ├── transaction_service.py # Transaction logic
│   │   │   └── user_service.py     # User management
│   │   └── utils/
│   │       ├── validators.py       # Custom validators
│   │       └── helpers.py          # Utility functions
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
```

#### 2. MongoDB Collections Schema

```python
# User Collection
{
    "_id": ObjectId,
    "email": str,                    # Unique email
    "password_hash": str,            # Hashed password
    "first_name": str,
    "last_name": str,
    "phone": str,
    "date_of_birth": datetime,
    "ssn_hash": str,                 # Hashed SSN
    "address": {
        "street": str,
        "city": str,
        "state": str,
        "zip_code": str,
        "country": str
    },
    "is_active": bool,
    "is_verified": bool,
    "role": str,                     # "user", "admin", "merchant"
    "created_at": datetime,
    "updated_at": datetime
}

# Credit Limit Collection
{
    "_id": ObjectId,
    "user_id": ObjectId,             # Reference to user
    "limit_amount": Decimal,
    "used_amount": Decimal,
    "available_amount": Decimal,     # Calculated field
    "credit_score": int,
    "approval_status": str,          # "pending", "approved", "rejected"
    "approved_by": ObjectId,         # Reference to admin user
    "approved_at": datetime,
    "created_at": datetime,
    "updated_at": datetime
}

# Transaction Collection
{
    "_id": ObjectId,
    "user_id": ObjectId,             # Reference to user
    "merchant_id": ObjectId,         # Reference to merchant
    "transaction_type": str,         # "purchase", "payment", "refund"
    "amount": Decimal,
    "currency": str,                 # Default "USD"
    "status": str,                   # "pending", "completed", "failed", "cancelled"
    "description": str,
    "reference_id": str,
    "payment_method": str,
    "created_at": datetime,
    "updated_at": datetime
}

# Merchant Collection
{
    "_id": ObjectId,
    "name": str,
    "email": str,                    # Unique email
    "phone": str,
    "address": {
        "street": str,
        "city": str,
        "state": str,
        "zip_code": str,
        "country": str
    },
    "business_type": str,
    "tax_id": str,
    "is_active": bool,
    "created_at": datetime,
    "updated_at": datetime
}
```

### Frontend Architecture (React + JavaScript)

```javascript
// Project structure
src/
├── components/
│   ├── common/
│   │   ├── Button.js
│   │   ├── Input.js
│   │   ├── Modal.js
│   │   └── Loading.js
│   ├── layout/
│   │   ├── Header.js
│   │   ├── Sidebar.js
│   │   └── Footer.js
│   └── features/
│       ├── auth/
│       ├── dashboard/
│       ├── transactions/
│       └── credit-limits/
├── pages/
│   ├── Login.js
│   ├── Register.js
│   ├── Dashboard.js
│   ├── Transactions.js
│   └── Profile.js
├── services/
│   ├── api.js
│   ├── auth.js
│   └── transactions.js
├── store/
│   ├── index.js
│   ├── authSlice.js
│   └── transactionSlice.js
├── utils/
│   ├── constants.js
│   ├── helpers.js
│   └── validators.js
└── App.js
```

## Security Architecture

### 1. Authentication & Authorization
- **JWT Tokens**: Stateless authentication with refresh tokens
- **Role-based Access Control**: Admin, User, Merchant roles
- **Password Security**: bcrypt hashing with salt

### 2. Data Protection
- **Encryption**: Sensitive data encryption at rest
- **Hashing**: bcrypt for passwords, SHA-256 for SSN


### 3. API Security
- **Rate Limiting**: Per-user and per-endpoint limits
- **Input Validation**: Pydantic schemas with custom validators
- **CORS**: Configured for specific domains
- **Security Headers**: XSS protection, content security policy

## Credit Assessment Architecture

### 1. Credit Assessment Algorithm
```python
class CreditAssessmentService:
    def calculate_credit_score(self, user_data: UserData) -> int:
        score = 300  # Base score
        
        # Income factor (30%)
        income_score = self._calculate_income_score(user_data.income)
        score += income_score * 0.3
        
        # Payment history (25%)
        payment_score = self._calculate_payment_score(user_data.payment_history)
        score += payment_score * 0.25
        
        # Credit utilization (20%)
        utilization_score = self._calculate_utilization_score(user_data.credit_utilization)
        score += utilization_score * 0.2
        
        # Employment history (15%)
        employment_score = self._calculate_employment_score(user_data.employment_history)
        score += employment_score * 0.15
        
        # Age of credit (10%)
        age_score = self._calculate_age_score(user_data.credit_age)
        score += age_score * 0.1
        
        return min(850, max(300, score))
    
    def determine_credit_limit(self, credit_score: int, income: float) -> float:
        # Credit limit calculation based on score and income
        base_limit = income * 0.3  # 30% of monthly income
        
        if credit_score >= 750:
            multiplier = 1.5
        elif credit_score >= 650:
            multiplier = 1.0
        elif credit_score >= 550:
            multiplier = 0.7
        else:
            multiplier = 0.5
        
        return base_limit * multiplier
```

### 2. Transaction Management
```python
class TransactionService:
    async def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        # Validate transaction data
        # Check credit limit availability
        # Create transaction record
        # Update credit limit usage
        # Send notifications
        pass
    
    async def get_user_transactions(self, user_id: str, filters: dict) -> List[Transaction]:
        # Retrieve user transactions with pagination and filtering
        pass
    
    async def update_transaction_status(self, transaction_id: str, status: str) -> Transaction:
        # Update transaction status
        # Handle status-specific logic
        pass
```

## Database Design with MongoDB

### 1. Indexes for Performance
```python
# User collection indexes
db.users.create_index("email", unique=True)
db.users.create_index("phone")
db.users.create_index("created_at")

# Credit limit collection indexes
db.credit_limits.create_index("user_id")
db.credit_limits.create_index("approval_status")
db.credit_limits.create_index([("user_id", 1), ("created_at", -1)])

# Transaction collection indexes
db.transactions.create_index("user_id")
db.transactions.create_index("merchant_id")
db.transactions.create_index("status")
db.transactions.create_index([("user_id", 1), ("created_at", -1)])
db.transactions.create_index([("merchant_id", 1), ("created_at", -1)])

# Merchant collection indexes
db.merchants.create_index("email", unique=True)
db.merchants.create_index("is_active")
```

### 2. Data Aggregation for Analytics
```python
# Credit limit utilization pipeline
pipeline = [
    {"$match": {"user_id": user_id}},
    {"$group": {
        "_id": "$user_id",
        "total_limit": {"$sum": "$limit_amount"},
        "total_used": {"$sum": "$used_amount"},
        "utilization_rate": {
            "$divide": ["$used_amount", "$limit_amount"]
        }
    }}
]

# Transaction summary pipeline
pipeline = [
    {"$match": {"user_id": user_id}},
    {"$group": {
        "_id": "$transaction_type",
        "count": {"$sum": 1},
        "total_amount": {"$sum": "$amount"}
    }}
]
```

## API Design

### 1. RESTful Endpoints
```python
# Authentication
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout

# Users
GET /api/v1/users/me
PUT /api/v1/users/me
GET /api/v1/users/{user_id}

# Credit Limits
GET /api/v1/credit-limits/me
POST /api/v1/credit-limits/apply
PUT /api/v1/credit-limits/{limit_id}

# Transactions
GET /api/v1/transactions
POST /api/v1/transactions
GET /api/v1/transactions/{transaction_id}
PUT /api/v1/transactions/{transaction_id}

# Merchants
GET /api/v1/merchants
POST /api/v1/merchants
GET /api/v1/merchants/{merchant_id}
```

### 2. Response Format
```python
# Success Response
{
    "success": True,
    "data": {...},
    "message": "Operation successful"
}

# Error Response
{
    "success": False,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {...}
    }
}
```

## Testing Strategy

### 1. Backend Testing with Pytest
```python
# Test structure
tests/
├── conftest.py              # Pytest configuration
├── test_auth.py            # Authentication tests
├── test_users.py           # User management tests
├── test_credit_limits.py   # Credit limit tests
├── test_transactions.py    # Transaction tests
└── utils/
    ├── test_data.py        # Test data fixtures
    └── test_helpers.py     # Test helper functions
```

### 2. Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: API endpoint testing
- **Database Tests**: MongoDB operations testing
- **Security Tests**: Authentication and authorization

## Performance Optimization

### 1. Database Optimization
- **Indexing**: Strategic indexes on frequently queried fields
- **Connection Pooling**: Motor connection pool configuration
- **Query Optimization**: Efficient aggregation pipelines
- **Data Pagination**: Limit result sets

### 2. API Optimization
- **Response Caching**: Cache frequently accessed data
- **Compression**: Gzip compression for responses
- **Pagination**: Limit result sets with skip/limit
- **Field Selection**: Return only required fields

### 3. Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Bundle Optimization**: Webpack optimization
- **Caching**: Browser caching strategies
- **Image Optimization**: Optimized asset delivery

## Compliance & Regulatory Requirements

### 1. GDPR Compliance
- **Data Minimization**: Collect only necessary data
- **User Consent**: Explicit consent for data processing
- **Right to Erasure**: Data deletion capabilities
- **Data Portability**: Export user data functionality


This technical architecture provides a solid foundation for building a scalable, secure, and compliant pay-later application that meets enterprise-grade standards using modern technologies.
