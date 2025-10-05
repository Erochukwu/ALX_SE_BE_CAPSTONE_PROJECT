import pytest
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

from rest_framework.test import APIClient
from users.models import VendorProfile

@pytest.mark.django_db
class TestProducts:
    def setup_method(self):
        self.client = APIClient()
        self.vendor_user = CustomUser.objects.create_user(username="vendor1", password="pass123")
        self.vendor_profile = VendorProfile.objects.create(user=self.vendor_user, business_name="Vendor1")

    def test_vendor_can_create_product(self):
        self.client.force_authenticate(user=self.vendor_user)
        response = self.client.post("/api/products/", {
            "name": "Bananas",
            "description": "Fresh fruit",
            "price": 2.5,
            "quantity": 50,
        })
        assert response.status_code in [201, 200]
