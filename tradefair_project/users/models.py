"""
users/models.py

This module defines the custom user model and related profiles.
- CustomUser: Base user model for authentication.
- VendorProfile: Extends CustomUser for vendor-specific details.
- CustomerProfile: Extends CustomUser for customer-specific details.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom user model extending Django’s AbstractUser.
    Fields:
        - username, email, password (inherited)
        - is_vendor: Boolean flag (True if the user is a vendor)
    """
    is_vendor = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class VendorProfile(models.Model):
    """
    Profile for vendor users.
    Related to CustomUser via OneToOneField.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="vendor_profile")
    business_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Vendor: {self.business_name}"


class CustomerProfile(models.Model):
    """
    Profile for customer users.
    Related to CustomUser via OneToOneField.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="customer_profile")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Customer: {self.user.username}"
