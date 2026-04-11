# Pay-Later Application - Folder Structure

## Project Root Structure

```
pay_later/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Configuration settings
│   │   │   ├── database.py           # MongoDB connection with Motor
│   │   │   ├── security.py           # JWT and security utilities
│   │   │   └── exceptions.py         # Custom exceptions
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User model
│   │   │   ├── credit_limit.py       # Credit limit model
│   │   │   ├── transaction.py        # Transaction model
│   │   │   └── merchant.py           # Merchant model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User Pydantic schemas
│   │   │   ├── credit_limit.py       # Credit limit schemas
│   │   │   ├── transaction.py        # Transaction schemas
│   │   │   ├── merchant.py           # Merchant schemas
│   │   │   └── common.py             # Common schemas
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # Dependencies
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py           # Authentication endpoints
│   │   │       ├── users.py          # User management endpoints
│   │   │       ├── credit_limits.py  # Credit limit endpoints
│   │   │       ├── transactions.py   # Transaction endpoints
│   │   │       ├── merchants.py      # Merchant endpoints
│   │   │       └── admin.py          # Admin endpoints
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Authentication logic
│   │   │   ├── user_service.py       # User management logic
│   │   │   ├── credit_service.py     # Credit assessment logic
│   │   │   ├── transaction_service.py # Transaction logic
│   │   │   └── merchant_service.py   # Merchant logic
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── validators.py         # Custom validators
│   │   │   ├── helpers.py            # Utility functions
│   │   │   ├── constants.py          # Application constants
│   │   │   └── enums.py              # Enum definitions
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py               # Authentication middleware
│   │       ├── cors.py               # CORS middleware
│   │       └── rate_limit.py         # Rate limiting middleware
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py               # Pytest configuration
│   │   ├── test_auth.py              # Authentication tests
│   │   ├── test_users.py             # User tests
│   │   ├── test_credit_limits.py     # Credit limit tests
│   │   ├── test_transactions.py      # Transaction tests
│   │   ├── test_merchants.py         # Merchant tests
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── test_data.py          # Test data fixtures
│   │       └── test_helpers.py       # Test helper functions
│   ├── requirements.txt              # Python dependencies
│   ├── requirements-dev.txt          # Development dependencies
│   ├── .env.example                  # Environment variables example
│   ├── .gitignore
│   └── README.md
├── frontend/                         # React Frontend
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   └── manifest.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Button.js
│   │   │   │   ├── Input.js
│   │   │   │   ├── Modal.js
│   │   │   │   ├── Loading.js
│   │   │   │   ├── Alert.js
│   │   │   │   └── Pagination.js
│   │   │   ├── layout/
│   │   │   │   ├── Header.js
│   │   │   │   ├── Sidebar.js
│   │   │   │   ├── Footer.js
│   │   │   │   └── Navigation.js
│   │   │   └── features/
│   │   │       ├── auth/
│   │   │       │   ├── LoginForm.js
│   │   │       │   ├── RegisterForm.js
│   │   │       │   └── ForgotPassword.js
│   │   │       ├── dashboard/
│   │   │       │   ├── Dashboard.js
│   │   │       │   ├── CreditLimitCard.js
│   │   │       │   └── TransactionSummary.js
│   │   │       ├── transactions/
│   │   │       │   ├── TransactionList.js
│   │   │       │   ├── TransactionDetail.js
│   │   │       │   └── TransactionForm.js
│   │   │       └── profile/
│   │   │           ├── Profile.js
│   │   │           └── ProfileForm.js
│   │   ├── pages/
│   │   │   ├── Login.js
│   │   │   ├── Register.js
│   │   │   ├── Dashboard.js
│   │   │   ├── Transactions.js
│   │   │   ├── Profile.js
│   │   │   ├── CreditLimits.js
│   │   │   └── Admin.js
│   │   ├── services/
│   │   │   ├── api.js                # API client
│   │   │   ├── auth.js               # Authentication service
│   │   │   ├── users.js              # User service
│   │   │   ├── transactions.js       # Transaction service
│   │   │   └── creditLimits.js       # Credit limit service
│   │   ├── store/
│   │   │   ├── index.js              # Store configuration
│   │   │   ├── authSlice.js          # Authentication state
│   │   │   ├── userSlice.js          # User state
│   │   │   ├── transactionSlice.js   # Transaction state
│   │   │   └── creditLimitSlice.js   # Credit limit state
│   │   ├── utils/
│   │   │   ├── constants.js          # Application constants
│   │   │   ├── helpers.js            # Utility functions
│   │   │   ├── validators.js         # Form validators
│   │   │   └── formatters.js         # Data formatters
│   │   ├── styles/
│   │   │   ├── index.css             # Global styles
│   │   │   ├── components.css        # Component styles
│   │   │   └── variables.css         # CSS variables
│   │   ├── App.js
│   │   ├── index.js
│   │   └── routes.js                 # Route definitions
│   ├── package.json
│   ├── package-lock.json
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   │   ├── endpoints.md
│   │   ├── authentication.md
│   │   └── examples.md
│   ├── database/                     # Database documentation
│   │   ├── schema.md
│   │   ├── collections.md
│   │   └── indexes.md
│   ├── deployment/                   # Deployment guides
│   │   ├── setup.md
│   │   ├── environment.md
│   │   └── troubleshooting.md
│   └── development/                  # Development guides
│       ├── setup.md
│       ├── coding-standards.md
│       └── testing.md
├── scripts/                          # Utility scripts
│   ├── setup.sh                      # Project setup script
│   ├── start-dev.sh                  # Development startup
│   ├── test.sh                       # Test runner
│   └── lint.sh                       # Linting script
├── .gitignore
├── README.md
├── docker-compose.yml                # Development environment
└── Makefile                          # Build automation
```

## Backend Structure Details

### Core Configuration (`backend/app/core/`)
- **config.py**: Environment variables, database settings, JWT configuration
- **database.py**: MongoDB connection setup with Motor
- **security.py**: JWT token handling, password hashing, security utilities
- **exceptions.py**: Custom exception classes

### Models (`backend/app/models/`)
- **user.py**: User document model with MongoDB fields
- **credit_limit.py**: Credit limit document model
- **transaction.py**: Transaction document model
- **merchant.py**: Merchant document model

### Schemas (`backend/app/schemas/`)
- **user.py**: Pydantic schemas for user data validation
- **credit_limit.py**: Credit limit validation schemas
- **transaction.py**: Transaction validation schemas
- **merchant.py**: Merchant validation schemas
- **common.py**: Shared schemas (pagination, responses, etc.)

### API Routes (`backend/app/api/v1/`)
- **auth.py**: Login, register, token refresh endpoints
- **users.py**: User CRUD operations
- **credit_limits.py**: Credit limit management
- **transactions.py**: Transaction operations
- **merchants.py**: Merchant management
- **admin.py**: Administrative functions

### Services (`backend/app/services/`)
- **auth_service.py**: Authentication business logic
- **user_service.py**: User management logic
- **credit_service.py**: Credit assessment algorithms
- **transaction_service.py**: Transaction processing
- **merchant_service.py**: Merchant operations

## Frontend Structure Details

### Components (`frontend/src/components/`)
- **common/**: Reusable UI components
- **layout/**: Layout components (header, sidebar, etc.)
- **features/**: Feature-specific components

### Pages (`frontend/src/pages/`)
- Main application pages with routing

### Services (`frontend/src/services/`)
- API communication layer
- Business logic services

### Store (`frontend/src/store/`)
- State management with Redux Toolkit
- Slice definitions for different features

## Key Files Description

### Backend Key Files
- **main.py**: FastAPI application initialization
- **requirements.txt**: Python dependencies
- **conftest.py**: Pytest configuration and fixtures

### Frontend Key Files
- **App.js**: Main application component
- **routes.js**: Route definitions
- **api.js**: Centralized API client
- **package.json**: Node.js dependencies

### Configuration Files
- **.env.example**: Environment variables template
- **docker-compose.yml**: Development environment setup
- **Makefile**: Build and development commands

This folder structure provides a clean separation of concerns, follows best practices for both FastAPI and React applications, and ensures scalability and maintainability of the codebase.
