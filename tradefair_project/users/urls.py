from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationViewSet, VendorRegistrationViewSet, UserLoginViewSet

router = DefaultRouter()
router.register(r'users/register', UserRegistrationViewSet, basename='user-registration')
router.register(r'vendors/register', VendorRegistrationViewSet, basename='vendor-registration')
router.register(r'login', UserLoginViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
]