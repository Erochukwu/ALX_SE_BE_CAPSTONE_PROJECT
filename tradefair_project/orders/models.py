"""
orders/models.py

Defines order-related models.
- Preorder: Customers preordering products.
"""

from django.db import models
from users.models import CustomerProfile
from products.models import Product


class Preorder(models.Model):
    """
    Represents a preorder made by a customer for a product.
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="preorders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="preorders")
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"Preorder: {self.customer.user.username} -> {self.product.name}"
