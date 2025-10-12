"""
URL configuration for tradefair_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from users.views import RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # -------------------------
    # Admin & Core URLs
    # -------------------------
    path('admin/', admin.site.urls),

    # -------------------------
    # API Endpoints
    # -------------------------
    path('api/auth/', include('rest_framework.urls')),  # DRF browsable API login/logout
    path('api/users/', include('users.urls')),          # Custom Users API routes
    path('api/vendors/', include('vendors.urls')),
    path('api/products/', include('products.urls')),
    path('api/preorders/', include('orders.urls')),
    path("api/followers/", include("followers.urls")),
    path('api/', include('users.urls')),
    path('api/payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# -------------------------
# Serve media files during development
# -------------------------
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
