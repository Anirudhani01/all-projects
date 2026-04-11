# Testing Documentation

This directory contains all test files for the e-commerce backend application.

## 📁 Test File Structure

```
app/tests/
├── __init__.py                    # Makes this a Python package
├── conftest.py                    # Test configuration and fixtures
├── test_auth_simple.py            # Authentication validation tests (422 errors)
├── test_auth.py                   # Comprehensive authentication tests with mocking
├── demo_422_error.py              # Interactive demonstration of 422 errors
├── test_main.py                   # Basic application tests
└── README.md                      # This documentation file
```

## 🧪 Test Files Overview

### **1. `test_auth_simple.py`** - Main Validation Test Suite
- **Purpose**: Tests for 422 validation errors and data structure validation
- **Coverage**: 9 tests covering all validation scenarios
- **Status**: ✅ All tests passing
- **Usage**: `python -m pytest app/tests/test_auth_simple.py -v`

### **2. `test_auth.py`** - Comprehensive Authentication Tests
- **Purpose**: Full authentication flow testing with mocked database operations
- **Coverage**: Registration, login, error handling, and integration tests
- **Status**: ⚠️ Some tests need mocking fixes for Python 3.7 compatibility
- **Usage**: `python -m pytest app/tests/test_auth.py -v`

### **3. `demo_422_error.py`** - Interactive Demonstration
- **Purpose**: Demonstrates the exact 422 error scenarios and solutions
- **Coverage**: Real API calls to show validation behavior
- **Status**: ✅ Ready to use
- **Usage**: `python app/tests/demo_422_error.py`

### **4. `conftest.py`** - Test Configuration
- **Purpose**: Shared test fixtures and configuration
- **Features**: Mock database, sample data, JWT tokens
- **Status**: ✅ Configured for Python 3.7 compatibility

## 🚀 How to Run Tests

### **Run All Validation Tests:**
```bash
python -m pytest app/tests/test_auth_simple.py -v
```

### **Run Specific Test:**
```bash
python -m pytest app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_validation_error_wrong_field -v
```

### **Run Comprehensive Tests:**
```bash
python -m pytest app/tests/test_auth.py -v
```

### **Run Demo Script:**
```bash
python app/tests/demo_422_error.py
```

## 🔍 Test Categories

### **Validation Error Tests (422 Errors)**
1. **Wrong Field Name**: `mail` instead of `email`
2. **Short Password**: Less than 8 characters
3. **Invalid Email**: Malformed email format
4. **Short Name**: Less than 2 characters
5. **Missing Fields**: Required fields not provided

### **Login Validation Tests**
1. **Missing Password**: Only email provided
2. **Missing Email**: Only password provided

### **Valid Data Structure Tests**
1. **Valid Registration Data**: Correct format passes validation
2. **Valid Login Data**: Correct format passes validation

## 📊 Test Results

All validation tests are currently passing:

```
================================= test session starts ==================================
platform win32 -- Python 3.7.0, pytest-7.4.3, pluggy-1.2.0

app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_validation_error_wrong_field PASSED [ 11%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_validation_error_short_password PASSED [ 22%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_validation_error_invalid_email PASSED [ 33%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_validation_error_short_name PASSED [ 44%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_validation_error_missing_fields PASSED [ 55%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_login_user_validation_error_missing_password PASSED [ 66%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_login_user_validation_error_missing_email PASSED [ 77%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_register_user_valid_data_structure PASSED [ 88%]
app/tests/test_auth_simple.py::TestAuthenticationValidation::test_login_user_valid_data_structure PASSED [100%]

======================== 9 passed, 1 warning ========================
```

## 🔧 Test Configuration

### **Dependencies Required:**
- `pytest` - Testing framework
- `fastapi[testing]` - FastAPI test client
- `requests` - For demo script API calls

### **Environment Setup:**
- FastAPI server should be running (use `python start_dev.py`)
- MongoDB connection (optional for validation tests)
- Python 3.7+ compatibility maintained

## 📝 Adding New Tests

### **For New Validation Tests:**
1. Add test methods to `TestAuthenticationValidation` class in `test_auth_simple.py`
2. Follow naming convention: `test_[scenario]_[expected_result]`
3. Use descriptive docstrings explaining the test purpose

### **For New Integration Tests:**
1. Add test methods to `TestAuthentication` class in `test_auth.py`
2. Use proper mocking for database operations
3. Test both success and failure scenarios

### **Test Naming Convention:**
- `test_[feature]_[scenario]_[expected_result]`
- Example: `test_register_user_validation_error_wrong_field`

## 🎯 Key Testing Principles

1. **Test Validation First**: Always test data validation before business logic
2. **Mock External Dependencies**: Use mocks for database, external APIs
3. **Test Edge Cases**: Include boundary conditions and error scenarios
4. **Clear Assertions**: Make test failures easy to understand
5. **Descriptive Names**: Test names should explain what is being tested

## 🚨 Common Issues & Solutions

### **422 Validation Errors:**
- ✅ **Expected**: These indicate proper API validation
- ❌ **Unexpected**: Check if request data format is correct

### **Database Connection Errors:**
- Use mock database for unit tests
- Ensure MongoDB is running for integration tests

### **Import Errors:**
- Check that all `__init__.py` files are present
- Verify import paths are correct

## 📚 Additional Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Python Mocking**: https://docs.python.org/3/library/unittest.mock.html

---

**Note**: All test files are properly organized within the `app/tests/` directory structure. Never create test files outside this directory.
