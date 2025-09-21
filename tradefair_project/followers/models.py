"""
followers/models.py

Defines the Follow model for customers following vendors.
"""

from django.db import models
from users.models import CustomerProfile, VendorProfile


class Follow(models.Model):
    """
    Represents a follow relationship between a customer and a vendor.
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="follows")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "vendor")  # Prevent duplicate follows

    def __str__(self):
        return f"{self.customer.user.username} follows {self.vendor.business_name}"

