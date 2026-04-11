# LazyPay - Modular monolithic FastAPI + MongoDB (Pay-Later)

A modular monolithic FastAPI application for a pay-later service using MongoDB.

## Features

- **User Management**: Onboard users with credit limits and track outstanding balances
- **User Bank System**: Every user gets a default ₹2000 bank balance for repayments
- **Merchant Management**: Onboard merchants with configurable fee percentages
- **Transaction Processing**: Handle purchases and payments with idempotency
- **Wallet System**: Users can add money to merchant wallets from their credit limit
- **Repayment System**: Users can repay outstanding amounts from their bank balance
- **Reporting**: Generate reports on fees, dues, and user limits
- **Authentication**: JWT-based authentication with 3-min access tokens and 5-min refresh tokens
- **Role-Based Access Control (RBAC)**: Comprehensive permission system with admin, merchant, and user roles
- **Structured Logging**: Comprehensive logging with structlog
- **Error Handling**: Proper exception mapping to HTTP status codes
- **Validation**: Input validation with Pydantic schemas
- **Database**: MongoDB with Motor for async operations

## Authentication & Authorization

### JWT Authentication
- **Access Tokens**: 3-minute expiration for API access
- **Refresh Tokens**: 5-minute expiration for token renewal
- **Token Blacklisting**: Secure logout with token invalidation
- **Password Security**: bcrypt hashing with salt
- **User Registration**: Email, name, password, and role assignment

### RBAC (Role-Based Access Control)
The application implements a comprehensive RBAC system with the following components:

#### **Roles**
- **Admin**: Full system access with all permissions
- **Merchant**: Can manage transactions and view reports
- **User**: Can view own data, make purchases, and repayments

#### **Permissions**
- **Users**: `users:read`, `users:write`, `users:delete`
- **Transactions**: `transactions:read`, `transactions:write`, `transactions:approve`
- **Reports**: `reports:read`, `reports:export`
- **Merchants**: `merchants:read`, `merchants:write`
- **System**: `system:admin` (full access)

#### **RBAC Features**
- **Permission-Based Dependencies**: FastAPI middleware for endpoint protection
- **Role Assignment**: Dynamic role assignment to users
- **Permission Checking**: Real-time permission validation
- **Audit Logging**: Comprehensive logging of all RBAC operations
- **API Management**: Complete CRUD operations for roles and permissions

### User Bank System
The application implements a comprehensive User Bank System for managing user finances:

#### **Key Features**
- **Default Bank Balance**: Every new user gets ₹2000 in their bank account
- **Credit Limit**: Fixed ₹2000 credit limit for all users
- **Available Credit**: Calculated as `credit_limit - outstanding_amount`
- **Outstanding Amount**: Includes merchant purchases + percentage fees
- **Repayment System**: Users can repay outstanding amounts from their bank balance

#### **Financial Flow**
1. **User Registration**: User gets ₹2000 bank balance + ₹2000 credit limit
2. **Merchant Purchase**: User adds money to merchant wallet from credit limit
3. **Outstanding Calculation**: Outstanding amount = purchase amount + merchant fee
4. **Repayment**: User repays from bank balance, reducing outstanding amount
5. **Credit Recovery**: Available credit increases as outstanding amount decreases

#### **Example Flow**
```
User starts with: Bank ₹2000, Credit ₹2000, Outstanding ₹0
User adds ₹500 to merchant (10% fee): Bank ₹2000, Credit ₹1500, Outstanding ₹550
User repays ₹200: Bank ₹1800, Credit ₹1500, Outstanding ₹350
```

### Default Users
The system comes with pre-configured users for testing:
- **John** (admin@admin.com) - Admin role with full access
- **Alice** (alice@merchant.com) - Merchant role
- **Bob** (bob@user.com) - User role
- **Nani** (nani@gmail.com) - User role with test data

## Setup

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud instance)
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pay_later_cursor
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   Create a `.env` file with the following variables:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=lazypay
   APP_ENV=local
   PORT=8000
   LOG_LEVEL=INFO
   
   # JWT Configuration
   JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=3
   REFRESH_TOKEN_EXPIRE_MINUTES=5
   ```

5. **Start MongoDB**
   Ensure MongoDB is running on your system or use a cloud instance.

6. **Run the application**
   ```bash
   ./scripts/dev.sh
   # Or directly: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Initialize RBAC System**
   The RBAC system is automatically initialized on application startup, creating:
   - Default roles (admin, merchant, user)
   - Default permissions for all resources
   - Default users for testing

## API Documentation

Once the application is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and blacklist token
- `POST /api/v1/auth/change-password` - Change user password
- `GET /api/v1/auth/profile` - Get user profile
- `GET /api/v1/auth/me` - Get current user info

### User Bank & Repayment Endpoints
- `POST /api/v1/users/{user_id}/repay` - Repay outstanding amount from bank balance
- `POST /api/v1/users/{user_id}/deposit` - Deposit money to user bank account
- `GET /api/v1/users/{user_id}/balance` - Get user balance information
- `GET /api/v1/users/{user_id}/merchant-usage` - Get user's merchant usage breakdown

### Wallet Endpoints
- `POST /api/v1/wallet/add-to-merchant` - Add money to merchant wallet from credit
- `GET /api/v1/wallet/user-credit/{user_id}` - Get user credit information
- `GET /api/v1/wallet/transactions` - Get wallet transactions
- `GET /api/v1/wallet/merchant-usage` - Get user's merchant wallet usage

### RBAC Management Endpoints
- `GET /api/v1/rbac/roles` - Get all roles (admin only)
- `POST /api/v1/rbac/roles` - Create new role (admin only)
- `GET /api/v1/rbac/roles/{role_id}` - Get role by ID (admin only)
- `PUT /api/v1/rbac/roles/{role_id}` - Update role (admin only)
- `DELETE /api/v1/rbac/roles/{role_id}` - Delete role (system admin only)
- `GET /api/v1/rbac/permissions` - Get all permissions (admin only)
- `POST /api/v1/rbac/permissions` - Create new permission (system admin only)
- `POST /api/v1/rbac/user-roles` - Assign role to user (admin only)
- `GET /api/v1/rbac/user-roles/{user_id}` - Get user roles (admin only)
- `DELETE /api/v1/rbac/user-roles/{user_id}/{role_id}` - Remove role from user (admin only)
- `GET /api/v1/rbac/users/{user_id}/permissions` - Get user permissions (admin only)
- `POST /api/v1/rbac/users/{user_id}/check-permission` - Check user permission (admin only)

## Project Structure

```
app/
├── api/                    # FastAPI routers and dependencies
│   ├── routers/           # API endpoint routers
│   │   ├── users.py       # User endpoints (RBAC protected)
│   │   ├── merchants.py   # Merchant endpoints (RBAC protected)
│   │   ├── transactions.py # Transaction endpoints (RBAC protected)
│   │   ├── reports.py     # Report endpoints (RBAC protected)
│   │   ├── auth.py        # Authentication endpoints
│   │   └── rbac.py        # RBAC management endpoints
│   ├── dependencies.py    # Dependency injection
│   └── error_handlers.py  # Exception handling
├── auth/                  # Authentication module
│   ├── models.py          # Auth data models
│   ├── schemas.py         # Auth API schemas
│   ├── jwt_handler.py     # JWT token management
│   ├── repository.py      # Auth database operations
│   ├── service.py         # Auth business logic
│   ├── dependencies.py    # Auth FastAPI dependencies
│   └── __init__.py        # Auth module exports
├── rbac/                  # Role-Based Access Control module
│   ├── models.py          # RBAC data models
│   ├── repository.py      # RBAC database operations
│   ├── service.py         # RBAC business logic
│   ├── initializer.py     # RBAC system initialization
│   ├── middleware.py      # Permission checking dependencies
│   └── __init__.py        # RBAC module exports
├── config/                # Application settings
│   └── settings.py        # Environment configuration
├── db/                   # Database client and session management
│   └── mongo.py          # MongoDB connection and indexes
├── modules/              # Business logic modules
│   ├── users/            # User management
│   │   ├── models.py     # User data models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── repository.py # Data access layer
│   │   └── service.py    # Business logic
│   ├── merchants/        # Merchant management
│   │   ├── models.py     # Merchant data models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── repository.py # Data access layer
│   │   └── service.py    # Business logic
│   ├── transactions/     # Transaction processing
│   │   ├── models.py     # Transaction data models
│   │   ├── schemas.py    # Pydantic schemas
│   │   ├── repository.py # Data access layer
│   │   └── service.py    # Business logic
│   └── reports/          # Reporting system
│       ├── models.py     # Report data models
│       ├── schemas.py    # Report API schemas
│       ├── repository.py # Report data access
│       └── service.py    # Report business logic
├── tests/                # Test suite
│   ├── test_user/        # User module tests
│   ├── test_merchants/   # Merchant module tests
│   └── test_transactions/ # Transaction module tests
└── common/               # Shared utilities
    ├── exceptions.py     # Custom exceptions
    ├── logging.py        # Logging configuration
    └── types.py          # Common type definitions
```

## Testing

### Authentication Testing
```bash
# Test authentication system
python test_auth.py

# Test RBAC integration
python test_rbac_integration.py
```

### RBAC Testing
The RBAC system includes comprehensive testing:
- **Phase 1**: Foundation testing (models, repository, service)
- **Phase 2**: Middleware testing (permission checking)
- **Phase 3**: API endpoint testing (RBAC management)
- **Phase 4**: Integration testing (with main application)

### Test Structure
```
test_rbac/
├── test_rbac_phase1.py   # Foundation testing
├── test_rbac_phase2.py   # Middleware testing
└── test_rbac_phase3.py   # API endpoint testing
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DB` | Database name | `lazypay` |
| `APP_ENV` | Environment | `local` |
| `PORT` | Application port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `IDEMPOTENCY_TTL_HOURS` | Idempotency key TTL | `24` |
| `JWT_SECRET_KEY` | JWT signing secret | `your-super-secret-jwt-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | `3` |
| `REFRESH_TOKEN_EXPIRE_MINUTES` | Refresh token expiration | `5` |

## Database Indexes

The application automatically creates the following indexes:
- `users.email` (unique)
- `users.status`
- `user_balances.user_id` (unique)
- `user_balances.outstanding_amount`
- `merchants.name` (unique)
- `merchant_fee_history.(merchant_id, effective_from)`
- `transactions.(user_id, created_at)`
- `transactions.(merchant_id, created_at)`
- `transactions.(user_id, idempotency_key)` (unique, sparse)
- `idempotency_keys.(scope, key)` (unique)
- `idempotency_keys.ttl_expires_at` (TTL)

### RBAC Indexes
- `roles.name` (unique)
- `roles.is_active`
- `permissions.name` (unique)
- `permissions.resource`
- `permissions.is_active`
- `user_roles.(user_id, role_id)` (unique)
- `user_roles.user_id`
- `user_roles.role_id`
- `user_roles.is_active`
- `user_roles.expires_at`

### Authentication Indexes
- `auth_users.email` (unique)
- `auth_users.is_active`
- `token_blacklist.token_id` (unique)
- `token_blacklist.expires_at` (TTL)

## Security Features

### Authentication Security
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: Short-lived tokens for security
- **Token Blacklisting**: Secure logout mechanism
- **Password Hashing**: bcrypt with salt for password security
- **Input Validation**: Comprehensive request validation

### Authorization Security
- **Role-Based Access**: Granular role assignments
- **Permission-Based Control**: Fine-grained permission system
- **Middleware Protection**: All endpoints protected by RBAC
- **Audit Logging**: Complete audit trail for all operations
- **Error Handling**: Secure error messages without data exposure

## Frontend Integration

### React Frontend (`pay_later_frontend/`)
The application includes a React-based frontend for user interaction:

#### **Features**
- **Role-Based Navigation**: Different dashboards for admin, merchant, and user roles
- **Enhanced Error Handling**: Comprehensive error logging and visual error display
- **Real-Time Data**: Live updates from backend API endpoints
- **Responsive Design**: Modern UI with mobile-friendly layout

#### **Pages**
- **Admin Dashboard**: Overview of system metrics (users, merchants, transactions, dues)
- **Users Management**: View and manage all users in the system
- **Merchants Management**: Create, view, and update merchant information
- **Transactions Management**: Process purchases and payments
- **User Dashboard**: Personal user profile and transaction history
- **Merchant Dashboard**: Merchant profile, earnings, and transaction history

#### **Error Handling Improvements**
All admin pages now include enhanced error handling:
- **Console Logging**: Detailed API call logging for debugging
- **Visual Error Display**: Red error boxes for API failures
- **Response Format Handling**: Robust handling of different API response formats
- **Loading States**: Proper loading indicators during API calls

#### **API Integration**
- **Authentication**: JWT token management with automatic refresh
- **Role-Based Access**: Different API endpoints based on user role
- **Real-Time Updates**: Automatic data refresh and error recovery
- **Consistent Error Handling**: Uniform error display across all pages

### Frontend Setup
```bash
# Navigate to frontend directory
cd pay_later_frontend

# Install dependencies
npm install

# Start development server
npm start
```

The frontend will be available at `http://localhost:3000`

## Recent Improvements

### Frontend Error Handling (August 2025)
- **Enhanced Users Page**: Added comprehensive error logging and visual error display
- **Enhanced Merchants Page**: Applied consistent error handling and logging
- **Enhanced Transactions Page**: Implemented robust error handling and response format handling
- **Console Logging**: Added detailed API call logging (`🔍 Fetching...`, `✅ API response:`, `❌ Failed to fetch:`)
- **Visual Error Display**: Red error boxes showing specific API error messages
- **Response Format Handling**: Robust handling of different API response structures

### RBAC System Fixes (August 2025)
- **Admin Role Creation**: Fixed missing admin role causing 403 Forbidden errors
- **Pydantic Validation**: Resolved ObjectId to string conversion issues
- **Route Ordering**: Fixed FastAPI route conflicts for `/me` endpoints
- **Frontend Routing**: Resolved route conflicts between admin and merchant pages
- **JavaScript Error Handling**: Added null checks for undefined data in frontend

## Next Steps

The following features are planned for future implementation:
- **Advanced RBAC**: Hierarchical roles and dynamic permissions
- **API Rate Limiting**: Request throttling and abuse prevention
- **Monitoring**: Metrics, observability, and alerting
- **Performance Optimization**: Caching and query optimization
- **Deployment**: Docker containerization and CI/CD pipeline
