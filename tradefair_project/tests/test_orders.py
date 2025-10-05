import pytest
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

from rest_framework.test import APIClient
from users.models import CustomerProfile, VendorProfile
from products.models import Product
from orders.models import Preorder

@pytest.mark.django_db
class TestPreorders:
    def setup_method(self):
        self.client = APIClient()

        # Create vendor & customer
        self.vendor_user = CustomUser.objects.create_user(username="vendor1", password="pass123")
        self.vendor_profile = VendorProfile.objects.create(user=self.vendor_user, business_name="Shop1")

        self.customer_user = CustomUser.objects.create_user(username="customer1", password="pass123")
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user, address="123 Street")

        # Create product
        self.product = Product.objects.create(
            name="Tomatoes", price=10, quantity=20, vendor=self.vendor_user
        )

    def test_customer_can_create_preorder(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post("/api/preorders/", {
            "product": self.product.id,
            "quantity": 3
        })
        assert response.status_code in [201, 200]
        assert Preorder.objects.count() == 1

    def test_vendor_can_view_preorders(self):
        preorder = Preorder.objects.create(
            customer=self.customer_profile,
            vendor=self.vendor_user,
            product=self.product,
            quantity=2,
        )
        self.client.force_authenticate(user=self.vendor_user)
        response = self.client.get("/api/preorders/")
        assert response.status_code == 200
        assert len(response.data) >= 1
