# orders/tests.py
"""
Tests for orders app models and views in the TradeFair project.
Covers Preorder model and PreorderViewSet, including payment actions.
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from users.models import VendorProfile, CustomerProfile
from vendors.models import Shed
from products.models import Product
from orders.models import Preorder
from unittest.mock import patch

class PreorderModelTests(TestCase):
    def setUp(self):
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.customer = CustomerProfile.objects.create(user=self.customer_user)
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.product = Product.objects.create(
            shed=self.shed,
            vendor=self.vendor_user,
            name='T-Shirt',
            price=20.00,
            quantity=50
        )
        self.preorder = Preorder.objects.create(
            customer=self.customer,
            vendor=self.vendor_user,
            product=self.product,
            quantity=2,
            status='pending'
        )

    def test_preorder_creation(self):
        """Test Preorder model creation and relationships."""
        self.assertEqual(self.preorder.customer, self.customer)
        self.assertEqual(self.preorder.vendor, self.vendor_user)
        self.assertEqual(self.preorder.product, self.product)
        self.assertEqual(self.preorder.quantity, 2)
        self.assertEqual(self.preorder.status, 'pending')

class PreorderViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.customer = CustomerProfile.objects.create(user=self.customer_user)
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.product = Product.objects.create(
            shed=self.shed,
            vendor=self.vendor_user,
            name='T-Shirt',
            price=20.00,
            quantity=50
        )
        self.preorder = Preorder.objects.create(
            customer=self.customer,
            vendor=self.vendor_user,
            product=self.product,
            quantity=2,
            status='pending'
        )
        self.vendor_token = Token.objects.create(user=self.vendor_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

    def test_list_preorders_customer(self):
        """Test that customers can list their own preorders."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.get('/api/preorders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_preorder_customer(self):
        """Test that customers can create preorders."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.post('/api/preorders/', {
            'product': self.product.id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, 201)

    def test_create_preorder_non_customer(self):
        """Test that non-customers cannot create preorders."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.vendor_token.key}')
        response = self.client.post('/api/preorders/', {
            'product': self.product.id,
            'quantity': 3
        })
        self.assertEqual(response.status_code, 403)

    def test_confirm_preorder_vendor(self):
        """Test that vendors can confirm preorders for their products."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.vendor_token.key}')
        response = self.client.patch(f'/api/preorders/{self.preorder.id}/confirm/')
        self.assertEqual(response.status_code, 200)
        self.preorder.refresh_from_db()
        self.assertEqual(self.preorder.status, 'confirmed')

    @patch('paystackapi.transaction.Transaction.initialize')
    def test_initiate_payment_customer(self, mock_initialize):
        """Test that customers can initiate payment (mock Paystack response)."""
        mock_initialize.return_value = {
            'status': True,
            'data': {'authorization_url': 'https://paystack.com/mock-url', 'reference': 'mock_ref'}
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.post(f'/api/preorders/{self.preorder.id}/initiate_payment/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['authorization_url'], 'https://paystack.com/mock-url')
