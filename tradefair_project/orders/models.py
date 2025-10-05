"""
orders/models.py

Defines order-related models.
- Preorder: Customers preordering products.
"""

from django.db import models
from django.conf import settings
from users.models import CustomerProfile
from products.models import Product


class Preorder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    """
    Represents a preorder made by a customer for a product.
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="preorders")
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_preorders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="preorders")
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Preorder: {self.customer.user.username} -> {self.product.name} ({self.status})"
