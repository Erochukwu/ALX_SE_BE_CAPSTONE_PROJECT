"""
products/views.py

API views for managing products within the TradeFair project.

Features:
- Vendors can CREATE, UPDATE, and DELETE only their own products.
- Anyone (public/customers) can view available products.
- Supports search and filtering by name, price range, and shed.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Vendors can manage (create/edit/delete) only their own products.
    - Everyone else (customers/guests) can read products.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only requests
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check vendor ownership
        if not hasattr(request.user, 'vendor_profile'):
            return False

        return obj.shed.vendor.user == request.user


class ProductViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD operations for the Product model.

    Permissions:
        - Authenticated vendors can create and manage their own products.
        - Public/customers have read-only access.

    Filtering and Searching:
        - Filter by shed ID (?shed=3)
        - Filter by price range (?min_price=10&max_price=200)
        - Search by product name or description (?search=phone)
    """

    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsVendorOwnerOrReadOnly]

    # Enable filtering and searching
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    filterset_fields = ['shed']  # Example: ?shed=1
    search_fields = ['name', 'description']  # Example: ?search=laptop

    def get_queryset(self):
        """
        Limit vendors to view only their own products when logged in.
        Public users see all available products.
        """
        user = self.request.user
        if hasattr(user, 'vendor_profile'):
            return Product.objects.filter(shed__vendor__user=user)
        return Product.objects.all()

    def perform_create(self, serializer):
        """
        Assigns product to the correct vendor shed.
        Ensures that only vendors can create products.
        """
        user = self.request.user

        if not hasattr(user, 'vendor_profile'):
            raise PermissionDenied("Only vendors can add products.")

        shed_id = self.request.data.get("shed")
        if not shed_id:
            raise PermissionDenied("Please specify the shed this product belongs to.")

        serializer.save()
