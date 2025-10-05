# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SignupView, LoginView,
    VendorProfileViewSet, CustomerProfileViewSet
)

router = DefaultRouter()
router.register(r'vendors', VendorProfileViewSet, basename='vendor')
router.register(r'customers', CustomerProfileViewSet, basename='customer')

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]

