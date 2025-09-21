"""
payments/models.py

Defines payment-related models.
- Payment: Represents payments for preorders.
"""

from django.db import models
from orders.models import Preorder


class Payment(models.Model):
    """
    Represents a payment linked to a preorder.
    """
    preorder = models.OneToOneField(Preorder, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending"
    )

    def __str__(self):
        return f"Payment for {self.preorder.product.name} - {self.status}"

