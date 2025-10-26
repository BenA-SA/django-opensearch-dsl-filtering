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
from django_opensearch_dsl_filtering import CharFilter, DateFilter, DocumentFilterSet, NumericFilter, PointFilter

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
    location = PointFilter(field_name="location", label="Location")

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
- `PointFilter`: For geo point fields with postcode and distance filtering

## Customizing Filters

Each filter can be customized with the following parameters:

- `field_name`: The name of the field to filter on
- `lookup_expr`: The lookup expression to use (e.g., "match", "term", "wildcard", "gt", "lt", etc.)
- `label`: The label to use for the form field

### PointFilter

The `PointFilter` is specifically designed for geo point fields and provides location-based filtering using UK postcodes:

```python
from django_opensearch_dsl_filtering import PointFilter

class StoreDocumentFilterSet(DocumentFilterSet):
    document = StoreDocument
    
    # Filter stores by proximity to a postcode
    location = PointFilter(
        field_name="location",  # The geo_point field in your document
        label="Find Stores Near You",
        postcode_label="Postcode",
        distance_label="Distance (miles)"
    )
```

**How it works:**
1. Users enter a UK postcode (e.g., "SW1A 1AA") and a distance in miles
2. The filter calls the postcodes.io API to get latitude/longitude coordinates
3. An OpenSearch `geo_distance` query filters results within the specified radius
4. The distance is automatically converted from miles to kilometers for OpenSearch

**Requirements:**
- Your OpenSearch document must have a `geo_point` field
- Internet access to reach the postcodes.io API
- The `requests` library (automatically installed with this package)

## License

MIT
