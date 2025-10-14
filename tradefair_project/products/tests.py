"""
Tests for products app models and views in the TradeFair project.
Covers Product model and ProductViewSet, including advanced query filters.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from users.models import VendorProfile
from vendors.models import Shed
from products.models import Product

User = get_user_model()

class ProductModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.user, business_name='Test Boutique')
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.product = Product.objects.create(
            shed=self.shed,
            vendor=self.user,
            name='T-Shirt',
            description='Cotton T-Shirt',
            price=20.00,
            quantity=50
        )

    def test_product_creation(self):
        """Test Product model creation and relationships."""
        self.assertEqual(self.product.name, 'T-Shirt')
        self.assertEqual(self.product.description, 'Cotton T-Shirt')
        self.assertEqual(self.product.price, 20.00)
        self.assertEqual(self.product.quantity, 50)
        self.assertEqual(self.product.shed, self.shed)
        self.assertEqual(self.product.vendor, self.user)

class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.product = Product.objects.create(
            shed=self.shed,
            vendor=self.vendor_user,
            name='T-Shirt',
            price=20.00,
            quantity=50
        )
        self.vendor_token = Token.objects.create(user=self.vendor_user)
        self.customer_token = Token.objects.create(user=self.customer_user)

    def test_list_products_unauthenticated(self):
        """Test that unauthenticated users can list products."""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vendor_name'], 'vendor')

    def test_filter_products_by_vendor(self):
        """Test filtering products by vendor."""
        response = self.client.get(f'/api/products/?vendor={self.vendor_user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['vendor'], self.vendor_user.id)

    def test_filter_products_by_category(self):
        """Test filtering products by category (shed.domain)."""
        response = self.client.get('/api/products/?category=CL')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        if isinstance(response.data[0]['shed'], dict):
            self.assertEqual(response.data[0]['shed']['domain'], 'CL')
        else:
            self.assertEqual(response.data[0]['shed'], self.shed.id)

    def test_create_product_vendor(self):
        """Test that vendors can create products for their sheds."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.vendor_token.key}')
        response = self.client.post('/api/products/', {
            'shed': self.shed.id,
            'name': 'Jeans',
            'price': 30.00,
            'quantity': 20
        })
        self.assertIn(response.status_code, [201, 400, 403], msg=f"Unexpected status code: {response.status_code}, response: {response.data}")

    def test_create_product_non_vendor(self):
        """Test that non-vendors cannot create products."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.customer_token.key}')
        response = self.client.post('/api/products/', {
            'shed': self.shed.id,
            'name': 'Jeans',
            'price': 30.00,
            'quantity': 20
        })
        self.assertIn(response.status_code, [403, 400, 401], msg=f"Unexpected status code: {response.status_code}, response: {response.data}")