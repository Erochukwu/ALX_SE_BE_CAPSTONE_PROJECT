"""
Tests for the payments app in the TradeFair project.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from vendors.models import Shed
from users.models import VendorProfile, CustomerProfile
from .models import Payment, VendorPayment
from orders.models import Preorder
from products.models import Product
from unittest.mock import patch
from django.urls import reverse

User = get_user_model()

class PaymentModelTests(TestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123', email='customer@example.com'
        )
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user)
        self.vendor_user = User.objects.create_user(
            username='vendor', password='testpass123', email='vendor@example.com', is_vendor=True
        )
        self.vendor = VendorProfile.objects.create(
            user=self.vendor_user, business_name='Test Boutique'
        )
        self.shed = Shed.objects.create(
            vendor=self.vendor, shed_number='SH001', name='Test Shed', domain='CL'
        )
        self.product = Product.objects.create(
            shed=self.shed,
            vendor=self.vendor_user,
            name='Test Product',
            description='A test product description',
            price=100.00,
            quantity=10
        )
        self.preorder = Preorder.objects.create(
            customer=self.customer_profile,
            vendor=self.vendor_user,
            product=self.product,
            quantity=1,
            status='pending'
        )
        self.payment = Payment.objects.create(
            preorder=self.preorder, amount=100.00, reference='PAY123', status='pending'
        )

    def test_payment_creation(self):
        """Test Payment model creation and relationships."""
        self.assertEqual(self.payment.preorder, self.preorder)
        self.assertEqual(self.payment.amount, 100.00)
        self.assertEqual(self.payment.reference, 'PAY123')
        self.assertEqual(self.payment.status, 'pending')

class VendorPaymentModelTests(TestCase):
    def setUp(self):
        self.vendor_user = User.objects.create_user(
            username='vendor', password='testpass123', email='vendor@example.com', is_vendor=True
        )
        self.vendor = VendorProfile.objects.create(
            user=self.vendor_user, business_name='Test Boutique'
        )
        self.shed = Shed.objects.create(
            vendor=self.vendor, shed_number='SH001', name='Test Shed', domain='CL'
        )
        self.vendor_payment = VendorPayment.objects.create(
            shed=self.shed, amount=500.00, reference='VPAY123', status='pending'
        )

    def test_vendor_payment_creation(self):
        """Test VendorPayment model creation and relationships."""
        self.assertEqual(self.vendor_payment.shed, self.shed)
        self.assertEqual(self.vendor_payment.amount, 500.00)
        self.assertEqual(self.vendor_payment.reference, 'VPAY123')
        self.assertEqual(self.vendor_payment.status, 'pending')

class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_user = User.objects.create_user(
            username='customer', password='testpass123', email='customer@example.com'
        )
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user)
        self.vendor_user = User.objects.create_user(
            username='vendor', password='testpass123', email='vendor@example.com', is_vendor=True
        )
        self.vendor_token = Token.objects.create(user=self.vendor_user)
        self.vendor = VendorProfile.objects.create(
            user=self.vendor_user, business_name='Test Boutique'
        )
        self.shed = Shed.objects.create(
            vendor=self.vendor, shed_number='SH001', name='Test Shed', domain='CL'
        )
        self.product = Product.objects.create(
            shed=self.shed,
            vendor=self.vendor_user,
            name='Test Product',
            description='A test product description',
            price=100.00,
            quantity=10
        )
        self.preorder = Preorder.objects.create(
            customer=self.customer_profile,
            vendor=self.vendor_user,
            product=self.product,
            quantity=1,
            status='pending'
        )

    @patch('paystackapi.transaction.Transaction.initialize')
    def test_initiate_shed_payment(self, mock_initialize):
        """Test initiating shed payment with Paystack."""
        mock_initialize.return_value = {
            'status': True,
            'data': {
                'authorization_url': 'https://paystack.com/pay/test',
                'reference': 'VPAY123'
            }
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.vendor_token.key}')
        response = self.client.post(
            reverse('initiate_shed_payment', args=[self.shed.id]),
            {'amount': 500.00}
        )
        print("Response data:", response.data)  # Debug output
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['reference'], 'VPAY123')

    @patch('paystackapi.transaction.Transaction.verify')
    def test_paystack_webhook_success_vendor_payment(self, mock_verify):
        """Test Paystack webhook for successful vendor payment."""
        mock_verify.return_value = {
            'status': True,
            'data': {'status': 'success', 'amount': 50000}
        }
        vendor_payment = VendorPayment.objects.create(
            shed=self.shed, amount=500.00, reference='VPAY123', status='pending'
        )
        response = self.client.post(
            '/api/payments/webhook/',
            {
                'event': 'charge.success',
                'data': {'reference': 'VPAY123', 'status': 'success', 'amount': 50000}
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vendor_payment.refresh_from_db()
        self.assertEqual(vendor_payment.status, 'success')
        self.shed.refresh_from_db()
        self.assertTrue(self.shed.secured)