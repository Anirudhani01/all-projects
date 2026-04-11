# LazyPay API Test Suite

This directory contains comprehensive test cases for all LazyPay API endpoints, organized by module.

## 📁 Test Structure

```
app/tests/
├── test_user/                    # User module tests
│   ├── __init__.py
│   └── test_user_endpoints.py   # All user endpoint tests
├── test_merchants/              # Merchant module tests
│   ├── __init__.py
│   └── test_merchant_endpoints.py # All merchant endpoint tests
├── test_transactions/           # Transaction module tests
│   ├── __init__.py
│   └── test_transaction_endpoints.py # All transaction endpoint tests
└── README.md                    # This file
```

## 🧪 Test Coverage

### User Module Tests (`test_user/`)
- **POST** `/api/v1/users/` - Create user
- **GET** `/api/v1/users/{user_id}` - Get user profile
- **GET** `/api/v1/users/{user_id}/dues` - Get user dues
- **GET** `/api/v1/users/` - Get users by limit status

### Merchant Module Tests (`test_merchants/`)
- **POST** `/api/v1/merchants/` - Create merchant
- **GET** `/api/v1/merchants/` - Get all merchants
- **GET** `/api/v1/merchants/{merchant_id}` - Get merchant details
- **PATCH** `/api/v1/merchants/{merchant_id}/fee` - Update merchant fee
- **GET** `/api/v1/merchants/{merchant_id}/fee-history` - Get merchant fee history

### Transaction Module Tests (`test_transactions/`)
- **POST** `/api/v1/transactions/purchase` - Process purchase
- **POST** `/api/v1/transactions/payment` - Process payment
- **GET** `/api/v1/transactions/{transaction_id}` - Get transaction by ID
- **GET** `/api/v1/transactions/` - Get transactions with filters
- **GET** `/api/v1/transactions/summary` - Get transaction summary

## 🚀 Running Tests

### Prerequisites
Make sure you have the required dependencies installed:
```bash
pip install pytest pytest-asyncio httpx
```

### Running All Tests
```bash
# From the project root directory
python run_all_tests.py
```

### Running Specific Module Tests
```bash
# Run only user tests
python run_all_tests.py users

# Run only merchant tests
python run_all_tests.py merchants

# Run only transaction tests
python run_all_tests.py transactions
```

### Running by Test Type
```bash
# Run only unit tests (mocked)
python run_all_tests.py unit

# Run only integration tests (with real database)
python run_all_tests.py integration

# Run all tests
python run_all_tests.py all
```

### Running Individual Test Files
```bash
# Run user tests directly
pytest app/tests/test_user/ -v

# Run merchant tests directly
pytest app/tests/test_merchants/ -v

# Run transaction tests directly
pytest app/tests/test_transactions/ -v
```

## 📋 Test Categories

### Unit Tests
- Use mocked services and dependencies
- Test individual endpoint functionality
- Fast execution, no database dependency
- Test validation, error handling, and business logic

### Integration Tests
- Use real database connections
- Test end-to-end functionality
- Require running application and MongoDB
- Test actual data persistence and retrieval

## 🎯 Test Features

### Comprehensive Coverage
- ✅ **Success scenarios** - Normal operation
- ✅ **Error scenarios** - Invalid inputs, missing data
- ✅ **Edge cases** - Boundary conditions
- ✅ **Validation** - Input validation and error responses
- ✅ **Business logic** - Service layer functionality

### Test Data
- Sample request/response fixtures
- Realistic test data structures
- Proper validation of response schemas
- Mock service responses

### Error Handling
- HTTP status code validation
- Error message verification
- Exception handling scenarios
- Service error propagation

## 🔧 Test Configuration

### Environment Setup
Tests use the same environment variables as the main application:
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB` - Database name
- `APP_ENV` - Application environment

### Test Database
Integration tests use the same MongoDB instance as the main application.
Make sure MongoDB is running before running integration tests.

## 📊 Test Reports

### Verbose Output
Tests run with verbose output (`-v`) to show detailed test results.

### Color Output
Tests use colored output (`--color=yes`) for better readability.

### Traceback Style
Tests use short tracebacks (`--tb=short`) for concise error reporting.

## 🐛 Debugging Tests

### Running Single Test
```bash
# Run a specific test method
pytest app/tests/test_user/test_user_endpoints.py::TestUserEndpoints::test_create_user_success -v

# Run tests matching a pattern
pytest -k "create_user" -v
```

### Debug Mode
```bash
# Run with debug output
pytest -v --tb=long --capture=no
```

### Coverage Report
```bash
# Install coverage
pip install pytest-cov

# Run with coverage
pytest --cov=app --cov-report=html
```

## 📝 Adding New Tests

### Test File Structure
1. Create test file in appropriate module directory
2. Follow naming convention: `test_<module>_endpoints.py`
3. Use descriptive test method names
4. Include both unit and integration test classes

### Test Method Naming
```python
def test_<endpoint>_<scenario>_<expected_result>(self):
    """Test description."""
    # Arrange
    # Act
    # Assert
```

### Fixtures
- Use `@pytest.fixture` for reusable test data
- Create sample request/response data
- Mock service dependencies for unit tests

### Assertions
- Verify HTTP status codes
- Validate response data structure
- Check service method calls
- Test error conditions

## 🎉 Success Criteria

Tests are considered successful when:
- ✅ All unit tests pass
- ✅ All integration tests pass (with running application)
- ✅ No test warnings or deprecation notices
- ✅ Proper error handling coverage
- ✅ All endpoints have test coverage

## 📞 Support

If you encounter issues with tests:
1. Check that MongoDB is running
2. Verify all dependencies are installed
3. Ensure the application is properly configured
4. Check test environment variables
5. Review test logs for specific error messages
