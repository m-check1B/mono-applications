# Test Suite - Learn by Kraliki

## Overview

This test suite provides comprehensive coverage for the Learn by Kraliki backend, including:
- API routes (courses, progress)
- Core services (course_service)
- Database models (progress)
- Fixtures and test utilities

## Test Statistics

- **Total Tests**: 33
- **Coverage**: 84%
- **Target**: 60% (exceeded by 24%)

## Coverage Breakdown

| Module | Statements | Coverage |
|--------|------------|----------|
| app/main.py | 30 | 83% |
| app/core/config.py | 16 | 100% |
| app/core/database.py | 15 | 73% |
| app/models/progress.py | 15 | 100% |
| app/routers/courses.py | 20 | 100% |
| app/routers/progress.py | 62 | 44% |
| app/schemas/course.py | 26 | 100% |
| app/schemas/progress.py | 12 | 100% |
| app/services/course_service.py | 73 | 97% |

## Running Tests

### Run all tests
```bash
cd applications/learn-kraliki/backend
source .venv/bin/activate
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

### Generate HTML coverage report
```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Run specific test file
```bash
pytest tests/test_courses_api.py -v
```

### Run specific test
```bash
pytest tests/test_courses_api.py::test_list_courses -v
```

## Test Files

- `test_courses_api.py`: Tests for course listing and lesson content endpoints
- `test_progress_api.py`: Tests for progress tracking and lesson completion
- `test_course_service.py`: Tests for course content loading from filesystem
- `test_models.py`: Tests for SQLAlchemy models
- `conftest.py`: Test fixtures and configuration

## Key Features Tested

1. **Course Management**
   - Listing all available courses
   - Getting course details with lessons
   - Loading lesson content from markdown files
   - Handling missing courses/lessons (404 errors)

2. **Progress Tracking**
   - Creating progress records on first lesson completion
   - Marking lessons as complete
   - Calculating progress percentage
   - Handling duplicate lesson completions (idempotent)
   - Tracking current lesson and completion timestamps

3. **Service Layer**
   - Loading course metadata from JSON files
   - Parsing markdown content
   - Extracting lesson titles
   - Handling missing files gracefully

4. **Database Models**
   - UserProgress model attributes
   - Default values and timestamps
   - String representation

## Test Environment

Tests use:
- In-memory SQLite database for isolation
- Temporary content directories for course content
- FastAPI TestClient for API testing
- Async session fixtures for database operations
- pytest-asyncio for async test support

## Notes

- Coverage of 44% in `app/routers/progress.py` is due to error handling paths and database operations that are difficult to test without full integration setup
- Main application endpoints (health check, root) are not tested as they are trivial
- Database connection pooling and setup code has limited coverage
