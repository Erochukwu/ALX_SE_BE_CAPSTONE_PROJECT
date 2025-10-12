# payments/tests.py
"""
Tests for payments app models and views in the TradeFair project.
Covers Payment and VendorPayment models, initiate_shed_payment, and paystack_webhook views.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from unittest.mock import patch
from users.models import VendorProfile, CustomerProfile
from vendors.models import Shed
from products.models import Product
from orders.models import Preorder
from payments.models import Payment, VendorPayment

class PaymentModelTests(TestCase):
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
        self.payment = Payment.objects.create(
            preorder=self.preorder,
            amount=40.00,
            reference='test_ref_123',
            status='pending'
        )

    def test_payment_creation(self):
        """Test Payment model creation and relationships."""
        self.assertEqual(self.payment.preorder, self.preorder)
        self.assertEqual(self.payment.amount, 40.00)
        self.assertEqual(self.payment.reference, 'test_ref_123')
        self.assertEqual(self.payment.status, 'pending')

class VendorPaymentModelTests(TestCase):
    def setUp(self):
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.vendor_payment = VendorPayment.objects.create(
            vendor=self.vendor,
            shed=self.shed,
            amount=10000.00,
            reference='shed_ref_123',
            status='pending'
        )

    def test_vendor_payment_creation(self):
        """Test VendorPayment model creation and relationships."""
        self.assertEqual(self.vendor_payment.vendor, self.vendor)
        self.assertEqual(self.vendor_payment.shed, self.shed)
        self.assertEqual(self.vendor_payment.amount, 10000.00)
        self.assertEqual(self.vendor_payment.reference, 'shed_ref_123')
        self.assertEqual(self.vendor_payment.status, 'pending')

class PaymentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.vendor_user = User.objects.create_user(username='vendor', email='vendor@example.com', password='testpass123')
        self.vendor = VendorProfile.objects.create(user=self.vendor_user, business_name='Test Boutique')
        self.shed = Shed.objects.create(vendor=self.vendor, name='Clothing Shed', shed_number='CL001', domain='CL')
        self.client.login(username='vendor', password='testpass123')

    @patch('paystackapi.transaction.Transaction.initialize')
    def test_initiate_shed_payment(self, mock_initialize):
        """Test initiating shed payment with Paystack."""
        mock_initialize.return_value = {
            'status': True,
            'data': {'authorization_url': 'https://paystack.com/mock-url', 'reference': 'shed_1_1'}
        }
        response = self.client.post(reverse('initiate_shed_payment', args=[self.shed.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to Paystack
        self.assertTrue(VendorPayment.objects.filter(reference='shed_1_1', status='pending').exists())

    @patch('paystackapi.transaction.Transaction.initialize')
    def test_initiate_shed_payment_failure(self, mock_initialize):
        """Test shed payment initiation failure."""
        mock_initialize.return_value = {'status': False, 'message': 'Payment error'}
        response = self.client.post(reverse('initiate_shed_payment', args=[self.shed.id]))
        self.assertEqual(response.status_code, 200)  # Renders error.html
        self.assertFalse(VendorPayment.objects.exists())

    def test_paystack_webhook_success_vendor_payment(self):
        """Test Paystack webhook for successful vendor payment."""
        payload = {
            'event': 'charge.success',
            'data': {'reference': 'shed_ref_123'}
        }
        vendor_payment = VendorPayment.objects.create(
            vendor=self.vendor,
            shed=self.shed,
            amount=10000.00,
            reference='shed_ref_123',
            status='pending'
        )
        response = self.client.post(reverse('paystack_webhook'), data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        vendor_payment.refresh_from_db()
        self.shed.refresh_from_db()
        self.assertEqual(vendor_payment.status, 'success')
        self.assertTrue(self.shed.secured)

    def test_paystack_webhook_success_preorder_payment(self):
        """Test Paystack webhook for successful preorder payment."""
        customer_user = User.objects.create_user(username='customer', email='customer@example.com', password='testpass123')
        customer = CustomerProfile.objects.create(user=customer_user)
        product = Product.objects.create(
            shed=self.shed,
            vendor=self.vendor_user,
            name='T-Shirt',
            price=20.00,
            quantity=50
        )
        preorder = Preorder.objects.create(
            customer=customer,
            vendor=self.vendor_user,
            product=product,
            quantity=2,
            status='pending'
        )
        payment = Payment.objects.create(
            preorder=preorder,
            amount=40.00,
            reference='preorder_ref_123',
            status='pending'
        )
        payload = {
            'event': 'charge.success',
            'data': {'reference': 'preorder_ref_123'}
        }
        response = self.client.post(reverse('paystack_webhook'), data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'completed')

    def test_initiate_shed_payment_get(self):
        """Test GET request for shed payment initiation form."""
        response = self.client.get(reverse('initiate_shed_payment', args=[self.shed.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payments/initiate_shed.html')
        self.assertContains(response, self.shed.name)
