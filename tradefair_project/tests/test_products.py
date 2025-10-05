# tests/test_products.py
"""
Tests for product management.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_setup import TestSetup

class ProductsTests(APITestCase, TestSetup):
    """Tests for product creation and viewing."""

    def setUp(self):
        """Create vendor, shed, and authenticate."""
        self.vendor_user, self.vendor_profile, self.shed = self.create_vendor()
        self.client.force_authenticate(user=self.vendor_user)

    def test_vendor_can_create_product(self):
        """Vendor can create a product in their shed."""
        url = reverse("product-list")  # Make sure your DRF router for products is 'product'
        data = {
            "vendor": self.vendor_user.id,
            "shed": self.shed.id,
            "name": "New Product",
            "price": 200,
            "quantity": 5
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
