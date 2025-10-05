"""
orders/urls.py

API routes for preorder management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PreorderViewSet

router = DefaultRouter()
router.register(r'', PreorderViewSet, basename='preorder')

urlpatterns = [
    path('', include(router.urls)),
]
