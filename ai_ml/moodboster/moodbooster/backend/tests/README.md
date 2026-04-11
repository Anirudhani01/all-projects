# MoodBooster Backend Tests

This directory contains comprehensive tests for the MoodBooster backend application.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_api.py                 # API endpoint tests
├── test_boosters.py            # Booster service tests
├── test_llm_integration.py     # LLM integration tests
├── test_mood.py                # Mood analysis tests
├── test_sessions.py            # Session service tests
├── test_runner.py              # Test runner script
└── README.md                   # This file
```

## Test Categories

### 1. Unit Tests
- **test_mood.py**: Tests for mood analysis functionality
- **test_boosters.py**: Tests for booster service
- **test_sessions.py**: Tests for session management

### 2. Integration Tests
- **test_llm_integration.py**: Tests for LLM integration (Gemini, Ollama)
- **test_api.py**: Tests for API endpoints

### 3. Test Fixtures
- **conftest.py**: Shared fixtures and test configuration

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Install the application
pip install -e .
```

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_mood.py

# Run specific test function
pytest tests/test_mood.py::TestMoodAnalysis::test_analyze_mood_happy
```

### Using the Test Runner
```bash
# Run all tests
python tests/test_runner.py

# Run specific test
python tests/test_runner.py --test test_mood.py

# Run async tests only
python tests/test_runner.py --async-only

# Run with coverage
python tests/test_runner.py --coverage
```

### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only async tests
pytest -m async

# Run only LLM tests
pytest -m llm

# Run only API tests
pytest -m api

# Run only database tests
pytest -m database

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

### Database Testing
- Uses SQLite in-memory database for testing
- Each test gets a fresh database session
- Tables are created and dropped for each test

### LLM Testing
- Tests work with or without LLM services
- Mocks are used when services are unavailable
- Fallback to keyword-based analysis is tested

### API Testing
- Uses FastAPI TestClient for API testing
- Database dependencies are overridden
- Tests cover all endpoints and error cases

## Test Data

### Sample Data
- **sample_diary_entry**: Sample diary entry for testing
- **sample_mood_analysis**: Sample mood analysis result
- **test_cases**: Various test cases for different scenarios

### Mock Data
- LLM responses are mocked for consistent testing
- Database operations are isolated per test
- External API calls are mocked

## Coverage

### Running Coverage
```bash
# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Coverage with minimum threshold
pytest --cov=app --cov-fail-under=80
```

### Coverage Reports
- HTML report: `htmlcov/index.html`
- Terminal report: Shows missing lines
- Minimum coverage: 80%

## Test Categories

### 1. Mood Analysis Tests
- **Happy mood detection**
- **Sad mood detection**
- **Angry mood detection**
- **Stressed mood detection**
- **Neutral mood detection**
- **Edge cases and error handling**
- **Consistency testing**
- **LLM integration testing**

### 2. Booster Service Tests
- **Booster retrieval for each mood**
- **Booster structure validation**
- **Metadata validation**
- **Error handling**

### 3. Session Service Tests
- **Session creation**
- **Session retrieval**
- **Activity tracking**
- **Duration calculation**
- **Data handling**

### 4. API Tests
- **Diary entry creation**
- **Mood analysis endpoints**
- **Booster endpoints**
- **Health check**
- **Error handling**

### 5. LLM Integration Tests
- **Gemini API integration**
- **Ollama integration**
- **Fallback mechanisms**
- **Response parsing**
- **Error handling**

## Best Practices

### Writing Tests
1. **Use descriptive test names**
2. **Test one thing per test**
3. **Use appropriate assertions**
4. **Mock external dependencies**
5. **Test edge cases and errors**

### Test Organization
1. **Group related tests in classes**
2. **Use fixtures for common setup**
3. **Keep tests independent**
4. **Use appropriate markers**

### Performance
1. **Use async tests for async code**
2. **Mock slow operations**
3. **Use database transactions for isolation**
4. **Clean up after tests**

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure PYTHONPATH includes backend directory
2. **Database errors**: Check test database configuration
3. **Async errors**: Use pytest-asyncio and proper async markers
4. **LLM errors**: Ensure services are mocked or available

### Debug Mode
```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest -v -s tests/test_mood.py::TestMoodAnalysis::test_analyze_mood_happy
```

## Continuous Integration

### GitHub Actions
```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov
    pytest --cov=app --cov-report=xml
```

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Run tests before commit
pre-commit run --all-files
```

## Contributing

### Adding New Tests
1. **Follow naming conventions**
2. **Use appropriate test classes**
3. **Add proper docstrings**
4. **Use fixtures when possible**
5. **Test both success and failure cases**

### Test Review
1. **Ensure tests are comprehensive**
2. **Check for proper mocking**
3. **Verify edge case coverage**
4. **Ensure tests are maintainable**
