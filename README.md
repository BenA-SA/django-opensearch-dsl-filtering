# Django Opensearch DSL Filtering

A filtering system for Opensearch documents similar to django-filter, but designed to work with Opensearch queries instead of Django ORM.

## Installation

```bash
pip install django-opensearch-dsl-filtering
```

## Features

- Filter Opensearch documents using a familiar Django-like API
- Generate Django forms for your filters automatically
- Support for pagination and sorting
- Various filter types: CharFilter, NumericFilter, RangeFilter, DateFilter, BooleanFilter

## Quick Start

### Define a Document FilterSet

```python
from django_opensearch_dsl import Document
from django_opensearch_dsl_filtering import CharFilter, DateFilter, DocumentFilterSet, NumericFilter

# Assuming you have a Document class defined
class BookDocument(Document):
    # Your document definition here
    class Index:
        name = "books"

    class Django:
        model = Book
        fields = ["id"]

# Create a FilterSet for your document
class BookDocumentFilterSet(DocumentFilterSet):
    document = BookDocument

    # Define filters
    title = CharFilter(field_name="title", lookup_expr="match", label="Title")
    author = CharFilter(field_name="author", lookup_expr="match", label="Author")
    publication_date = DateFilter(field_name="publication_date", label="Publication Date")
    price = NumericFilter(field_name="price", label="Price")
    price_min = NumericFilter(field_name="price", lookup_expr="gte", label="Min Price")
    price_max = NumericFilter(field_name="price", lookup_expr="lte", label="Max Price")

    # Define sorting options
    SORT_CHOICES = [
        ("", "Default"),
        ("title", "Title (A-Z)"),
        ("-title", "Title (Z-A)"),
        ("price", "Price (Low to High)"),
        ("-price", "Price (High to Low)"),
    ]
```

### Use the FilterSet in a View

```python
from django.shortcuts import render

def book_search(request):
    # Create a filter set with the request data
    filter_set = BookDocumentFilterSet(data=request.GET)

    # Get the search results
    search = filter_set.search()
    results = search.execute()

    # Get the form for rendering in the template
    form = filter_set.get_form()

    return render(
        request,
        "books/search.html",
        {
            "form": form,
            "results": results,
        },
    )
```

### Use the Form in a Template

```html
<form method="get">
    {{ form.as_p }}
    <button type="submit">Search</button>
</form>

<div class="results">
    {% for result in results %}
        <div class="result">
            <h2>{{ result.title }}</h2>
            <p>Author: {{ result.author }}</p>
            <p>Price: ${{ result.price }}</p>
        </div>
    {% endfor %}
</div>
```

## Available Filters

- `CharFilter`: For text fields
- `NumericFilter`: For numeric fields
- `RangeFilter`: For numeric fields with a range
- `DateFilter`: For date fields
- `BooleanFilter`: For boolean fields

## Customizing Filters

Each filter can be customized with the following parameters:

- `field_name`: The name of the field to filter on
- `lookup_expr`: The lookup expression to use (e.g., "match", "term", "wildcard", "gt", "lt", etc.)
- `label`: The label to use for the form field

## Sorting on Nested Fields

When working with nested fields in Opensearch, you may need to configure special sorting behavior. The `DocumentFilterSet` class supports nested field sorting through the `NESTED_SORT_FIELDS` attribute.

### Example with Nested Fields

```python
from django_opensearch_dsl import Document, fields
from django_opensearch_dsl_filtering import DocumentFilterSet, RangeFilter

class CompanyDocument(Document):
    company_name = fields.TextField(
        fields={"raw_search_field": fields.KeywordField()},
    )
    company_number = fields.TextField()
    primary_accounts = fields.NestedField(
        properties={
            "Date": fields.DateField(),
            "Number_of_Employees": fields.IntegerField(),
        }
    )

class CompanyFilterSet(DocumentFilterSet):
    document = CompanyDocument

    # Filters
    number_of_employees = RangeFilter(
        field_name="primary_accounts__Number_of_Employees",
        label="Number of Employees"
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
    NESTED_SORT_FIELDS = {
        "number_of_employees": {
            "field": "primary_accounts.Number_of_Employees",
            "nested_path": "primary_accounts",
            "mode": "max",  # Options: max, min, avg, sum, median
        }
    }
```

### Nested Sort Field Configuration

The `NESTED_SORT_FIELDS` dictionary accepts the following parameters for each field:

- `field`: The actual Opensearch field path (required)
- `nested_path`: The path to the nested object (required)
- `mode`: How to aggregate multiple values (optional, default: "avg")
  - `max`: Use the maximum value
  - `min`: Use the minimum value
  - `avg`: Use the average value
  - `sum`: Use the sum of all values
  - `median`: Use the median value

## License

MIT
