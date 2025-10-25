"""
Books app configuration.
"""

from django.apps import AppConfig


class BooksConfig(AppConfig):
    """Books app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "test_project.books"
