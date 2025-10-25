"""
OpenSearch documents for Book model.
"""

from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry

from .models import Book


@registry.register_document
class BookDocument(Document):
    """OpenSearch document for Book model."""

    title = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    author = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    isbn = fields.KeywordField()
    publication_date = fields.DateField()
    price = fields.FloatField()
    pages = fields.IntegerField()
    in_stock = fields.BooleanField()
    description = fields.TextField()

    class Index:
        """Index settings."""

        name = "books"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        """Django model configuration."""

        model = Book
        fields = []  # We're manually defining all fields above

        # Fields to include when indexing
        related_models = []
