# users/urls.py
"""
URL configuration for the 'users' app.

This file defines API endpoints related to user registration, authentication, 
and user profile management (for vendors and customers). It uses Django REST Framework 
viewsets and JWT authentication.

Endpoints:
1. /api/register/       - User registration (SignupView)
2. /api/token/          - JWT login (TokenObtainPairView)
3. /api/token/refresh/  - JWT token refresh (TokenRefreshView)
4. /api/vendors/        - Vendor profile CRUD via VendorProfileViewSet
5. /api/customers/      - Customer profile CRUD via CustomerProfileViewSet
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignupView, LoginView, RegisterView, VendorProfileViewSet, CustomerProfileViewSet

# -------------------------
# DRF Router for Profiles
# -------------------------
# DefaultRouter automatically generates URLs for CRUD operations for viewsets
router = DefaultRouter()
router.register(r'vendors', VendorProfileViewSet, basename='vendor')
router.register(r'customers', CustomerProfileViewSet, basename='customer')

# -------------------------
# URL Patterns
# -------------------------
urlpatterns = [
    # Include DRF router URLs
    path('', include(router.urls)),
    # Signup endpoint for creating vendor/customer profiles
    path('signup/', SignupView.as_view(), name='signup'),
    # Login endpoint for token authentication
    path('login/', LoginView.as_view(), name='login'),
    # Registration endpoint for creating users
    path('register/', RegisterView.as_view(), name='register'),
]
