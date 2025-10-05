"""
orders/views.py

API views for managing preorders.
- Customers can create/view/update/delete their own preorders.
- Vendors can confirm or cancel preorders for their own products.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Preorder
from .serializers import PreorderSerializer


class IsPreorderOwnerOrVendor(permissions.BasePermission):
    """
    Custom permission:
    - Customers can view/manage their own preorders.
    - Vendors can view/confirm preorders made for their products.
    """
    def has_object_permission(self, request, view, obj):
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
    Handles CRUD operations for Preorder model.
    """
    serializer_class = PreorderSerializer
    queryset = Preorder.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsPreorderOwnerOrVendor]

    def get_queryset(self):
        user = self.request.user

        # Vendor: show all preorders for their products
        if hasattr(user, "vendor_profile"):
            return Preorder.objects.filter(product__shed__vendor__user=user)

        # Customer: show their own preorders
        if hasattr(user, "customer_profile"):
            return Preorder.objects.filter(customer__user=user)

        return Preorder.objects.none()

    def perform_create(self, serializer):
        user = self.request.user

        # Ensure only customers can create preorders
        if not hasattr(user, "customer_profile"):
            raise PermissionDenied("Only customers can create preorders.")

        product = serializer.validated_data["product"]
        serializer.save(
            customer=user.customer_profile,
            vendor=product.shed.vendor.user  # Automatically assign vendor
        )

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
    def confirm(self, request, pk=None):
        """
        PATCH /api/preorders/{id}/confirm/
        Allows a vendor to confirm a preorder for their product.
        """
        preorder = self.get_object()

        # Ensure only vendor of the product can confirm
        if preorder.vendor != request.user:
            raise PermissionDenied("You are not authorized to confirm this preorder.")

        preorder.status = "confirmed"
        preorder.save()
        return Response({"detail": "Preorder confirmed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        """
        PATCH /api/preorders/{id}/cancel/
        Allows vendor or customer to cancel preorder.
        """
        preorder = self.get_object()
        user = request.user

        if preorder.vendor != user and preorder.customer.user != user:
            raise PermissionDenied("You are not authorized to cancel this preorder.")

        preorder.status = "cancelled"
        preorder.save()
        return Response({"detail": "Preorder cancelled successfully."}, status=status.HTTP_200_OK)
