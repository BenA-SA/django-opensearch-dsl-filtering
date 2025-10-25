"""
Unit tests for filters without requiring OpenSearch.
"""

import pytest
from django import forms

from django_opensearch_dsl_filtering import (
    BooleanFilter,
    CharFilter,
    DateFilter,
    NumericFilter,
    RangeFilter,
)


@pytest.mark.unit
class TestCharFilter:
    """Test CharFilter functionality."""

    def test_init_with_defaults(self):
        """Test CharFilter initialization with defaults."""
        filter_obj = CharFilter(field_name="title")

        assert filter_obj.field_name == "title"
        assert filter_obj.label == "Title"
        assert filter_obj.lookup_expr == "match"

    def test_init_with_custom_values(self):
        """Test CharFilter initialization with custom values."""
        filter_obj = CharFilter(
            field_name="author",
            lookup_expr="term",
            label="Book Author",
        )

        assert filter_obj.field_name == "author"
        assert filter_obj.label == "Book Author"
        assert filter_obj.lookup_expr == "term"

    def test_get_form_field(self):
        """Test CharFilter form field generation."""
        filter_obj = CharFilter(field_name="title", label="Book Title")
        form_field = filter_obj.get_form_field()

        assert isinstance(form_field, forms.CharField)
        assert form_field.label == "Book Title"
        assert form_field.required is False


@pytest.mark.unit
class TestNumericFilter:
    """Test NumericFilter functionality."""

    def test_init_with_defaults(self):
        """Test NumericFilter initialization with defaults."""
        filter_obj = NumericFilter(field_name="price")

        assert filter_obj.field_name == "price"
        assert filter_obj.label == "Price"
        assert filter_obj.lookup_expr == "term"

    def test_init_with_custom_values(self):
        """Test NumericFilter initialization with custom values."""
        filter_obj = NumericFilter(
            field_name="price",
            lookup_expr="gte",
            label="Minimum Price",
        )

        assert filter_obj.field_name == "price"
        assert filter_obj.label == "Minimum Price"
        assert filter_obj.lookup_expr == "gte"

    def test_get_form_field(self):
        """Test NumericFilter form field generation."""
        filter_obj = NumericFilter(field_name="price", label="Book Price")
        form_field = filter_obj.get_form_field()

        assert isinstance(form_field, forms.FloatField)
        assert form_field.label == "Book Price"
        assert form_field.required is False


@pytest.mark.unit
class TestDateFilter:
    """Test DateFilter functionality."""

    def test_init_with_defaults(self):
        """Test DateFilter initialization with defaults."""
        filter_obj = DateFilter(field_name="publication_date")

        assert filter_obj.field_name == "publication_date"
        assert filter_obj.label == "Publication Date"
        assert filter_obj.lookup_expr == "term"

    def test_get_form_field(self):
        """Test DateFilter form field generation."""
        filter_obj = DateFilter(
            field_name="publication_date",
            label="Published On",
        )
        form_field = filter_obj.get_form_field()

        assert isinstance(form_field, forms.DateField)
        assert form_field.label == "Published On"
        assert form_field.required is False


@pytest.mark.unit
class TestBooleanFilter:
    """Test BooleanFilter functionality."""

    def test_init_with_defaults(self):
        """Test BooleanFilter initialization with defaults."""
        filter_obj = BooleanFilter(field_name="in_stock")

        assert filter_obj.field_name == "in_stock"
        assert filter_obj.label == "In Stock"

    def test_get_form_field(self):
        """Test BooleanFilter form field generation."""
        filter_obj = BooleanFilter(field_name="in_stock", label="Available")
        form_field = filter_obj.get_form_field()

        assert isinstance(form_field, forms.BooleanField)
        assert form_field.label == "Available"
        assert form_field.required is False


@pytest.mark.unit
class TestRangeFilter:
    """Test RangeFilter functionality."""

    def test_init_with_defaults(self):
        """Test RangeFilter initialization with defaults."""
        filter_obj = RangeFilter(field_name="price")

        assert filter_obj.field_name == "price"
        assert filter_obj.label == "Price"
        assert filter_obj.min_label == "Min Price"
        assert filter_obj.max_label == "Max Price"

    def test_init_with_custom_labels(self):
        """Test RangeFilter initialization with custom labels."""
        filter_obj = RangeFilter(
            field_name="price",
            label="Book Price",
            min_label="From",
            max_label="To",
        )

        assert filter_obj.field_name == "price"
        assert filter_obj.label == "Book Price"
        assert filter_obj.min_label == "From"
        assert filter_obj.max_label == "To"

    def test_get_form_field(self):
        """Test RangeFilter form field generation."""
        filter_obj = RangeFilter(field_name="price")
        form_fields = filter_obj.get_form_field()

        assert isinstance(form_fields, dict)
        assert "min_value" in form_fields
        assert "max_value" in form_fields
        assert isinstance(form_fields["min_value"], forms.FloatField)
        assert isinstance(form_fields["max_value"], forms.FloatField)
        assert form_fields["min_value"].label == "Min Price"
        assert form_fields["max_value"].label == "Max Price"
