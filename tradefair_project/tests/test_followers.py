# tests/test_followers.py
"""
Tests for follower system: following/unfollowing vendors.
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .test_setup import TestSetup

class FollowersTests(APITestCase, TestSetup):
    """Tests following/unfollowing vendors."""

    def setUp(self):
        """Create customer, vendor, shed, and authenticate."""
        self.customer_user, self.customer_profile = self.create_customer()
        # Updated to unpack 3 values
        self.vendor_user, self.vendor_profile, self.shed = self.create_vendor()

        # Authenticate customer
        self.client.force_authenticate(user=self.customer_user)

    def test_customer_can_follow_vendor(self):
        """Customer can follow a vendor."""
        url = reverse("follow-list")  # router registered as 'follow'
        data = {"vendor": self.vendor_profile.id}
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_customer_can_unfollow_vendor(self):
        """Customer can unfollow a vendor."""
        # First follow
        url = reverse("follow-list")
        self.client.post(url, {"vendor": self.vendor_profile.id})

        # Then unfollow
        unfollow_url = reverse("follow-detail", args=[self.vendor_profile.id])
        response = self.client.delete(unfollow_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
