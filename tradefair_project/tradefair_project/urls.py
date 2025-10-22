"""
Main URL configuration for the TradeFair project.

Routes URLs to views for admin, authentication, API endpoints, and Swagger/ReDoc
documentation. Supports token-based authentication and media file serving in
development mode.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework import permissions  # Added import
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configure Swagger schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="TradeFair API",
        default_version='v1',
        description="RESTful API for the TradeFair marketplace, enabling customers to follow vendors, browse products, place preorders, and process payments via Paystack.",
        terms_of_service="https://www.tradefair.com/terms/",
        contact=openapi.Contact(email="support@tradefair.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls, name='admin'),
    # API endpoints for apps
    path('api-auth/', include('rest_framework.urls')),
    path('api/users/', include('users.urls')),
    # path('api/vendors/', include('vendors.urls')),
    # path('api/products/', include('products.urls')),
    # path('api/preorders/', include('orders.urls')),
    # path('api/followers/', include('followers.urls')),
    # path('api/payments/', include('payments.urls')),
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/\?format=openapi$', schema_view.without_ui(cache_timeout=0), name='schema-openapi'),
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)