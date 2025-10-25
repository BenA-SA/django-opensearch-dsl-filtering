"""
Admin configuration for books app.
"""
from django.contrib import admin

from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Admin interface for Book model."""

    list_display = (
        "title",
        "author",
        "isbn",
        "publication_date",
        "price",
        "in_stock",
    )
    list_filter = ("in_stock", "publication_date")
    search_fields = ("title", "author", "isbn")
    date_hierarchy = "publication_date"
