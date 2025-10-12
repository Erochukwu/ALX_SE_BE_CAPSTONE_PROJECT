"""
payments/models.py

Defines payment-related models.
- Payment: Represents payments for preorders.
- VendorPayment: Represents payments for vendor shed allocation.
"""

from django.db import models
from orders.models import Preorder
from users.models import VendorProfile  # Changed from vendors.models.Vendor
from vendors.models import Shed  # Keep this as is

class Payment(models.Model):
    """
    Represents a payment linked to a preorder.
    """
    preorder = models.OneToOneField(Preorder, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True, null=True)  # For Paystack
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("completed", "Completed"), ("failed", "Failed")],
        default="pending"
    )

    def __str__(self):
        return f"Payment for {self.preorder.product.name} - {self.status}"

class VendorPayment(models.Model):
    """
    Represents a payment for vendor shed allocation/security.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='shed_payments')  # Changed to VendorProfile
    shed = models.OneToOneField(Shed, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shed Payment {self.reference} - {self.status}"