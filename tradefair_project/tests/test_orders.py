# tests/test_orders.py
"""
Tests for preorder system.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_setup import TestSetup

class OrdersTests(APITestCase, TestSetup):
    """Test customer/vendor preorder interactions."""

    def setUp(self):
        """Create users, vendor, shed, product, and authenticate."""
        self.customer_user, self.customer_profile = self.create_customer()
        self.vendor_user, self.vendor_profile, self.shed = self.create_vendor()
        self.product = self.create_product(vendor_profile=self.vendor_profile, shed=self.shed)

        # Authenticate customer by default
        self.client.force_authenticate(user=self.customer_user)

    def test_customer_can_create_preorder(self):
        """Customer can create a preorder for a product."""
        url = reverse("preorder-list")  # DRF router
        data = {
            "customer": self.customer_profile.id,
            "vendor": self.vendor_user.id,
            "product": self.product.id,
            "quantity": 2
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_vendor_can_view_preorders(self):
        """Vendor can view preorders made to them."""
        # First, create a preorder as customer
        url = reverse("preorder-list")
        self.client.post(url, {"customer": self.customer_profile.id, "vendor": self.vendor_user.id, "product": self.product.id, "quantity": 1})

        # Authenticate as vendor
        self.client.force_authenticate(user=self.vendor_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
