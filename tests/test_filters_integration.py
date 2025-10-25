"""
Integration tests for filters with OpenSearch.
"""
import time
from datetime import date, timedelta

import pytest

from django_opensearch_dsl_filtering import (
    BooleanFilter,
    CharFilter,
    DateFilter,
    DocumentFilterSet,
    NumericFilter,
    RangeFilter,
)
from test_project.books.documents import BookDocument
from test_project.books.models import Book


class BookDocumentFilterSet(DocumentFilterSet):
    """FilterSet for testing Book documents."""

    document = BookDocument

    title = CharFilter(field_name="title", lookup_expr="match", label="Title")
    author = CharFilter(field_name="author", lookup_expr="match", label="Author")
    isbn = CharFilter(field_name="isbn", lookup_expr="term", label="ISBN")
    publication_date = DateFilter(
        field_name="publication_date",
        lookup_expr="term",
        label="Publication Date",
    )
    price = NumericFilter(field_name="price", lookup_expr="term", label="Price")
    price_min = NumericFilter(
        field_name="price",
        lookup_expr="gte",
        label="Min Price",
    )
    price_max = NumericFilter(
        field_name="price",
        lookup_expr="lte",
        label="Max Price",
    )
    price_range = RangeFilter(field_name="price", label="Price Range")
    in_stock = BooleanFilter(field_name="in_stock", label="In Stock")

    SORT_CHOICES = [
        ("", "Default"),
        ("title.raw", "Title (A-Z)"),
        ("-title.raw", "Title (Z-A)"),
        ("price", "Price (Low to High)"),
        ("-price", "Price (High to Low)"),
    ]


@pytest.fixture
def sample_books(db, opensearch_clean):
    """Create sample books for testing."""
    books = [
        Book.objects.create(
            title="Django for Beginners",
            author="William S. Vincent",
            isbn="9781735467207",
            publication_date=date(2022, 1, 1),
            price=39.99,
            pages=350,
            in_stock=True,
            description="Learn Django by building web applications",
        ),
        Book.objects.create(
            title="Two Scoops of Django",
            author="Daniel Roy Greenfeld",
            isbn="9780692915727",
            publication_date=date(2021, 6, 15),
            price=49.99,
            pages=532,
            in_stock=True,
            description="Best practices for Django development",
        ),
        Book.objects.create(
            title="Python Crash Course",
            author="Eric Matthes",
            isbn="9781593279288",
            publication_date=date(2019, 5, 3),
            price=29.99,
            pages=544,
            in_stock=False,
            description="A hands-on introduction to Python",
        ),
        Book.objects.create(
            title="Test Driven Development",
            author="Harry J.W. Percival",
            isbn="9781491958704",
            publication_date=date(2023, 3, 20),
            price=59.99,
            pages=624,
            in_stock=True,
            description="TDD with Python and Django",
        ),
    ]

    # Index the books in OpenSearch
    for book in books:
        doc = BookDocument()
        doc.update(book)

    # Wait for indexing to complete
    time.sleep(2)

    return books


@pytest.mark.integration
@pytest.mark.django_db
class TestCharFilterIntegration:
    """Integration tests for CharFilter."""

    def test_match_filter(self, sample_books):
        """Test CharFilter with match lookup."""
        filter_set = BookDocumentFilterSet(data={"title": "Django"})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 2
        titles = [hit.title for hit in results]
        assert "Django for Beginners" in titles
        assert "Two Scoops of Django" in titles

    def test_term_filter(self, sample_books):
        """Test CharFilter with term lookup."""
        filter_set = BookDocumentFilterSet(data={"isbn": "9781735467207"})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert results.hits[0].title == "Django for Beginners"

    def test_author_filter(self, sample_books):
        """Test filtering by author."""
        filter_set = BookDocumentFilterSet(data={"author": "Eric"})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert results.hits[0].author == "Eric Matthes"


@pytest.mark.integration
@pytest.mark.django_db
class TestNumericFilterIntegration:
    """Integration tests for NumericFilter."""

    def test_exact_price_filter(self, sample_books):
        """Test NumericFilter with exact value."""
        filter_set = BookDocumentFilterSet(data={"price": 39.99})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert results.hits[0].title == "Django for Beginners"

    def test_min_price_filter(self, sample_books):
        """Test NumericFilter with gte lookup."""
        filter_set = BookDocumentFilterSet(data={"price_min": 50})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert results.hits[0].price == 59.99

    def test_max_price_filter(self, sample_books):
        """Test NumericFilter with lte lookup."""
        filter_set = BookDocumentFilterSet(data={"price_max": 40})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 2
        prices = [hit.price for hit in results]
        assert 39.99 in prices
        assert 29.99 in prices


@pytest.mark.integration
@pytest.mark.django_db
class TestRangeFilterIntegration:
    """Integration tests for RangeFilter."""

    def test_price_range_min_only(self, sample_books):
        """Test RangeFilter with only min value."""
        filter_set = BookDocumentFilterSet(
            data={"price_range_min_value": 40, "price_range_max_value": ""}
        )
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 2
        prices = [hit.price for hit in results]
        assert all(p >= 40 for p in prices)

    def test_price_range_max_only(self, sample_books):
        """Test RangeFilter with only max value."""
        filter_set = BookDocumentFilterSet(
            data={"price_range_min_value": "", "price_range_max_value": 40}
        )
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 2
        prices = [hit.price for hit in results]
        assert all(p <= 40 for p in prices)

    def test_price_range_both_values(self, sample_books):
        """Test RangeFilter with both min and max values."""
        filter_set = BookDocumentFilterSet(
            data={"price_range_min_value": 30, "price_range_max_value": 50}
        )
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 2
        prices = [hit.price for hit in results]
        assert all(30 <= p <= 50 for p in prices)


@pytest.mark.integration
@pytest.mark.django_db
class TestBooleanFilterIntegration:
    """Integration tests for BooleanFilter."""

    def test_in_stock_true(self, sample_books):
        """Test BooleanFilter with True value."""
        filter_set = BookDocumentFilterSet(data={"in_stock": True})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 3
        assert all(hit.in_stock for hit in results)

    def test_in_stock_false(self, sample_books):
        """Test BooleanFilter with False value."""
        filter_set = BookDocumentFilterSet(data={"in_stock": False})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert not results.hits[0].in_stock


@pytest.mark.integration
@pytest.mark.django_db
class TestDateFilterIntegration:
    """Integration tests for DateFilter."""

    def test_exact_date_filter(self, sample_books):
        """Test DateFilter with exact date."""
        filter_set = BookDocumentFilterSet(
            data={"publication_date": "2022-01-01"}
        )
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert results.hits[0].title == "Django for Beginners"


@pytest.mark.integration
@pytest.mark.django_db
class TestDocumentFilterSetIntegration:
    """Integration tests for DocumentFilterSet."""

    def test_sorting_ascending(self, sample_books):
        """Test sorting in ascending order."""
        filter_set = BookDocumentFilterSet(data={"sort": "price"})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 4
        prices = [hit.price for hit in results]
        assert prices == sorted(prices)

    def test_sorting_descending(self, sample_books):
        """Test sorting in descending order."""
        filter_set = BookDocumentFilterSet(data={"sort": "-price"})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 4
        prices = [hit.price for hit in results]
        assert prices == sorted(prices, reverse=True)

    def test_pagination(self, sample_books):
        """Test pagination functionality."""
        # First page with 2 items
        filter_set = BookDocumentFilterSet(data={"page": 1, "page_size": 2})
        search = filter_set.search()
        results = search.execute()

        assert len(results.hits) == 2

        # Second page with 2 items
        filter_set = BookDocumentFilterSet(data={"page": 2, "page_size": 2})
        search = filter_set.search()
        results = search.execute()

        assert len(results.hits) == 2

    def test_combined_filters(self, sample_books):
        """Test combining multiple filters."""
        filter_set = BookDocumentFilterSet(
            data={
                "author": "Daniel",
                "in_stock": True,
                "price_min": 40,
            }
        )
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 1
        assert results.hits[0].title == "Two Scoops of Django"

    def test_get_form(self, sample_books):
        """Test form generation."""
        filter_set = BookDocumentFilterSet()
        form = filter_set.get_form()

        # Check that form has all expected fields
        assert "title" in form.fields
        assert "author" in form.fields
        assert "isbn" in form.fields
        assert "price" in form.fields
        assert "price_min" in form.fields
        assert "price_max" in form.fields
        assert "price_range_min_value" in form.fields
        assert "price_range_max_value" in form.fields
        assert "in_stock" in form.fields
        assert "sort" in form.fields
        assert "page" in form.fields
        assert "page_size" in form.fields

    def test_empty_filter_returns_all(self, sample_books):
        """Test that empty filter returns all results."""
        filter_set = BookDocumentFilterSet(data={})
        search = filter_set.search()
        results = search.execute()

        assert results.hits.total.value == 4
