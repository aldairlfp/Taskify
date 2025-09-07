# 🧪 Taskify API Testing Guide

This guide covers the comprehensive automated testing setup for the Taskify API project.

## 📋 Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_auth.py                # Authentication endpoint tests
├── test_tasks.py               # Task management endpoint tests
├── test_models.py              # Database models and core functionality tests
├── test_api.py                 # General API functionality tests
├── test_performance.py         # Performance and load tests
├── test_integration.py         # End-to-end integration tests
└── test_utils.py              # Testing utilities and helpers
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Basic Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run specific test class
pytest tests/test_models.py::TestAuthCore -v

# Run specific test method
pytest tests/test_models.py::TestAuthCore::test_password_hashing -v
```

### 3. Quick Test Script (Windows)
```bash
quick_test.bat
```

### 4. Full Test Suite with Coverage
```bash
python run_tests.py
```

## 📊 Test Categories

### 🔐 Authentication Tests (`test_auth.py`)
- User registration and validation
- Login/logout functionality
- JWT token handling
- Password security
- Access control

### 📝 Task Management Tests (`test_tasks.py`)
- CRUD operations for tasks
- Data validation
- User ownership verification
- Pagination and filtering
- Error handling

### 🏗️ Model Tests (`test_models.py`)
- Database model validation
- Relationship testing
- Data integrity
- Core authentication functions
- Schema validation

### 🌐 API Tests (`test_api.py`)
- General API functionality
- Error handling
- Security features (XSS, SQL injection protection)
- Content validation
- CORS and headers

### 🚄 Performance Tests (`test_performance.py`)
- Response time validation
- Concurrent user simulation
- Load testing
- Memory usage monitoring
- Stress testing (optional)

### 🔄 Integration Tests (`test_integration.py`)
- Complete user workflows
- Data isolation between users
- End-to-end scenarios
- Error recovery testing

## 🛠️ Test Configuration

### Pytest Configuration (`pytest.ini`)
- Async test support
- Custom markers for test categorization
- Warning filters
- Test discovery settings

### Test Database
- Uses SQLite for testing (fast and isolated)
- Automatic setup and teardown
- Fresh database for each test

### Fixtures (`conftest.py`)
- Database session management
- Test user creation
- Authentication headers
- Async client setup

## 📈 Running Tests with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=app --cov-report=html --cov-report=term

# View HTML coverage report
# Open htmlcov/index.html in your browser
```

## 🏷️ Test Markers

Use markers to run specific types of tests:

```bash
# Run only authentication tests
pytest -m auth

# Run only task-related tests
pytest -m tasks

# Skip slow tests
pytest -m "not slow"

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## 🔧 Available Test Commands

### Basic Testing
```bash
# All tests with verbose output
pytest tests/ -v

# Run tests in parallel (faster)
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x

# Run only failed tests from last run
pytest tests/ --lf
```

### Coverage Testing
```bash
# Basic coverage
pytest tests/ --cov=app

# Coverage with HTML report
pytest tests/ --cov=app --cov-report=html

# Coverage with missing lines
pytest tests/ --cov=app --cov-report=term-missing
```

### Performance Testing
```bash
# Basic performance tests
pytest tests/test_performance.py -v

# Skip long-running stress tests
pytest tests/test_performance.py -v -k "not (sustained_load or maximum_concurrent)"
```

## 🐛 Debugging Tests

### Verbose Output
```bash
pytest tests/ -v -s  # -s shows print statements
```

### Run Specific Tests
```bash
# Run single test method
pytest tests/test_auth.py::TestAuth::test_login_success -v

# Run tests matching pattern
pytest tests/ -k "login" -v
```

### Debug Mode
```bash
# Drop into debugger on failure
pytest tests/ --pdb

# Set breakpoint in test code
import pdb; pdb.set_trace()
```

## 📝 Writing New Tests

### Test Structure
```python
import pytest
from httpx import AsyncClient

class TestNewFeature:
    """Test new feature functionality"""
    
    async def test_new_feature(self, async_client: AsyncClient, authenticated_headers: dict):
        """Test description"""
        # Arrange
        test_data = {"field": "value"}
        
        # Act
        response = await async_client.post("/endpoint", json=test_data, headers=authenticated_headers)
        
        # Assert
        assert response.status_code == 201
        assert response.json()["field"] == "value"
```

### Best Practices
1. **Use descriptive test names** - `test_user_cannot_access_other_users_tasks`
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **Test both success and failure cases**
4. **Use appropriate fixtures** - `async_client`, `authenticated_headers`, etc.
5. **Keep tests independent** - Each test should be able to run alone
6. **Test edge cases** - Empty data, large data, invalid data

### Available Fixtures
- `async_client` - Async HTTP client for API testing
- `db_session` - Database session for direct database testing
- `test_user` - Pre-created test user
- `test_user_token` - Authentication token for test user
- `authenticated_headers` - Headers with valid authentication
- `test_task` - Pre-created test task

## 🚀 Continuous Integration

### GitHub Actions
The project includes GitHub Actions workflow (`.github/workflows/tests.yml`) that:
- Runs tests on multiple Python versions
- Tests against PostgreSQL database
- Generates coverage reports
- Performs security scanning
- Runs on push and pull requests

### Local CI Simulation
```bash
# Run the same tests as CI
pytest tests/ --cov=app --cov-report=xml
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

## 📊 Test Metrics

After running tests with coverage, you can find:
- **Coverage percentage** - How much of your code is tested
- **Missing lines** - Which lines need test coverage
- **HTML report** - Visual coverage report in `htmlcov/`

### Target Metrics
- **Coverage**: Aim for 90%+ test coverage
- **Response Time**: API endpoints should respond < 1 second
- **Concurrent Users**: Should handle 50+ concurrent requests
- **Test Execution**: Full test suite should complete < 2 minutes

## 🛡️ Security Testing

The test suite includes:
- **SQL Injection Protection** - Tests malicious SQL input
- **XSS Protection** - Tests script injection attempts
- **Authentication Security** - Tests token validation
- **Data Isolation** - Ensures users can't access others' data
- **Input Validation** - Tests various invalid inputs

## 🔄 Maintenance

### Regular Tasks
1. **Update test data** when adding new features
2. **Review coverage reports** to identify untested code
3. **Update performance baselines** as the app grows
4. **Add integration tests** for new user workflows
5. **Review and update fixtures** when models change

### When to Run Tests
- **Before committing code** - Run relevant test files
- **Before pushing** - Run full test suite
- **Weekly** - Run performance tests
- **Before releases** - Run all tests including stress tests

## 🆘 Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Make sure virtual environment is activated
.venv\Scripts\activate

# Check if test database is accessible
pytest tests/test_models.py::TestModels::test_user_creation -v
```

**Import Errors**
```bash
# Ensure you're in the project root directory
cd C:\Users\Aldair\work\Taskify

# Check if app module is importable
python -c "from app.models.models import User; print('Import successful')"
```

**Async Test Issues**
```bash
# Make sure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest configuration
pytest --markers | grep asyncio
```

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Async Testing with httpx](https://www.python-httpx.org/async/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/)

---

Happy Testing! 🧪✨
