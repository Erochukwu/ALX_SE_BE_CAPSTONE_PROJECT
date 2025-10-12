# tradefair_project/urls.py
"""
Main URL configuration for the TradeFair project.

Routes URLs to views for admin, authentication, and all six apps (users, vendors, products, orders, followers, payments).
Supports token-based authentication, Swagger documentation, and media file serving in development.
"""

from django.conf import settings  # Access Django settings (e.g., DEBUG, MEDIA_URL)
from django.conf.urls.static import static  # Serve static/media files in development
from django.contrib import admin  # Django admin interface
from django.urls import path, include  # Path for URL patterns, include for app URLs
from rest_framework.authtoken.views import obtain_auth_token  # Token-based authentication endpoint
from users.views import RegisterView  # User registration view
from drf_yasg.views import get_schema_view  # Swagger schema view
from drf_yasg import openapi  # OpenAPI spec for Swagger

# Schema view for Swagger/ReDoc documentation (public access)
schema_view = get_schema_view(
    openapi.Info(
        title="TradeFair API",  # API title
        default_version='v1',  # API version
        description="API for TradeFair project: vendors, sheds, products, preorders, followers, payments.",  # Description
    ),
    public=True,  # Allow unauthenticated access to docs
)

# Main URL patterns
urlpatterns = [
    # -------------------------
    # Admin & Core URLs
    # -------------------------
    path('admin/', admin.site.urls, name='admin'),  # Django admin interface

    # -------------------------
    # Authentication URLs
    # -------------------------
    path('api/token/', obtain_auth_token, name='token_obtain'),  # Token authentication endpoint

    # -------------------------
    # User Registration
    # -------------------------
    path('api/register/', RegisterView.as_view(), name='register'),  # User registration

    # -------------------------
    # API Endpoints
    # -------------------------
    path('api-auth/', include('rest_framework.urls')),  # DRF browsable API login/logout
    path('api/users/', include('users.urls')),  # User-related routes (vendors, customers)
    path('api/vendors/', include('vendors.urls')),  # Vendor-related routes (sheds, dashboard)
    path('api/products/', include('products.urls')),  # Product-related routes
    path('api/preorders/', include('orders.urls')),  # Preorder-related routes
    path('api/followers/', include('followers.urls')),  # Follower-related routes
    path('api/payments/', include('payments.urls')),  # Payment-related routes

    # -------------------------
    # Documentation
    # -------------------------
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # ReDoc alternative
]

# -------------------------
# Serve media files during development
# -------------------------
if settings.DEBUG:  # Only in development (DEBUG=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media (images, collages)