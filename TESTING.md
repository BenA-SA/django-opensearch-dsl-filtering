# Testing Documentation

This document describes the testing infrastructure for django-opensearch-dsl-filtering.

## Overview

The project uses Docker Compose to set up a testing environment with:
- Django application with a test project
- OpenSearch service for integration testing
- pytest for running tests

## Test Project Structure

```
test_project/
├── __init__.py
├── settings.py          # Django settings for testing
├── urls.py              # URL configuration
└── books/               # Sample app for testing
    ├── __init__.py
    ├── apps.py
    ├── models.py        # Book model for testing
    ├── documents.py     # BookDocument for OpenSearch
    └── admin.py         # Admin configuration
```

## Running Tests

### Using Docker Compose (Recommended)

The easiest way to run tests is using Docker Compose, which handles all dependencies:

```bash
# Build and run tests
docker-compose up --build

# Run tests in detached mode
docker-compose up -d

# View logs
docker-compose logs -f django

# Stop services
docker-compose down
```

### Running Tests Locally

If you prefer to run tests locally without Docker:

1. Install dependencies:
```bash
pip install -r requirements/test.txt
```

2. Start OpenSearch:
```bash
# Using Docker
docker run -d \
  -p 9200:9200 \
  -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:2.11.0
```

3. Run migrations and create indices:
```bash
python manage.py migrate
python manage.py opensearch index create --force
```

4. Run tests:
```bash
# Run all tests
pytest

# Run only unit tests (no OpenSearch required)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run with coverage report
pytest --cov=django_opensearch_dsl_filtering --cov-report=html

# Run specific test file
pytest tests/test_filters_unit.py
```

## Test Types

### Unit Tests
Located in `tests/test_filters_unit.py`, these tests don't require OpenSearch and test:
- Filter initialization
- Form field generation
- Basic filter configuration

Run with: `pytest -m unit`

### Integration Tests
Located in `tests/test_filters_integration.py`, these tests require OpenSearch and test:
- Actual filtering with OpenSearch
- Search query generation
- Sorting and pagination
- Combined filters

Run with: `pytest -m integration`

## Test Fixtures

### `django_db_setup`
Sets up an in-memory SQLite database for testing.

### `opensearch_client`
Provides an OpenSearch client connected to the test instance.

### `opensearch_indices`
Creates and manages OpenSearch indices for testing.

### `opensearch_clean`
Cleans OpenSearch indices before and after each test.

### `sample_books`
Creates sample Book instances and indexes them in OpenSearch.

## Continuous Integration

Tests are automatically run on GitHub Actions when you push code or create a pull request.

The workflow:
1. Sets up Python environment
2. Starts OpenSearch service
3. Installs dependencies
4. Runs migrations
5. Creates OpenSearch indices
6. Runs pytest with coverage reporting

## Writing New Tests

When adding new features, follow these guidelines:

1. **Unit tests** for filter logic that doesn't need OpenSearch
2. **Integration tests** for testing actual OpenSearch queries
3. Use appropriate markers (`@pytest.mark.unit` or `@pytest.mark.integration`)
4. Use fixtures for common setup
5. Keep tests focused and independent

Example:

```python
import pytest
from django_opensearch_dsl_filtering import CharFilter

@pytest.mark.unit
def test_char_filter_initialization():
    """Test that CharFilter initializes correctly."""
    filter_obj = CharFilter(field_name="title", label="Book Title")
    assert filter_obj.field_name == "title"
    assert filter_obj.label == "Book Title"

@pytest.mark.integration
@pytest.mark.django_db
def test_char_filter_search(sample_books):
    """Test that CharFilter filters OpenSearch results."""
    # Your test code here
    pass
```

## Coverage

Test coverage reports are generated in:
- Terminal output (with `--cov-report=term-missing`)
- HTML format in `htmlcov/` directory
- XML format for CI tools

View HTML coverage report:
```bash
pytest --cov=django_opensearch_dsl_filtering --cov-report=html
open htmlcov/index.html  # or your browser
```

## Troubleshooting

### OpenSearch not starting
- Check that port 9200 is available
- Ensure you have enough memory allocated to Docker
- Check OpenSearch logs: `docker-compose logs opensearch`

### Tests timing out
- Increase the wait time in `conftest.py`
- Check that OpenSearch is healthy: `curl http://localhost:9200/_cluster/health`

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements/test.txt`
- Check that PYTHONPATH includes the project root

### Database errors
- Make sure migrations are run: `python manage.py migrate`
- Check that test database is properly configured in settings
