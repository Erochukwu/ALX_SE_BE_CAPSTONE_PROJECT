"""
URLs for the vendors app in the TradeFair project.

Defines API routes for managing products in a vendor's shed.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]