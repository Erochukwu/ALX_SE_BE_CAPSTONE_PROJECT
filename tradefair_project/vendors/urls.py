# vendors/urls.py
"""
URL configuration for the vendors app.

Defines API endpoints for managing sheds and accessing the vendor dashboard.
Uses Django REST Framework's DefaultRouter for automatic URL generation.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShedViewSet, VendorDashboardViewSet

router = DefaultRouter()
router.register(r'sheds', ShedViewSet, basename='shed')  # Shed management (GET, POST, etc.)
router.register(r'dashboard', VendorDashboardViewSet, basename='dashboard')  # Vendor dashboard (GET)

urlpatterns = [
    path('', include(router.urls)),  # Include all router-generated URLs
]