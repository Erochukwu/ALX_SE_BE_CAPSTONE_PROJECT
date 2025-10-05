# tests/test_setup.py
"""
Test setup helper functions for creating users, vendors, sheds, and products.
This file provides reusable methods for all test cases.
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Product
from vendors.models import Shed
from users.models import VendorProfile, CustomerProfile

User = get_user_model()


class TestSetup:
    """Reusable setup helper for creating test data."""

    def create_customer(self, username="customer", password="pass1234"):
        """Creates a customer user and profile."""
        user = User.objects.create_user(username=username, password=password)
        profile = CustomerProfile.objects.create(user=user)
        return user, profile

    def create_vendor(self, username="vendor", password="pass1234", business_name="Vendor Business"):
        """
        Creates a vendor user, profile, and a shed.
        Returns: user, profile, shed
        """
        user = User.objects.create_user(username=username, password=password, is_vendor=True)
        profile = VendorProfile.objects.create(user=user, business_name=business_name)
        shed = Shed.objects.create(vendor=profile, domain="FB", name=f"{business_name} Shed")
        return user, profile, shed

    def create_product(self, vendor_profile, shed, name="Test Product", price=100.0, quantity=10):
        """Creates a product tied to a vendor's shed."""
        product = Product.objects.create(
            vendor=vendor_profile.user,
            shed=shed,
            name=name,
            price=price,
            quantity=quantity,
        )
        return product

    def get_api_client(self):
        """Returns a DRF APIClient instance."""
        return APIClient()
