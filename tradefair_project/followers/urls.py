"""
followers/urls.py

Defines API routes for FollowViewSet.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FollowViewSet

router = DefaultRouter()
router.register(r"", FollowViewSet, basename="follower")

urlpatterns = [
    path('', include(router.urls)),
]