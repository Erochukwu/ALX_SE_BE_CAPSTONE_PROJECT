"""
followers/models.py

Defines models for managing vendor followers.
- Follow: represents a customer following a vendor.
"""

from django.db import models
from users.models import CustomerProfile
from vendors.models import VendorProfile


class Follow(models.Model):
    """
    Represents a follow relationship between a customer and a vendor.
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name="following")
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("customer", "vendor")
        ordering = ["-created_at"]  # Optional, to show newest follows first

    def __str__(self):
        return f"{self.customer.user.username} follows {self.vendor.user.username}"
