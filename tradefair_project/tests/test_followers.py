import pytest
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

from rest_framework.test import APIClient
from users.models import CustomerProfile, VendorProfile
from followers.models import Follow

@pytest.mark.django_db
class TestFollowers:
    def setup_method(self):
        self.client = APIClient()
        self.customer_user = CustomUser.objects.create_user(username="cust1", password="pass123")
        self.customer_profile = CustomerProfile.objects.create(user=self.customer_user, address="City")

        self.vendor_user = CustomUser.objects.create_user(username="vend1", password="pass123")
        self.vendor_profile = VendorProfile.objects.create(user=self.vendor_user, business_name="Vendor A")

    def test_customer_can_follow_vendor(self):
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post("/api/followers/", {"vendor": self.vendor_profile.id})
        assert response.status_code in [201, 200]
        assert Follow.objects.count() == 1

    def test_customer_can_unfollow_vendor(self):
        Follow.objects.create(customer=self.customer_profile, vendor=self.vendor_profile)
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.post("/api/followers/unfollow/", {"vendor_id": self.vendor_profile.id})
        assert response.status_code == 200
        assert Follow.objects.count() == 0
