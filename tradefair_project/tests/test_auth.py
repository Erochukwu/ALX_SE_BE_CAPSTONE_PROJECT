# tests/test_auth.py
from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username="testuser", password="pass123")
        self.assertFalse(user.is_vendor)
        self.assertTrue(user.check_password("pass123"))

    def test_create_vendor(self):
        user = User.objects.create_user(username="vendor1", password="pass123", is_vendor=True)
        self.assertTrue(user.is_vendor)
        self.assertEqual(user.username, "vendor1")
