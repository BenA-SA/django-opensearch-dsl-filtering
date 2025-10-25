"""
Book models for testing.
"""
from django.db import models


class Book(models.Model):
    """Book model for testing filtering functionality."""

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pages = models.IntegerField()
    in_stock = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for Book model."""

        ordering = ["-created_at"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        """String representation of Book."""
        return f"{self.title} by {self.author}"
