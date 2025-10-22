"""
Tests for pagination functionality in DocumentFilterSet.

This test module verifies that pagination correctly handles edge cases,
particularly when the requested page number exceeds the maximum available pages.
"""

import unittest
from unittest.mock import MagicMock, Mock

from django_opensearch_dsl_filtering import DocumentFilterSet


class TestPaginationMaxPage(unittest.TestCase):
    """Test cases for pagination with page numbers exceeding maximum."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock document class
        self.mock_document = Mock()
        self.mock_document.search = Mock()

        # Create a test filter set class
        class TestFilterSet(DocumentFilterSet):
            document = self.mock_document

        self.filterset_class = TestFilterSet

    def test_page_exceeds_max_redirects_to_last_page(self):
        """Test that requesting page beyond max returns last page."""
        # Mock the search object and its methods
        mock_search = MagicMock()
        mock_search.count.return_value = 15  # Total 15 results
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 3 with page_size 10 (should have max 2 pages)
        filterset = self.filterset_class(data={"page": 3, "page_size": 10})
        filterset.search()

        # Should slice from page 2 (page 10-19, i.e., start=10, end=20)
        # Page 2 is the last valid page
        mock_search.__getitem__.assert_called_once_with(slice(10, 20))

    def test_page_exceeds_max_with_different_page_size(self):
        """Test pagination with different page sizes."""
        # Mock the search object
        mock_search = MagicMock()
        mock_search.count.return_value = 25  # Total 25 results
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 10 with page_size 5 (should have max 5 pages)
        filterset = self.filterset_class(data={"page": 10, "page_size": 5})
        filterset.search()

        # Should slice from page 5 (page 20-24, i.e., start=20, end=25)
        mock_search.__getitem__.assert_called_once_with(slice(20, 25))

    def test_valid_page_number_unchanged(self):
        """Test that valid page numbers are not modified."""
        # Mock the search object
        mock_search = MagicMock()
        mock_search.count.return_value = 30  # Total 30 results
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 2 with page_size 10 (valid page)
        filterset = self.filterset_class(data={"page": 2, "page_size": 10})
        filterset.search()

        # Should slice from page 2 (items 10-19, i.e., start=10, end=20)
        mock_search.__getitem__.assert_called_once_with(slice(10, 20))

    def test_empty_results_defaults_to_page_one(self):
        """Test that empty results default to page 1."""
        # Mock the search object
        mock_search = MagicMock()
        mock_search.count.return_value = 0  # No results
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 5 with no results
        filterset = self.filterset_class(data={"page": 5, "page_size": 10})
        filterset.search()

        # Should default to page 1 (items 0-9, i.e., start=0, end=10)
        mock_search.__getitem__.assert_called_once_with(slice(0, 10))

    def test_exact_page_boundary(self):
        """Test pagination at exact page boundaries."""
        # Mock the search object
        mock_search = MagicMock()
        mock_search.count.return_value = 20  # Exactly 2 pages with size 10
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 2 (valid last page)
        filterset = self.filterset_class(data={"page": 2, "page_size": 10})
        filterset.search()

        # Should slice from page 2 (items 10-19, i.e., start=10, end=20)
        mock_search.__getitem__.assert_called_once_with(slice(10, 20))

    def test_page_boundary_plus_one(self):
        """Test requesting one page beyond the boundary."""
        # Mock the search object
        mock_search = MagicMock()
        mock_search.count.return_value = 20  # Exactly 2 pages with size 10
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 3 (one beyond max)
        filterset = self.filterset_class(data={"page": 3, "page_size": 10})
        filterset.search()

        # Should redirect to page 2 (items 10-19, i.e., start=10, end=20)
        mock_search.__getitem__.assert_called_once_with(slice(10, 20))

    def test_single_result_multiple_page_request(self):
        """Test with single result but requesting high page number."""
        # Mock the search object
        mock_search = MagicMock()
        mock_search.count.return_value = 1  # Only 1 result
        mock_search.filter.return_value = mock_search
        mock_search.query.return_value = mock_search
        mock_search.sort.return_value = mock_search
        mock_search.__getitem__.return_value = mock_search

        self.mock_document.search.return_value = mock_search

        # Request page 100 with only 1 result
        filterset = self.filterset_class(data={"page": 100, "page_size": 10})
        filterset.search()

        # Should redirect to page 1 (items 0-9, i.e., start=0, end=10)
        mock_search.__getitem__.assert_called_once_with(slice(0, 10))


if __name__ == "__main__":
    unittest.main()
