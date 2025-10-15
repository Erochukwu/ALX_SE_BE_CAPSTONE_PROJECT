"""
Tests for the followers app in the TradeFair project.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from users.models import VendorProfile, CustomerProfile
from .models import Follow

User = get_user_model()

class FollowModelTests(TestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123', email='customer@example.com'
        )
        CustomerProfile.objects.create(user=self.customer_user)
        self.vendor_user = User.objects.create_user(
            username='vendor', password='testpass123', email='vendor@example.com', is_vendor=True
        )
        self.vendor = VendorProfile.objects.create(
            user=self.vendor_user, business_name='Test Boutique', description='Test shop'
        )
        self.follow = Follow.objects.create(customer=self.customer_user, vendor=self.vendor)

    def test_follow_creation(self):
        """Test Follow model creation and relationships."""
        self.assertEqual(self.follow.customer.username, 'customer')
        self.assertEqual(self.follow.vendor.business_name, 'Test Boutique')
        self.assertTrue(self.follow.created_at)

    def test_unique_together_constraint(self):
        """Test that customer cannot follow the same vendor twice."""
        with self.assertRaises(Exception):
            Follow.objects.create(customer=self.customer_user, vendor=self.vendor)

class FollowViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123', email='customer@example.com'
        )
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user)
        self.customer_token = Token.objects.create(user=self.customer_user)
        self.vendor_user = User.objects.create_user(
            username='vendor', password='testpass123', email='vendor@example.com', is_vendor=True
        )
        self.vendor_token = Token.objects.create(user=self.vendor_user)
        self.vendor = VendorProfile.objects.create(
            user=self.vendor_user, business_name='Test Boutique', description='Test shop'
        )
        self.vendor2_user = User.objects.create_user(
            username='vendor2', password='testpass123', email='vendor2@example.com', is_vendor=True
        )
        self.vendor2 = VendorProfile.objects.create(
            user=self.vendor2_user, business_name='Test Boutique 2', description='Test shop 2'
        )
        self.follow = Follow.objects.create(customer=self.customer_user, vendor=self.vendor)

    def test_create_follow_authenticated_customer(self):
        """Test that authenticated customers can follow vendors."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.post('/api/followers/follow/', {'vendor': self.vendor2.id})
        print("Response data:", response.data)  # Debug output
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_follow_non_customer(self):
        """Test that non-customers (e.g., vendors) cannot follow."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.vendor_token.key}')
        response = self.client.post('/api/followers/follow/', {'vendor': self.vendor.id})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_follows_authenticated_customer(self):
        """Test that authenticated customers can list their follows."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get('/api/followers/follow/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_follows_unauthenticated(self):
        """Test that unauthenticated users cannot list follows."""
        response = self.client.get('/api/followers/follow/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unfollow_authenticated_customer(self):
        """Test that customers can unfollow vendors."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.delete(f'/api/followers/follow/{self.follow.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unfollow_non_existent(self):
        """Test unfollowing a non-existent follow relationship."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.delete('/api/followers/follow/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)