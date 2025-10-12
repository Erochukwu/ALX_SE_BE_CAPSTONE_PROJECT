# vendors/tests.py
"""
Tests for vendors app models and views in the TradeFair project.
Covers Shed model and ShedViewSet.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from users.models import VendorProfile
from vendors.models import Shed

class ShedModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.user, business_name='Test Boutique')
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', domain='CL')

    def test_shed_creation(self):
        """Test Shed model creation and shed_number generation."""
        self.assertEqual(self.shed.name, 'Clothing Shed')
        self.assertEqual(self.shed.domain, 'CL')
        self.assertEqual(self.shed.shed_number, 'CL001')
        self.assertEqual(self.shed.vendor, self.vendor)

class ShedViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.user, business_name='Test Boutique')
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.token = Token.objects.create(user=self.user)
        self.non_vendor = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')

    def test_list_sheds_unauthenticated(self):
        """Test that unauthenticated users can list sheds."""
        response = self.client.get('/api/vendors/sheds/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_shed_authenticated_vendor(self):
        """Test that authenticated vendors can create sheds."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post('/api/vendors/sheds/', {
            'name': 'New Shed',
            'domain': 'EL'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['shed_number'], 'EL001')

    def test_create_shed_non_vendor(self):
        """Test that non-vendors cannot create sheds."""
        non_vendor_token = Token.objects.create(user=self.non_vendor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {non_vendor_token.key}')
        response = self.client.post('/api/vendors/sheds/', {
            'name': 'Invalid Shed',
            'domain': 'CL'
        })
        self.assertEqual(response.status_code, 403)
