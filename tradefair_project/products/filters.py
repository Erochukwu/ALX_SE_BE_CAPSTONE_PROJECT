"""
products/filters.py

Defines custom filtering logic for Product model.
Allows filtering by:
    - Shed ID
    - Minimum and maximum price
"""

import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Product
        fields = ["shed", "min_price", "max_price"]
