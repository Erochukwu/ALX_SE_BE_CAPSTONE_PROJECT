# users/tests.py
"""
Tests for users app models and views in the TradeFair project.
Covers VendorProfile, CustomerProfile models, and VendorProfileViewSet.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from users.models import VendorProfile, CustomerProfile

class UserModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')

    def test_user_creation(self):
        """Test User model creation."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')

class VendorProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.user, business_name='Test Boutique')

    def test_vendor_profile_creation(self):
        """Test VendorProfile model creation and relationship."""
        self.assertEqual(self.vendor.business_name, 'Test Boutique')
        self.assertEqual(self.vendor.user, self.user)

class CustomerProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        self.customer = CustomerProfile.objects.create(user=self.user)

    def test_customer_profile_creation(self):
        """Test CustomerProfile model creation."""
        self.assertEqual(self.customer.user, self.user)

class VendorProfileViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.user, business_name='Test Boutique')
        self.token = Token.objects.create(user=self.user)
        self.customer = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')

    def test_list_vendors_unauthenticated(self):
        """Test that unauthenticated users can list vendors."""
        response = self.client.get('/api/users/vendors/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_vendor_unauthenticated(self):
        """Test that unauthenticated users can retrieve vendor details."""
        response = self.client.get(f'/api/users/vendors/{self.vendor.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['business_name'], 'Test Boutique')

    def test_create_vendor_authenticated(self):
        """Test that authenticated users can create vendor profiles."""
        new_user = User.objects.create_user(username='newvendor', email='new@example.com', password='testpass123')
        token = Token.objects.create(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.post('/api/users/vendors/', {'business_name': 'New Shop'})
        self.assertEqual(response.status_code, 201)
