"""
Pytest configuration and fixtures.
"""

import os
import time

import pytest
from django.core.management import call_command
from opensearchpy import OpenSearch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project.settings")


def pytest_configure(config):
    """Configure Django settings for pytest."""
    from django.conf import settings

    if not settings.configured:
        settings.configure()

    import django

    django.setup()


@pytest.fixture(scope="session")
def django_db_setup():
    """Set up the test database."""
    from django.conf import settings

    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }


@pytest.fixture(scope="session")
def opensearch_client():
    """Create an OpenSearch client for testing."""
    from django.conf import settings

    opensearch_config = settings.OPENSEARCH_DSL["default"]
    host_config = opensearch_config["hosts"][0]

    client = OpenSearch(
        hosts=[{"host": host_config["host"], "port": host_config["port"]}],
        http_auth=None,
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False,
    )

    # Wait for OpenSearch to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            if client.ping():
                break
        except Exception:
            if i == max_retries - 1:
                raise
            time.sleep(1)

    return client


@pytest.fixture(scope="session")
def opensearch_indices(opensearch_client, django_db_setup):
    """Set up OpenSearch indices for testing."""
    # Delete index if it exists using client directly
    try:
        opensearch_client.indices.delete(index="books", ignore=[404])
    except Exception:
        pass

    # Create indices
    call_command("opensearch", "index", "create", "--force")

    yield

    # Clean up indices after tests
    try:
        opensearch_client.indices.delete(index="books", ignore=[404])
    except Exception:
        pass


@pytest.fixture
def opensearch_clean(opensearch_client, opensearch_indices):
    """Clean OpenSearch indices before each test."""
    # Delete all documents from the books index
    try:
        opensearch_client.delete_by_query(
            index="books",
            body={"query": {"match_all": {}}},
            refresh=True,
        )
    except Exception:
        pass  # Index might not exist yet

    yield

    # Clean up after test
    try:
        opensearch_client.delete_by_query(
            index="books",
            body={"query": {"match_all": {}}},
            refresh=True,
        )
    except Exception:
        pass
