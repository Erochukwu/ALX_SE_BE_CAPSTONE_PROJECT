# orders/views.py
"""
API views for managing preorders in the TradeFair project.

Features:
- Customers can create/view/update/delete their own preorders.
- Vendors can confirm or cancel preorders for their own products.
- Customers can initiate Paystack payments for preorders and check payment status.
- All operations use JSON responses for API consistency.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.conf import settings
from paystackapi.transaction import Transaction
from .models import Preorder
from .serializers import PreorderSerializer
from payments.models import Payment


class IsPreorderOwnerOrVendor(permissions.BasePermission):
    """
    Custom permission for Preorder model.

    Allows customers to manage their own preorders.
    Allows vendors to view/confirm/cancel preorders for their products.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Args:
            request: HTTP request.
            view: View handling the request.
            obj: Preorder instance.

        Returns:
            bool: True if permission granted, False otherwise.
        """
        user = request.user

        # Vendors can view or confirm preorders for their own products
        if hasattr(user, "vendor_profile") and obj.product.shed.vendor.user == user:
            return True

        # Customers can manage their own preorders
        if hasattr(user, "customer_profile") and obj.customer.user == user:
            return True

        return False


class PreorderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing preorders.

    Features:
        - List/retrieve preorders (vendors see their products' preorders, customers see their own).
        - Create preorders (customers only).
        - Update/delete preorders (customers only).
        - Confirm/cancel preorders (vendors or customers).
        - Initiate payments (customers only).
        - Check payment status (customers only).

    Permissions:
        - IsAuthenticated for all actions.
        - IsPreorderOwnerOrVendor for object-level access.
    """
    serializer_class = PreorderSerializer
    queryset = Preorder.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPreorderOwnerOrVendor]

    def get_queryset(self):
        """
        Filter preorders based on user role.

        Vendors see all preorders for their products.
        Customers see their own preorders.
        Non-authenticated users see none.

        Returns:
            QuerySet: Filtered Preorder objects.
        """
        user = self.request.user

        # Vendor: show all preorders