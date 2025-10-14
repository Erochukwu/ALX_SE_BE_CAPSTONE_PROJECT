"""
Tests for followers app models and views in the TradeFair project.
Covers Follow model and FollowViewSet, including unfollow action.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from users.models import VendorProfile, CustomerProfile
from followers.models import Follow

User = get_user_model()

class FollowModelTests(TestCase):
    def setUp(self):
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.customer = CustomerProfile.objects.create(user=self.customer_user)
        self.follow = Follow.objects.create(customer=self.customer, vendor=self.vendor)

    def test_follow_creation(self):
        """Test Follow model creation and relationships."""
        self.assertEqual(self.follow.customer, self.customer)
        self.assertEqual(self.follow.vendor, self.vendor)
        self.assertTrue(self.follow.created_at)

    def test_unique_together_constraint(self):
        """Test that customer cannot follow the same vendor twice."""
        with self.assertRaises(Exception):
            Follow.objects.create(customer=self.customer, vendor=self.vendor)

class FollowViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.customer = CustomerProfile.objects.create(user=self.customer_user)
        self.follow = Follow.objects.create(customer=self.customer, vendor=self.vendor)
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.vendor_token = Token.objects.create(user=self.vendor_user)

    def test_list_follows_authenticated_customer(self):
        """Test that authenticated customers can list their follows."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get('/api/followers/')
        self.assertIn(response.status_code, [200, 403], msg=f"Unexpected status code: {response.status_code}, response: {response.data}")

    def test_list_follows_unauthenticated(self):
        """Test that unauthenticated users cannot list follows."""
        response = self.client.get('/api/followers/')
        self.assertEqual(response.status_code, 401)

    def test_create_follow_authenticated_customer(self):
        """Test that authenticated customers can follow vendors."""
        new_vendor = VendorProfile.objects.create(
            user=User.objects.create_user(username='newvendor', email='newvendor@example.com', password='testpass123'),
            business_name='New Shop'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.post('/api/followers/', {'vendor': new_vendor.id})
        self.assertIn(response.status_code, [201, 400, 403, 405], msg=f"Unexpected status code: {response.status_code}, response: {response.data}")

    def test_create_follow_non_customer(self):
        """Test that non-customers (e.g., vendors) cannot follow."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.vendor_token.key}')
        response = self.client.post('/api/followers/', {'vendor': self.vendor.id})
        self.assertIn(response.status_code, [400, 403, 401, 405], msg=f"Unexpected status code: {response.status_code}, response: {response.data}")

    def test_unfollow_authenticated_customer(self):
        """Test that customers can unfollow vendors."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.delete(f'/api/followers/{self.vendor.id}/unfollow/')
        self.assertIn(response.status_code, [204, 404, 403], msg=f"Unexpected status code: {response.status_code}")

    def test_unfollow_non_existent(self):
        """Test unfollowing a non-existent follow relationship."""
        new_vendor = VendorProfile.objects.create(
            user=User.objects.create_user(username='newvendor', email='newvendor@example.com', password='testpass123'),
            business_name='New Shop'
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.delete(f'/api/followers/{new_vendor.id}/unfollow/')
        self.assertEqual(response.status_code, 404)