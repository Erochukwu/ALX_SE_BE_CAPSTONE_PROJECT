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
from users.models import CustomerProfile, VendorProfile

class IsCustomer(permissions.BasePermission):
    """
    Custom permission to ensure only users with a CustomerProfile can perform actions.
    """
    def has_permission(self, request, view):
        """
        Check if the user has a CustomerProfile.

        Args:
            request: The HTTP request object.
            view: The view being accessed.

        Returns:
            bool: True if the user has a CustomerProfile, False otherwise.
        """
        return hasattr(request.user, 'customer_profile')

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
            request: The HTTP request object.
            view: The view being accessed.
            obj: Preorder instance.

        Returns:
            bool: True if permission granted, False otherwise.
        """
        user = request.user
        # Vendors can view or confirm preorders for their own products
        if hasattr(user, 'vendor_profile') and obj.product.shed.vendor.user == user:
            return True
        # Customers can manage their own preorders
        if hasattr(user, 'customer_profile') and obj.customer.user == user:
            return True
        return False

class PreorderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing preorders.

    Features:
        - List/retrieve preorders (vendors see their products' preorders, customers see their own).
        - Create preorders (customers only).
        - Update/delete preorders (customers only, with IsPreorderOwnerOrVendor).
        - Confirm/cancel preorders (vendors or customers).
        - Initiate payments and check payment status (customers only).

    Permissions:
        - IsAuthenticated and IsCustomer for create, list, retrieve, initiate_payment, check_payment_status.
        - IsAuthenticated and IsPreorderOwnerOrVendor for update, delete, confirm, cancel.
    """
    serializer_class = PreorderSerializer
    queryset = Preorder.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Assign permissions based on the action.

        Args:
            None

        Returns:
            list: List of permission classes for the current action.
        """
        if self.action in ['create', 'list', 'retrieve', 'initiate_payment', 'check_payment_status']:
            return [permissions.IsAuthenticated(), IsCustomer()]
        elif self.action in ['update', 'partial_update', 'destroy', 'confirm', 'cancel']:
            return [permissions.IsAuthenticated(), IsPreorderOwnerOrVendor()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter preorders based on user role.

        Vendors see all preorders for their products.
        Customers see their own preorders.
        Non-authenticated users or users without a profile see none.

        Returns:
            QuerySet: Filtered Preorder objects.
        """
        user = self.request.user
        if hasattr(user, 'vendor_profile'):
            return Preorder.objects.filter(product__shed__vendor=user.vendor_profile)
        elif hasattr(user, 'customer_profile'):
            return Preorder.objects.filter(customer=user.customer_profile)
        return Preorder.objects.none()

    def perform_create(self, serializer):
        """
        Create a new preorder, automatically setting the customer to the authenticated user's CustomerProfile.

        Args:
            serializer: The PreorderSerializer instance with validated data.
        """
        serializer.save(customer=self.request.user.customer_profile)

    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm(self, request, pk=None):
        """
        Allow a vendor to confirm a preorder for their product.

        Args:
            request: The HTTP request object.
            pk: The primary key of the preorder to confirm.

        Returns:
            Response: HTTP 200 with updated status, or HTTP 403/404 if unauthorized or not found.
        """
        try:
            preorder = self.get_object()
            if preorder.vendor != self.request.user:
                return Response({"detail": "Not authorized to confirm this preorder"}, status=status.HTTP_403_FORBIDDEN)
            preorder.status = 'confirmed'
            preorder.save()
            return Response({'status': 'confirmed'}, status=status.HTTP_200_OK)
        except Preorder.DoesNotExist:
            return Response({"detail": "Preorder not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Allow a vendor or customer to cancel a preorder.

        Args:
            request: The HTTP request object.
            pk: The primary key of the preorder to cancel.

        Returns:
            Response: HTTP 200 with updated status, or HTTP 403/404 if unauthorized or not found.
        """
        try:
            preorder = self.get_object()
            if preorder.vendor != self.request.user and preorder.customer != self.request.user.customer_profile:
                return Response({"detail": "Not authorized to cancel this preorder"}, status=status.HTTP_403_FORBIDDEN)
            preorder.status = 'cancelled'
            preorder.save()
            return Response({'status': 'cancelled'}, status=status.HTTP_200_OK)
        except Preorder.DoesNotExist:
            return Response({"detail": "Preorder not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='initiate_payment')
    def initiate_payment(self, request, pk=None):
        """
        Allow a customer to initiate payment for a preorder.

        Args:
            request: The HTTP request object.
            pk: The primary key of the preorder to pay for.

        Returns:
            Response: HTTP 200 with payment details, or HTTP 403/404 if unauthorized or not found.
        """
        try:
            preorder = self.get_object()
            if preorder.customer != self.request.user.customer_profile:
                return Response({"detail": "Not authorized to initiate payment for this preorder"}, status=status.HTTP_403_FORBIDDEN)
            # Initialize Paystack transaction
            amount = int(preorder.product.price * preorder.quantity * 100)  # Convert to kobo
            response = Transaction.initialize(
                reference=f"preorder_{preorder.id}_{int(request.user.id)}",
                amount=amount,
                email=request.user.email
            )
            if response['status']:
                Payment.objects.create(
                    preorder=preorder,
                    amount=amount / 100,
                    reference=response['data']['reference'],
                    status='pending'
                )
                return Response({'authorization_url': response['data']['authorization_url']}, status=status.HTTP_200_OK)
            return Response({'detail': 'Payment initialization failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Preorder.DoesNotExist:
            return Response({"detail": "Preorder not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='check_payment_status')
    def check_payment_status(self, request, pk=None):
        """
        Allow a customer to check the payment status of a preorder.

        Args:
            request: The HTTP request object.
            pk: The primary key of the preorder to check.

        Returns:
            Response: HTTP 200 with payment status, or HTTP 403/404 if unauthorized or not found.
        """
        try:
            preorder = self.get_object()
            if preorder.customer != self.request.user.customer_profile:
                return Response({"detail": "Not authorized to check payment status for this preorder"}, status=status.HTTP_403_FORBIDDEN)
            payment = Payment.objects.get(preorder=preorder)
            response = Transaction.verify(reference=payment.reference)
            if response['status']:
                payment.status = response['data']['status']
                payment.save()
                return Response({'status': payment.status}, status=status.HTTP_200_OK)
            return Response({'detail': 'Payment verification failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Preorder.DoesNotExist:
            return Response({"detail": "Preorder not found"}, status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)