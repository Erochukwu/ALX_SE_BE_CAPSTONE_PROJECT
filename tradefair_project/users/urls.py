from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationViewSet,
    VendorRegistrationViewSet,
    UserLoginViewSet,
    UserProfileViewSet,
    UserDeleteViewSet,
    paystack_payment_callback,
    mock_paystack_callback,
    test_redis
)

router = DefaultRouter()
router.register(r'users/register', UserRegistrationViewSet, basename='user-registration')
router.register(r'vendors/register', VendorRegistrationViewSet, basename='vendor-registration')
router.register(r'login', UserLoginViewSet, basename='login')
router.register(r'profile', UserProfileViewSet, basename='user-profile')
router.register(r'delete', UserDeleteViewSet, basename='user-delete')

urlpatterns = [
    path('', include(router.urls)),
    path('payment-callback/', paystack_payment_callback, name='paystack-payment-callback'),
    path('mock-paystack-callback/', mock_paystack_callback, name='mock-paystack-callback'),
    path('test-redis/', test_redis, name='test-redis'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]