"""
products/models.py

Defines product-related models.
- Product: Item listed by vendors.
"""

from django.db import models
from vendors.models import Shed


class Product(models.Model):
    """
    Product listed under a vendor’s shed.
    """
    shed = models.ForeignKey(Shed, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return self.name

