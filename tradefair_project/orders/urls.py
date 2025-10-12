# orders/urls.py
"""
URL configuration for preorder-related API endpoints in the TradeFair project.

Defines REST API routes for the PreorderViewSet, enabling CRUD operations for preorders,
as well as custom actions for confirming, canceling, initiating payments, and checking payment status.
Supports customer preordering and order status checking, and vendor preorder management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreorderViewSet

# Initialize DRF router for automatic URL routing
router = DefaultRouter()
# Register PreorderViewSet with empty prefix (maps to /api/preorders/)
router.register(r'', PreorderViewSet, basename='preorder')

# Expose router URLs for inclusion in main urls.py
urlpatterns = [
    path('', include(router.urls)),  # Includes list, retrieve, create, update, delete, and custom actions
]