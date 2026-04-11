# E-Commerce Backend API

A comprehensive, scalable e-commerce backend API built with FastAPI, MongoDB, and modern Python practices.

## 🚀 Features

- **FastAPI Framework**: High-performance, modern Python web framework
- **MongoDB Integration**: NoSQL database with Motor async driver
- **JWT Authentication**: Secure user authentication and authorization
- **Comprehensive API**: Products, users, reviews, wishlists, search, and categories
- **Dynamic Category Management**: Hierarchical categories and subcategories
- **Input Validation**: Pydantic models for data validation
- **Async Operations**: Non-blocking I/O for better performance
- **Auto-generated Docs**: OpenAPI/Swagger documentation
- **Testing Suite**: Comprehensive test coverage with pytest
- **Production Ready**: CORS, security middleware, and error handling

## 🏗️ Architecture

```
ecommerce-backend/
├── app/
│   ├── config/          # Configuration management
│   ├── models/          # Pydantic data models
│   ├── schemas/         # MongoDB schemas
│   ├── api/             # API routes and endpoints
│   │   └── v1/          # API version 1
│   ├── core/            # Core functionality
│   │   ├── security/    # JWT and authentication
│   │   ├── crud/        # Database operations
│   │   └── utils/       # Utility functions
│   └── tests/           # Test suite
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

## 📋 Prerequisites

- Python 3.8+
- MongoDB 4.4+
- pip (Python package manager)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB**
   ```bash
   # Make sure MongoDB is running on your system
   # Default: mongodb://localhost:27017
   ```

## ⚙️ Configuration

Edit the `.env` file with your settings:

```env
# Database Configuration
MONGODB_URL=mongodb://localhost:27017/ecommerce_dev
DATABASE_NAME=ecommerce_dev

# JWT Configuration
JWT_SECRET=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=true

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Security
SECRET_KEY=your_secret_key_here
```

## 🚀 Running the Application

### Development Mode
```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the built-in runner
python -m app.main
```

### 🏷️ Quick Start with Categories

1. **Start the server**:
   ```bash
   python -m app.main
   ```

2. **Create your first category**:
   ```bash
   # Login as admin first to get token
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "admin123"}'
   
   # Create a category
   curl -X POST "http://localhost:8000/api/v1/categories/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"name": "Saree", "slug": "saree", "description": "Traditional Indian sarees"}'
   ```

3. **View categories**:
   ```bash
   curl "http://localhost:8000/api/v1/categories/"
   ```

4. **Run the demo**:
   ```bash
   python demo_categories.py
   ```

### Production Mode
```bash
# Run without reload
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🔌 API Endpoints

### Base URL: `/api/v1`

#### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh JWT token
- `GET /auth/me` - Get current user profile
- `PUT /auth/me` - Update user profile
- `PUT /auth/me/password` - Update password
- `POST /auth/logout` - User logout

#### Products
- `GET /products` - Get products with filters and pagination
- `GET /products/{id}` - Get product by ID
- `GET /products/featured` - Get featured products
- `GET /products/related/{id}` - Get related products
- `POST /products` - Create product (Admin only)
- `PUT /products/{id}` - Update product (Admin only)
- `DELETE /products/{id}` - Delete product (Admin only)
- `GET /products/categories` - Get product categories
- `GET /products/materials` - Get product materials
- `GET /products/sizes` - Get product sizes
- `GET /products/colors` - Get product colors

#### Wishlist
- `GET /wishlist` - Get user's wishlist
- `POST /wishlist` - Add product to wishlist
- `DELETE /wishlist/{productId}` - Remove product from wishlist
- `GET /wishlist/check/{productId}` - Check if product is in wishlist
- `GET /wishlist/count` - Get wishlist count
- `DELETE /wishlist` - Clear entire wishlist

#### Reviews
- `GET /reviews/products/{productId}` - Get product reviews
- `POST /reviews/products/{productId}` - Create product review
- `GET /reviews/user` - Get user's reviews
- `PUT /reviews/{id}` - Update review
- `DELETE /reviews/{id}` - Delete review

#### Search
- `GET /search` - Global search
- `GET /search/suggestions` - Search suggestions
- `GET /search/trending` - Trending searches
- `GET /search/filters` - Available search filters

#### Categories
- `POST /categories` - Create category (Admin only)
- `GET /categories` - Get all categories with filtering
- `GET /categories/{id}` - Get category by ID
- `GET /categories/slug/{slug}` - Get category by slug
- `PUT /categories/{id}` - Update category (Admin only)
- `DELETE /categories/{id}` - Delete category (Admin only)
- `POST /categories/{id}/subcategories` - Create subcategory (Admin only)
- `GET /categories/{id}/subcategories` - Get subcategories for a category
- `GET /categories/{id}/with-subcategories` - Get category with subcategories

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register/Login** to get access and refresh tokens
2. **Include token** in Authorization header: `Bearer <token>`
3. **Refresh token** when access token expires

### Example Usage
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Use token
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <your_access_token>"
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest app/tests/test_main.py

# Run category tests
pytest app/tests/test_categories.py
```

### 🏷️ Testing the Category System

The category management system includes comprehensive tests:

```bash
# Test category creation and management
pytest app/tests/test_categories.py -v

# Test with coverage
pytest app/tests/test_categories.py --cov=app.core.crud.category --cov=app.api.v1.categories
```

### 🚀 Demo Script

Test the category system interactively:

```bash
# Run the demo script (requires server to be running)
python demo_categories.py
```

The demo script will:
- Create sample categories (Saree, Kurta, Jeans)
- Create subcategories under each category
- Demonstrate API endpoints
- Show the complete workflow

## 📊 Database Schema

### Products Collection
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
  "colors": [{"name": "string", "hex": "string", "image": "string"}],
  "sizes": ["string"],
  "material": "string",
  "category": "string",
  "subcategory": "string",
  "tags": ["string"],
  "isFeatured": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Categories Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "slug": "string",
  "description": "string",
  "image": "string",
  "icon": "string",
  "isActive": "boolean",
  "isFeatured": "boolean",
  "sortOrder": "integer",
  "productCount": "integer",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Subcategories Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "slug": "string",
  "description": "string",
  "categoryId": "ObjectId",
  "isActive": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Users Collection
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

## 🚀 Performance Features

- **Database Indexing**: Strategic indexes on search, filter, and category fields
- **Connection Pooling**: MongoDB connection pooling with Motor
- **Async Operations**: Non-blocking I/O operations
- **Pagination**: Efficient pagination with skip/limit
- **Aggregation**: MongoDB aggregation pipelines for complex queries
- **Category Optimization**: Automatic product counting and efficient category queries

## 🔒 Security Features

- **Password Hashing**: bcrypt for secure password storage
- **JWT Security**: Token expiration and refresh mechanism
- **Input Validation**: Pydantic models for data validation
- **CORS Configuration**: Configurable cross-origin resource sharing
- **Rate Limiting**: Built-in rate limiting capabilities
- **XSS Protection**: Security headers and input sanitization

## 🐳 Docker Support

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t ecommerce-backend .
docker run -p 8000:8000 ecommerce-backend
```

## 📈 Monitoring and Logging

The application includes:
- **Structured Logging**: JSON-formatted logs
- **Request Timing**: X-Process-Time headers
- **Health Checks**: `/health` endpoint
- **Error Handling**: Global exception handler
- **Performance Metrics**: Built-in timing middleware

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## 🏷️ Category Management System

The e-commerce backend now includes a comprehensive **Dynamic Category Management System** that allows admins to create, manage, and organize products through hierarchical categories and subcategories.

### ✨ Key Features

- **🔄 Dynamic Categories**: Create new categories anytime without code changes
- **🏗️ Hierarchical Structure**: Categories → Subcategories → Products
- **📊 Automatic Counting**: Product counts update automatically per category
- **🔍 Enhanced Filtering**: Filter products by category and subcategory
- **🎨 Rich Metadata**: Support for images, icons, and custom ordering
- **🔒 Admin Control**: Only admins can modify categories for data integrity
- **🚀 SEO-Friendly**: Slug-based routing for better URLs

### 📋 Category Structure Example

```
Saree (Category)
├── Cotton Saree (Subcategory)
├── Silk Saree (Subcategory)
└── Party Wear Saree (Subcategory)

Kurta (Category)
├── Men's Kurta (Subcategory)
├── Women's Kurta (Subcategory)
└── Kids Kurta (Subcategory)

Jeans (Category)
├── Skinny Jeans (Subcategory)
├── Regular Fit (Subcategory)
└── High Waist (Subcategory)
```

### 🚀 Usage Examples

#### Create a Category
```bash
curl -X POST "http://localhost:8000/api/v1/categories/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "Saree",
    "slug": "saree",
    "description": "Traditional Indian sarees for all occasions",
    "image": "https://example.com/saree-category.jpg",
    "icon": "saree-icon",
    "isActive": true,
    "isFeatured": true,
    "sortOrder": 1
  }'
```

#### Create a Subcategory
```bash
curl -X POST "http://localhost:8000/api/v1/categories/{category_id}/subcategories" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "Cotton Saree",
    "slug": "cotton-saree",
    "description": "Pure cotton sarees for daily wear"
  }'
```

#### Get Categories with Subcategories
```bash
curl "http://localhost:8000/api/v1/categories/slug/saree/with-subcategories"
```

#### Create Product with Category
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "Cotton Saree",
    "description": "Beautiful cotton saree",
    "price": 1500.00,
    "material": "Cotton",
    "category": "saree",
    "subcategory": "cotton-saree",
    "images": ["https://example.com/saree1.jpg"],
    "colors": [{"name": "Blue", "hex": "#0000FF", "image": "blue.jpg"}],
    "sizes": ["Free Size"]
  }'
```

### 🔧 Technical Implementation

- **Models**: Pydantic models for validation and serialization
- **CRUD Operations**: Full CRUD operations for categories and subcategories
- **Database Indexes**: Optimized MongoDB indexes for performance
- **Product Integration**: Automatic category product counting
- **API Endpoints**: RESTful API with proper error handling
- **Testing**: Comprehensive test suite for category management

### 📱 Frontend Integration

Categories are designed to work seamlessly with frontend applications:

- **Dynamic Navigation**: Categories automatically appear in navigation menus
- **Product Filtering**: Filter products by category and subcategory
- **SEO Optimization**: Slug-based URLs for better search engine optimization
- **Rich Display**: Support for category images and icons
- **Responsive Design**: Categories adapt to different screen sizes

## 🔮 Future Enhancements

- [x] **Dynamic Category Management** ✅
- [x] **Subcategory Support** ✅
- [x] **Product-Category Integration** ✅
- [ ] Redis caching for performance
- [ ] Elasticsearch for advanced search
- [ ] Image upload and storage
- [ ] Payment gateway integration
- [ ] Order management system
- [ ] Analytics and reporting
- [ ] Multi-language support
- [ ] Webhook system
- [ ] Rate limiting middleware
- [ ] API versioning strategy

---

**Built with ❤️ using FastAPI and MongoDB**
