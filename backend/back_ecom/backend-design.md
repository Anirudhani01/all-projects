# E-Commerce Backend Design Document

## 🏗️ **Architecture Overview**

### **Technology Stack**
- **Framework**: FastAPI (Python 3.8+)
- **Database**: MongoDB with Motor (async driver)
- **Authentication**: JWT with PyJWT(value based authentication)
- **Validation**: Pydantic models
- **Documentation**: Auto-generated OpenAPI/Swagger
- **Testing**: pytest with async support
- **Deployment**: uvicorn

### **Project Structure**
```
ecommerce-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py         # Environment settings
│   │   └── database.py         # Database configuration
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── product.py          # Product schemas
│   │   ├── user.py             # User schemas
│   │   ├── review.py           # Review schemas
│   │   └── wishlist.py         # Wishlist schemas
│   ├── schemas/                # Database schemas
│   │   ├── __init__.py
│   │   ├── product.py          # MongoDB product schema
│   │   ├── user.py             # MongoDB user schema
│   │   ├── review.py           # MongoDB review schema
│   │   └── wishlist.py         # MongoDB wishlist schema
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── v1/                 # API version 1
│   │   │   ├── __init__.py
│   │   │   ├── products.py     # Product endpoints
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── wishlist.py     # Wishlist endpoints
│   │   │   ├── reviews.py      # Review endpoints
│   │   │   └── search.py       # Search endpoints
│   │   └── deps.py             # Dependencies and middleware
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── security.py         # JWT and password handling
│   │   ├── crud/               # CRUD operations
│   │   │   ├── __init__.py
│   │   │   ├── product.py      # Product CRUD
│   │   │   ├── user.py         # User CRUD
│   │   │   ├── review.py       # Review CRUD
│   │   │   └── wishlist.py     # Wishlist CRUD
│   │   └── utils.py            # Utility functions
│   └── tests/                  # Test suite
│       ├── __init__.py
│       ├── conftest.py         # Test configuration
│       ├── test_products.py    # Product tests
│       ├── test_auth.py        # Authentication tests
│       └── test_wishlist.py    # Wishlist tests
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

## 🗄️ **Database Design**

### **MongoDB Collections**

#### **1. Products Collection**
```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "price": "decimal",
  "originalPrice": "decimal",
  "discount": "decimal",
  "rating": "decimal",
  "reviewCount": "integer",
  "images": ["string"],
  "colors": [
    {
      "name": "string",
      "hex": "string",
      "image": "string"
    }
  ],
  "sizes": ["string"],
  "availableSizes": ["string"],
  "material": "string",
  "care": "string",
  "features": ["string"],
  "category": "string",
  "tags": ["string"],
  "isFeatured": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### **2. Users Collection**
```json
{
  "_id": "ObjectId",
  "email": "string",
  "name": "string",
  "hashedPassword": "string",
  "isActive": "boolean",
  "isAdmin": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### **3. Reviews Collection**
```json
{
  "_id": "ObjectId",
  "productId": "ObjectId",
  "userId": "ObjectId",
  "rating": "integer",
  "comment": "string",
  "userName": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

#### **4. Wishlist Collection**
```json
{
  "_id": "ObjectId",
  "userId": "ObjectId",
  "productId": "ObjectId",
  "addedAt": "datetime"
}
```

#### **5. Categories Collection**
```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "slug": "string",
  "createdAt": "datetime"
}
```

### **Database Indexes**
```javascript
// Products collection
db.products.createIndex({ "name": "text", "description": "text", "tags": "text" })
db.products.createIndex({ "category": 1 })
db.products.createIndex({ "material": 1 })
db.products.createIndex({ "price": 1 })
db.products.createIndex({ "rating": 1 })
db.products.createIndex({ "isFeatured": 1 })

// Users collection
db.users.createIndex({ "email": 1 }, { unique: true })

// Reviews collection
db.reviews.createIndex({ "productId": 1 })
db.reviews.createIndex({ "userId": 1 })

// Wishlist collection
db.wishlist.createIndex({ "userId": 1, "productId": 1 }, { unique: true })
```

## 🔌 **API Endpoints Design**

### **Base URL**: `/api/v1`

#### **Products Endpoints**
```
GET    /products              # Get products with pagination and filters
GET    /products/{id}         # Get product by ID
GET    /products/featured     # Get featured products
GET    /products/search       # Search products
GET    /products/related/{id} # Get related products
POST   /products              # Create product (Admin only)
PUT    /products/{id}         # Update product (Admin only)
DELETE /products/{id}         # Delete product (Admin only)
```

#### **Authentication Endpoints**
```
POST   /auth/register         # User registration
POST   /auth/login            # User login
POST   /auth/refresh          # Refresh JWT token
POST   /auth/logout           # User logout
GET    /auth/me               # Get current user profile
PUT    /auth/me               # Update user profile
```

#### **Wishlist Endpoints**
```
GET    /wishlist              # Get user's wishlist
POST   /wishlist              # Add product to wishlist
DELETE /wishlist/{productId}  # Remove product from wishlist
GET    /wishlist/check/{productId} # Check if product is in wishlist
```

#### **Reviews Endpoints**
```
GET    /products/{id}/reviews # Get product reviews
POST   /products/{id}/reviews # Add product review
PUT    /reviews/{id}          # Update review
DELETE /reviews/{id}          # Delete review
```

#### **Search & Analytics Endpoints**
```
GET    /search                # Global search
GET    /categories            # Get product categories
GET    /materials             # Get available materials
GET    /sizes                 # Get available sizes
GET    /colors                # Get available colors
GET    /stats/products        # Product statistics (Admin)
```

### **Query Parameters**

#### **Products Filtering**
```
page: int           # Page number (default: 1)
limit: int          # Items per page (default: 12, max: 50)
search: string      # Search query
category: string    # Filter by category
material: string    # Filter by material
size: string        # Filter by size
color: string       # Filter by color
price_min: float    # Minimum price
price_max: float    # Maximum price
sort: string        # Sort field (price, rating, date, name)
order: string       # Sort order (asc, desc)
featured: boolean   # Filter featured products
```

#### **Response Format**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "limit": 12,
      "total": 100,
      "pages": 9
    },
    "filters": {
      "applied": {...},
      "available": {...}
    }
  },
  "message": "Products retrieved successfully"
}
```

## 🔐 **Authentication & Security**

### **JWT Token Structure**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### **Token Payload**
```json
{
  "sub": "user_id",
  "email": "user_email",
  "is_admin": false,
  "exp": "expiration_timestamp",
  "iat": "issued_at_timestamp"
}
```

### **Security Features**
- Password hashing with bcrypt
- JWT token expiration (1 hour access, 7 days refresh)
- Rate limiting on authentication endpoints
- CORS configuration for frontend domain
- Input validation and sanitization
- SQL injection prevention (MongoDB native)
- XSS protection headers

## 📊 **Data Validation**

### **Pydantic Models**
```python
# Product validation
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    price: Decimal = Field(..., ge=0)
    originalPrice: Optional[Decimal] = Field(None, ge=0)
    discount: Optional[Decimal] = Field(None, ge=0, le=100)
    material: str = Field(..., min_length=1, max_length=100)
    category: str = Field(..., min_length=1, max_length=100)
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(..., min_items=1)
    colors: List[ColorCreate] = Field(..., min_items=1)
    sizes: List[str] = Field(..., min_items=1)

# User validation
class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)

# Review validation
class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=10, max_length=1000)
```

## 🚀 **Performance & Scalability**

### **Optimization Strategies**
1. **Database Indexing**: Strategic indexes on search and filter fields
2. **Connection Pooling**: MongoDB connection pooling with Motor
3. **Caching**: Redis caching for frequently accessed data
4. **Pagination**: Efficient pagination with skip/limit
5. **Aggregation**: MongoDB aggregation pipelines for complex queries
6. **Async Operations**: Non-blocking I/O operations

### **Expected Performance**
- Product listing: < 100ms
- Product search: < 150ms
- Product detail: < 50ms
- Wishlist operations: < 50ms
- Review operations: < 100ms

## 🧪 **Testing Strategy**

### **Test Coverage**
- Unit tests for all CRUD operations
- Integration tests for API endpoints
- Authentication and authorization tests
- Database operation tests
- Performance and load testing

### **Test Data**
- Mock product catalog (100+ products)
- Test user accounts
- Sample reviews and wishlists
- Edge case scenarios

## 🔧 **Environment Configuration**

### **Development Environment**
```env
# Database
MONGODB_URL=mongodb://localhost:27017/ecommerce_dev
DATABASE_NAME=ecommerce_dev

# JWT
JWT_SECRET=dev_secret_key_change_in_production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server
PORT=8000
HOST=0.0.0.0
DEBUG=true

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Security
SECRET_KEY=dev_secret_key_change_in_production
```

### **Production Environment**
```env
# Database
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/ecommerce
DATABASE_NAME=ecommerce_prod

# JWT
JWT_SECRET=production_secret_key_very_long_and_random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server
PORT=8000
HOST=0.0.0.0
DEBUG=false

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Security
SECRET_KEY=production_secret_key_very_long_and_random
```

## 📋 **Implementation Checklist**

### **Core Components**
- [ ] Project structure setup
- [ ] Install requirements from requirements.txt
- [ ] Setup .env file with environment variables
- [ ] FastAPI application configuration
- [ ] MongoDB connection setup
- [ ] Pydantic models for validation
- [ ] MongoDB schemas and indexes
- [ ] Basic CRUD operations

### **API Development**
- [ ] Product management endpoints
- [ ] User authentication system
- [ ] Wishlist management
- [ ] Review system
- [ ] Search functionality
- [ ] Basic middleware and CORS

### **Quality & Security**
- [ ] Frontend API integration
- [ ] Comprehensive testing
- [ ] Error handling and validation
- [ ] Security hardening
- [ ] Input validation and sanitization

### **Production Readiness**
- [ ] Performance optimization
- [ ] Environment configuration
- [ ] Monitoring and logging
- [ ] Documentation
- [ ] Final testing and validation

## 🎯 **Success Metrics**

### **Functional Requirements**
- ✅ All frontend features work with backend API
- ✅ Search and filtering perform efficiently
- ✅ Wishlist syncs between frontend and backend
- ✅ Product reviews are persistent
- ✅ User authentication works correctly

### **Performance Requirements**
- ✅ API response times under 200ms
- ✅ Support for 1000+ products
- ✅ Efficient search across product catalog
- ✅ Scalable architecture for future growth

### **Security Requirements**
- ✅ Secure user authentication
- ✅ Input validation and sanitization
- ✅ JWT token security
- ✅ Rate limiting on sensitive endpoints
- ✅ CORS configuration

---

**This design document provides a comprehensive blueprint for implementing a FastAPI + MongoDB backend that will seamlessly integrate with your existing React frontend. The architecture is designed for scalability, performance, and maintainability.**
