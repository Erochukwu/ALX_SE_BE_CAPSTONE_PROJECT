import pytest
from django.contrib.auth import get_user_model
CustomUser = get_user_model()

from rest_framework.test import APIClient
from rest_framework import status

@pytest.mark.django_db
class TestAuth:
    def setup_method(self):
        self.client = APIClient()

    def test_user_registration_and_login(self):
        # Register user
        response = self.client.post("/api/register/", {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code in [201, 200]

        # Login
        response = self.client.post("/api/token/", {
            "username": "testuser",
            "password": "password123"
        })
        assert response.status_code == 200
        assert "token" in response.data
