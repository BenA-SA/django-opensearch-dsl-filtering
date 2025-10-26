"""Tests for nested field sorting functionality."""

import unittest
from unittest.mock import MagicMock

from django_opensearch_dsl_filtering.filters import DocumentFilterSet


class TestNestedFieldSorting(unittest.TestCase):
    """Test cases for nested field sorting."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock document class
        self.mock_document = MagicMock()
        self.mock_search = MagicMock()
        self.mock_document.search.return_value = self.mock_search

        # Mock the search object to return itself for method chaining
        self.mock_search.query.return_value = self.mock_search
        self.mock_search.sort.return_value = self.mock_search
        self.mock_search.__getitem__.return_value = self.mock_search

    def test_simple_ascending_sort(self):
        """Test simple ascending sort without nested fields."""

        class SimpleFilterSet(DocumentFilterSet):
            document = self.mock_document
            SORT_CHOICES = [
                ("", "Default"),
                ("title", "Title (A-Z)"),
                ("-title", "Title (Z-A)"),
            ]

        filterset = SimpleFilterSet(data={"sort": "title"})
        search = filterset.search()  # noqa: F841

        # Verify sort was called with the field name
        self.mock_search.sort.assert_called_with("title")

    def test_simple_descending_sort(self):
        """Test simple descending sort without nested fields."""

        class SimpleFilterSet(DocumentFilterSet):
            document = self.mock_document
            SORT_CHOICES = [
                ("", "Default"),
                ("title", "Title (A-Z)"),
                ("-title", "Title (Z-A)"),
            ]

        filterset = SimpleFilterSet(data={"sort": "-title"})
        search = filterset.search()  # noqa: F841

        # Verify sort was called with the negative field name
        self.mock_search.sort.assert_called_with("-title")

    def test_nested_field_ascending_sort(self):
        """Test nested field sorting in ascending order."""

        class NestedFilterSet(DocumentFilterSet):
            document = self.mock_document
            SORT_CHOICES = [
                ("", "Default"),
                ("number_of_employees", "Number of Employees (Low to High)"),
                ("-number_of_employees", "Number of Employees (High to Low)"),
            ]
            NESTED_SORT_FIELDS = {
                "number_of_employees": {
                    "field": "primary_accounts.Number_of_Employees",
                    "nested_path": "primary_accounts",
                    "mode": "max",
                }
            }

        filterset = NestedFilterSet(data={"sort": "number_of_employees"})
        search = filterset.search()  # noqa: F841

        # Verify sort was called with nested configuration
        expected_sort = {
            "primary_accounts.Number_of_Employees": {
                "order": "asc",
                "mode": "max",
                "nested": {"path": "primary_accounts"},
            }
        }
        self.mock_search.sort.assert_called_with(expected_sort)

    def test_nested_field_descending_sort(self):
        """Test nested field sorting in descending order."""

        class NestedFilterSet(DocumentFilterSet):
            document = self.mock_document
            SORT_CHOICES = [
                ("", "Default"),
                ("number_of_employees", "Number of Employees (Low to High)"),
                ("-number_of_employees", "Number of Employees (High to Low)"),
            ]
            NESTED_SORT_FIELDS = {
                "number_of_employees": {
                    "field": "primary_accounts.Number_of_Employees",
                    "nested_path": "primary_accounts",
                    "mode": "max",
                }
            }

        filterset = NestedFilterSet(data={"sort": "-number_of_employees"})
        search = filterset.search()  # noqa: F841

        # Verify sort was called with nested configuration in descending order
        expected_sort = {
            "primary_accounts.Number_of_Employees": {
                "order": "desc",
                "mode": "max",
                "nested": {"path": "primary_accounts"},
            }
        }
        self.mock_search.sort.assert_called_with(expected_sort)

    def test_nested_field_with_min_mode(self):
        """Test nested field sorting with min mode."""

        class NestedFilterSet(DocumentFilterSet):
            document = self.mock_document
            NESTED_SORT_FIELDS = {
                "employee_count": {
                    "field": "departments.employee_count",
                    "nested_path": "departments",
                    "mode": "min",
                }
            }

        filterset = NestedFilterSet(data={"sort": "employee_count"})
        search = filterset.search()  # noqa: F841

        # Verify sort was called with min mode
        expected_sort = {
            "departments.employee_count": {
                "order": "asc",
                "mode": "min",
                "nested": {"path": "departments"},
            }
        }
        self.mock_search.sort.assert_called_with(expected_sort)

    def test_nested_field_with_default_mode(self):
        """Test nested field sorting with default mode (avg)."""

        class NestedFilterSet(DocumentFilterSet):
            document = self.mock_document
            NESTED_SORT_FIELDS = {
                "salary": {
                    "field": "employees.salary",
                    "nested_path": "employees",
                    # mode not specified, should default to 'avg'
                }
            }

        filterset = NestedFilterSet(data={"sort": "salary"})
        search = filterset.search()  # noqa: F841

        # Verify sort was called with default avg mode
        expected_sort = {
            "employees.salary": {
                "order": "asc",
                "mode": "avg",
                "nested": {"path": "employees"},
            }
        }
        self.mock_search.sort.assert_called_with(expected_sort)

    def test_no_sort_specified(self):
        """Test that no sorting is applied when sort field is not specified."""

        class SimpleFilterSet(DocumentFilterSet):
            document = self.mock_document

        filterset = SimpleFilterSet(data={})
        search = filterset.search()  # noqa: F841

        # Verify sort was not called
        self.mock_search.sort.assert_not_called()

    def test_mixed_nested_and_simple_fields(self):
        """Test that simple and nested fields can coexist in the same filterset."""

        class MixedFilterSet(DocumentFilterSet):
            document = self.mock_document
            SORT_CHOICES = [
                ("", "Default"),
                ("title", "Title (A-Z)"),
                ("-title", "Title (Z-A)"),
                ("employee_count", "Employees (Low to High)"),
                ("-employee_count", "Employees (High to Low)"),
            ]
            NESTED_SORT_FIELDS = {
                "employee_count": {
                    "field": "departments.employee_count",
                    "nested_path": "departments",
                    "mode": "sum",
                }
            }

        # Test simple field
        filterset = MixedFilterSet(data={"sort": "title"})
        search = filterset.search()  # noqa: F841
        self.mock_search.sort.assert_called_with("title")

        # Reset mock
        self.mock_search.reset_mock()

        # Test nested field
        filterset = MixedFilterSet(data={"sort": "employee_count"})
        search = filterset.search()  # noqa: F841
        expected_sort = {
            "departments.employee_count": {
                "order": "asc",
                "mode": "sum",
                "nested": {"path": "departments"},
            }
        }
        self.mock_search.sort.assert_called_with(expected_sort)

    def test_nested_field_missing_nested_path_raises_error(self):
        """Test that missing nested_path raises a ValueError."""

        class InvalidNestedFilterSet(DocumentFilterSet):
            document = self.mock_document
            NESTED_SORT_FIELDS = {
                "employee_count": {
                    "field": "departments.employee_count",
                    # Missing nested_path - should raise error
                }
            }

        filterset = InvalidNestedFilterSet(data={"sort": "employee_count"})

        # Should raise ValueError when trying to search
        with self.assertRaises(ValueError) as context:
            filterset.search()

        self.assertIn("nested_path is required", str(context.exception))
        self.assertIn("employee_count", str(context.exception))


if __name__ == "__main__":
    unittest.main()
