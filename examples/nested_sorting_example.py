"""
Example demonstrating the nested field sorting feature.

This example replicates the use case described in the issue.
"""

from unittest.mock import MagicMock

from django_opensearch_dsl_filtering.filters import (
    CharFilter,
    DocumentFilterSet,
    RangeFilter,
)


def example_company_filterset():
    """Example showing how to configure nested field sorting for companies."""

    # Mock the document class (in real use, this would be your actual Document)
    mock_document = MagicMock()
    mock_search = MagicMock()
    mock_document.search.return_value = mock_search

    # Mock the search object to return itself for method chaining
    mock_search.query.return_value = mock_search
    mock_search.sort.return_value = mock_search
    mock_search.__getitem__.return_value = mock_search

    class CompanyFilterSet(DocumentFilterSet):
        document = mock_document

        # Company Fields
        company_name = CharFilter(
            field_name="company_name__raw_search_field",
            label="Company Name",
            lookup_expr="wildcard",
        )
        company_number = CharFilter(
            field_name="company_number",
            label="Company Number",
            lookup_expr="wildcard",
        )

        # Accounting fields
        number_of_employees = RangeFilter(
            field_name="primary_accounts__Number_of_Employees",
            label="Number of Employees",
        )

        # Define sorting options
        SORT_CHOICES = [
            ("", "Default"),
            ("company_name", "Company Name (A-Z)"),
            ("-company_name", "Company Name (Z-A)"),
            ("number_of_employees", "Employees (Low to High)"),
            ("-number_of_employees", "Employees (High to Low)"),
        ]

        # Configure nested field sorting
        # This replicates the manual sort configuration from the issue
        NESTED_SORT_FIELDS = {
            "number_of_employees": {
                "field": "primary_accounts.Number_of_Employees",
                "nested_path": "primary_accounts",
                "mode": "max",
            }
        }

    # Create a filterset with descending sort on number of employees
    filterset = CompanyFilterSet(data={"sort": "-number_of_employees"})
    search = filterset.search()

    # Verify the sort was applied correctly
    # This should match the manual configuration from the issue:
    # search.sort({
    #     "primary_accounts.Number_of_Employees": {
    #         "order": "desc",
    #         "mode": "max",
    #         "nested": {"path": "primary_accounts"},
    #     }
    # })

    expected_sort = {
        "primary_accounts.Number_of_Employees": {
            "order": "desc",
            "mode": "max",
            "nested": {"path": "primary_accounts"},
        }
    }

    # Get the actual sort call
    actual_sort_call = mock_search.sort.call_args[0][0]

    print("Expected sort configuration:")
    print(expected_sort)
    print("\nActual sort configuration:")
    print(actual_sort_call)
    print("\nMatch:", expected_sort == actual_sort_call)

    return expected_sort == actual_sort_call


if __name__ == "__main__":
    success = example_company_filterset()
    if success:
        print("\n✓ Example works correctly!")
        print(
            "The nested field sorting now replicates the manual configuration "
            "from the issue."
        )
    else:
        print("\n✗ Example failed!")
