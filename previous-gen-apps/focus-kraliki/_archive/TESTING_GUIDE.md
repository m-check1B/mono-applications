# Testing Guide for Focus Lite

## Overview

This guide covers all testing procedures for the Focus Lite application, including unit tests, integration tests, end-to-end tests, and health checks.

## Table of Contents

- [Quick Start](#quick-start)
- [Test Suite Structure](#test-suite-structure)
- [Running Tests](#running-tests)
- [Integration Tests](#integration-tests)
- [End-to-End Tests](#end-to-end-tests)
- [Health Checks](#health-checks)
- [Test Coverage](#test-coverage)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx

# Verify installation
pytest --version
```

### Run All Tests

```bash
# From the project root
./test_e2e.sh

# Or just integration tests
cd backend
pytest tests/integration/ -v
```

## Test Suite Structure

```
backend/tests/
├── conftest.py                          # Root test fixtures
├── integration/
│   ├── conftest.py                      # Integration-specific fixtures
│   ├── test_knowledge_flow.py           # Knowledge CRUD + AI chat tests
│   ├── test_agent_tools_api.py          # II-Agent tools API tests
│   └── test_settings_byok.py            # Settings + BYOK tests
├── unit/
│   ├── test_auth.py                     # Authentication tests
│   ├── test_flow_memory.py              # Flow memory tests
│   └── ...                              # Other unit tests
└── e2e/
    └── ...                              # End-to-end tests

Root level:
├── test_e2e.sh                          # End-to-end test runner
├── health_check.sh                      # Service health checker
└── TESTING_GUIDE.md                     # This file
```

## Running Tests

### Integration Tests Only

```bash
cd backend

# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_knowledge_flow.py -v

# Run specific test class
pytest tests/integration/test_knowledge_flow.py::TestKnowledgeTypeCRUD -v

# Run specific test
pytest tests/integration/test_knowledge_flow.py::TestKnowledgeTypeCRUD::test_list_item_types_creates_defaults -v
```

### With Coverage

```bash
# Generate coverage report
pytest tests/integration/ --cov=app --cov-report=html --cov-report=term

# View HTML report
open backend/htmlcov/index.html  # macOS
xdg-open backend/htmlcov/index.html  # Linux
```

### Watch Mode (Development)

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw tests/integration/ -- -v
```

## Integration Tests

### Test Categories

#### 1. Knowledge Flow Tests (`test_knowledge_flow.py`)

Tests the knowledge management system:

- **Knowledge Type CRUD**
  - Creating default types on first access
  - Custom type creation
  - Type updates and deletion
  - Cascade deletion of items

- **Knowledge Item CRUD**
  - Item creation and validation
  - Listing with filters
  - Updates and completion toggling
  - Search functionality

- **AI Chat**
  - Basic chat responses
  - Function calling (create/update items)
  - Usage tracking for free tier
  - BYOK (Bring Your Own Key) support

**Run:**
```bash
pytest tests/integration/test_knowledge_flow.py -v
```

#### 2. Agent Tools API Tests (`test_agent_tools_api.py`)

Tests the II-Agent HTTP API (all 7 tools):

- **Authentication**
  - Agent token validation
  - Regular token compatibility
  - Unauthorized access prevention

- **Knowledge Tools**
  - Create knowledge items
  - Update knowledge items
  - List knowledge items (with filters)

- **Task Tools**
  - Create tasks (with/without projects)
  - Update tasks
  - List tasks (with filters)
  - Auto-completion timestamps

- **Project Tools**
  - Create-or-get projects
  - Duplicate prevention

- **Data Isolation**
  - User data separation
  - Cross-user access prevention

**Run:**
```bash
pytest tests/integration/test_agent_tools_api.py -v
```

#### 3. Settings & BYOK Tests (`test_settings_byok.py`)

Tests settings and Bring Your Own Key functionality:

- **API Key Management**
  - Save/update/delete API keys
  - Key validation
  - Network error handling

- **Usage Statistics**
  - Free tier tracking
  - Premium user handling
  - BYOK user exemption

- **BYOK Integration**
  - Custom key usage in AI calls
  - Usage limit bypass
  - System key fallback

- **Security**
  - User data isolation
  - Key non-exposure in responses

**Run:**
```bash
pytest tests/integration/test_settings_byok.py -v
```

## End-to-End Tests

The E2E test script (`test_e2e.sh`) performs comprehensive system testing.

### What It Tests

1. **Service Health**
   - Backend API (port 3017)
   - II-Agent WebSocket (port 8765)
   - Frontend (port 5173)

2. **Database Connectivity**
   - Connection verification
   - Query execution

3. **API Endpoints**
   - Authentication requirements
   - Proper error codes
   - API documentation

4. **Integration Suite**
   - Runs all pytest integration tests
   - Reports results

5. **Configuration**
   - Environment variables
   - Required files

### Running E2E Tests

```bash
# From project root
./test_e2e.sh

# The script will:
# 1. Check all services
# 2. Verify database connection
# 3. Test critical endpoints
# 4. Run integration tests
# 5. Generate report
```

### E2E Test Report

After running, check:
- Console output for summary
- `/tmp/focus_lite_e2e_report_*.txt` for full report
- `/tmp/pytest_output.log` for detailed test output

## Health Checks

The health check script (`health_check.sh`) verifies service status.

### Running Health Checks

```bash
# From project root
./health_check.sh

# Exit codes:
# 0 = All services healthy
# 1 = Some services unhealthy
```

### What It Checks

1. **Backend API**
   - Port listening (3017)
   - Health endpoint response
   - API version info

2. **Database**
   - Connection via backend
   - Query execution

3. **II-Agent WebSocket**
   - Port listening (8765)
   - WebSocket upgrade support

4. **Frontend**
   - Port listening (5173)
   - Application serving

5. **Critical Endpoints**
   - Knowledge API security
   - Agent tools security
   - Settings security
   - Knowledge AI security

### Health Check in CI/CD

```yaml
# Example GitHub Actions workflow
- name: Health Check
  run: |
    ./health_check.sh
    if [ $? -ne 0 ]; then
      echo "Health check failed"
      exit 1
    fi
```

## Test Coverage

### Coverage Requirements

- **Target Coverage:** 90%+
- **Minimum Coverage:** 80%
- **Critical Paths:** 95%+

### Checking Coverage

```bash
# Generate coverage report
cd backend
pytest tests/integration/ --cov=app --cov-report=term-missing

# HTML report with line-by-line coverage
pytest tests/integration/ --cov=app --cov-report=html
```

### Coverage by Module

Expected coverage levels:

- `app/routers/knowledge.py`: 95%+
- `app/routers/knowledge_ai.py`: 90%+
- `app/routers/agent_tools.py`: 95%+
- `app/routers/settings.py`: 95%+
- `app/models/*`: 90%+
- `app/services/*`: 85%+

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:testpass@localhost:5432/testdb
          JWT_SECRET: test-secret-key
        run: |
          cd backend
          pytest tests/integration/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: backend/coverage.xml

      - name: Run E2E tests
        run: |
          ./test_e2e.sh
```

### GitLab CI Example

```yaml
test:
  stage: test
  image: python:3.11
  services:
    - postgres:15
  variables:
    POSTGRES_DB: testdb
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: testpass
    DATABASE_URL: postgresql://postgres:testpass@postgres:5432/testdb
    JWT_SECRET: test-secret-key
  script:
    - cd backend
    - pip install -r requirements.txt
    - pip install pytest pytest-asyncio pytest-cov httpx
    - pytest tests/integration/ -v --cov=app --cov-report=term --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure you're in the backend directory
cd backend

# Check Python path
echo $PYTHONPATH

# Run tests with proper path
PYTHONPATH=. pytest tests/integration/ -v
```

#### 2. Database Connection Errors

**Problem:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Check database is running
docker ps | grep postgres

# Verify DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL

# Test connection manually
psql $DATABASE_URL -c "SELECT 1"
```

#### 3. Fixture Not Found

**Problem:** `fixture 'test_user_with_knowledge_types' not found`

**Solution:**
```bash
# Ensure conftest.py exists in correct location
ls backend/tests/integration/conftest.py

# Check fixture scope matches usage
# Verify fixture is properly imported
```

#### 4. Tests Passing Locally but Failing in CI

**Solution:**
```bash
# Check environment variables
env | grep -E "DATABASE_URL|JWT_SECRET"

# Ensure test database is fresh
pytest tests/integration/ -v --create-db

# Check service dependencies
./health_check.sh
```

#### 5. Mock Not Working

**Problem:** `TypeError: 'Mock' object is not callable`

**Solution:**
```python
# Use proper mock setup
from unittest.mock import Mock, patch

# Example: Mock OpenRouter client
with patch("app.routers.knowledge_ai.get_openrouter_client") as mock:
    mock_client = Mock()
    mock.return_value = mock_client
    # ... rest of test
```

#### 6. Async Test Errors

**Problem:** `RuntimeError: Event loop is closed`

**Solution:**
```python
# Ensure test is marked as async
@pytest.mark.asyncio
async def test_something(async_client: AsyncClient):
    response = await async_client.get("/endpoint")

# Check event_loop fixture in conftest.py
```

### Debug Mode

```bash
# Run tests with debug output
pytest tests/integration/ -v -s --log-cli-level=DEBUG

# Run single test with full traceback
pytest tests/integration/test_knowledge_flow.py::test_name -vvv

# Drop into debugger on failure
pytest tests/integration/ --pdb
```

### Test Data Cleanup

```bash
# Clean test database
rm backend/test.db

# Clear pytest cache
rm -rf backend/.pytest_cache

# Clear coverage data
rm backend/.coverage
rm -rf backend/htmlcov
```

## Best Practices

### Writing New Tests

1. **Use Descriptive Names**
   ```python
   # Good
   def test_knowledge_item_creation_validates_type_id():

   # Bad
   def test_create():
   ```

2. **Follow AAA Pattern**
   ```python
   async def test_something(async_client, auth_headers):
       # Arrange
       data = {"title": "Test"}

       # Act
       response = await async_client.post("/endpoint", json=data, headers=auth_headers)

       # Assert
       assert response.status_code == 200
   ```

3. **Test One Thing**
   - Each test should verify one specific behavior
   - Use multiple tests for multiple scenarios

4. **Use Fixtures**
   - Avoid repetitive setup
   - Share common test data via fixtures

5. **Mock External Services**
   - Don't call real OpenRouter API
   - Mock HTTP clients
   - Use test databases

### Test Organization

```python
class TestFeatureName:
    """Group related tests in classes."""

    @pytest.mark.asyncio
    async def test_happy_path(self, ...):
        """Test the main success scenario."""
        pass

    @pytest.mark.asyncio
    async def test_error_handling(self, ...):
        """Test error conditions."""
        pass

    @pytest.mark.asyncio
    async def test_edge_case(self, ...):
        """Test boundary conditions."""
        pass
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX Testing](https://www.python-httpx.org/advanced/#calling-into-python-web-apps)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

## Support

For testing issues:

1. Check this guide
2. Review test output and logs
3. Run health checks
4. Check service status
5. Consult team or documentation

---

**Last Updated:** 2025-01-14
**Version:** 1.0.0
