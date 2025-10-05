"""
products/urls.py

Defines REST API endpoints for vendor products.
"""

# products/urls.py
from django.urls import path
from .views import ProductViewSet

# Use DRF router for ProductViewSet instead of manually adding unrelated URLs
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = router.urls
