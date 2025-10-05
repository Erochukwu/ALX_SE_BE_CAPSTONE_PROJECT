"""
vendors/urls.py

Defines REST API endpoints for vendors and sheds.
"""

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ShedViewSet

router = DefaultRouter()
router.register(r'sheds', ShedViewSet, basename='shed')

urlpatterns = [
    path('', include(router.urls)),
]
