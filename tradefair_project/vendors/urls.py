"""
vendors/urls.py

Defines REST API endpoints for vendors and sheds.
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ShedViewSet, VendorDashboardViewSet

router = DefaultRouter()
router.register(r'sheds', ShedViewSet, basename='shed')
router.register(r'dashboard', VendorDashboardViewSet, basename='dashboard', viewset=VendorDashboardViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
