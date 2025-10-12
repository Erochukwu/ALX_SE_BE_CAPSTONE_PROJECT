# products/views.py
"""
API views for managing products within the TradeFair project.

Features:
- Vendors can create, update, and delete their own products.
- Public users (customers/guests) have read-only access to view products.
- Supports filtering by shed, vendor, category (shed.domain), and searching by name or description.
"""

from rest_framework import viewsets, permissions, filters
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer


class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for Product model.

    Allows read access to all users (including anonymous).
    Restricts write access (create/update/delete) to the vendor owning the product's shed.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Args:
            request: HTTP request.
            view: View handling the request.
            obj: Product instance.

        Returns:
            bool: True if permission granted, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        if not hasattr(request.user, 'vendor_profile'):
            return False
        return obj.shed.vendor.user == request.user


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products.

    Features:
        - List/retrieve products (all users, including anonymous).
        - Create/update/delete products (vendors only, for their own sheds).
        - Filter by shed ID (?shed=3), vendor ID (?vendor=2), category (?category=CL).
        - Search by product name or description (?search=phone).

    Permissions:
        - Public read-only access via IsAuthenticatedOrReadOnly.
        - Vendor-specific write access via IsVendorOwnerOrReadOnly.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsVendorOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['shed', 'shed__vendor__id', 'shed__domain']  # Filter by shed, vendor, category
    search_fields = ['name', 'description']  # Example: ?search=laptop

    def get_queryset(self):
        """
        Filter products based on user role.

        Vendors see only their own products (via their sheds).
        Public users (customers/guests) see all products.
        Supports additional filtering via query parameters (shed, vendor, category).

        Returns:
            QuerySet: Filtered Product objects.
        """
        user = self.request.user
        if hasattr(user, 'vendor_profile'):
            return Product.objects.filter(shed__vendor__user=user)
        return Product.objects.all()

    def perform_create(self, serializer):
        """
        Create a new product for the authenticated vendor's shed.

        Args:
            serializer: ProductSerializer instance with validated data.

        Raises:
            PermissionDenied: If user is not a vendor or shed is not owned by the vendor.
        """
        user = self.request.user
        if not hasattr(user, 'vendor_profile'):
            raise PermissionDenied("Only vendors can add products.")

        shed_id = self.request.data.get("shed")
        if not shed_id:
            raise PermissionDenied("Please specify the shed this product belongs to.")

        # Verify the shed belongs to the vendor
        try:
            shed = user.vendor_profile.sheds.get(id=shed_id)
        except Product.shed.field.related_model.DoesNotExist:
            raise PermissionDenied("You cannot assign a product to a shed you do not own.")

        # Save the product, linking to the shed
        serializer.save(shed=shed)