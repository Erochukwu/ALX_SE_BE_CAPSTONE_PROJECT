"""
API views for the orders app in the TradeFair project.

Provides RESTful endpoints for managing preorders, including CRUD operations and
custom actions for confirming, canceling, and processing payments via Paystack.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
from paystackapi.transaction import Transaction
from .models import Preorder
from .serializers import PreorderSerializer
from payments.models import Payment
from users.models import CustomerProfile, VendorProfile

class IsCustomer(permissions.BasePermission):
    """
    Custom permission to restrict actions to users with a CustomerProfile.
    """
    def has_permission(self, request, view):
        """
        Check if the authenticated user has a CustomerProfile.

        Args:
            request: The HTTP request object.
            view: The view being accessed.

        Returns:
            bool: True if the user has a CustomerProfile, False otherwise.
        """
        return hasattr(request.user, 'customer_profile')

class IsPreorderOwnerOrVendor(permissions.BasePermission):
    """
    Custom permission for preorder objects.

    Allows customers to manage their own preorders and vendors to manage preorders
    for their products.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions for a preorder.

        Args:
            request: The HTTP request object.
            view: The view being accessed.
            obj: The Preorder instance.

        Returns:
            bool: True if the user is the preorder's customer or vendor, False otherwise.
        """
        user = request.user
        if hasattr(user, 'vendor_profile') and obj.product.shed.vendor.user == user:
            return True
        if hasattr(user, 'customer_profile') and obj.customer.user == user:
            return True
        return False

class PreorderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing preorders in the TradeFair project.

    Provides endpoints for:
    - Listing and retrieving preorders (filtered by user role).
    - Creating preorders (customers only).
    - Updating and deleting preorders (customers or vendors, per permissions).
    - Confirming or canceling preorders (vendors or customers).
    - Initiating and checking payment status (customers only).

    Permissions:
    - IsAuthenticated and IsCustomer for create, list, retrieve, initiate_payment, check_payment_status.
    - IsAuthenticated and IsPreorderOwnerOrVendor for update, delete, confirm, cancel.
    """
    serializer_class = PreorderSerializer
    queryset = Preorder.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Assign permissions based on the requested action.

        Returns:
            list: Permission classes applicable to the current action.
        """
        if self.action in ['create', 'list', 'retrieve', 'initiate_payment', 'check_payment_status']:
            return [permissions.IsAuthenticated(), IsCustomer()]
        elif self.action in ['update', 'partial_update', 'destroy', 'confirm', 'cancel']:
            return [permissions.IsAuthenticated(), IsPreorderOwnerOrVendor()]
        return super().get_permissions()

    def get_queryset(self):
        """
        Filter preorders based on the authenticated user's role.

        Vendors see preorders for their products, customers see their own preorders,
        and other users see none.

        Returns:
            QuerySet: Filtered Preorder objects.
        """
        user = self.request.user
        if hasattr(user, 'vendor_profile'):
            return Preorder.objects.filter(product__shed__vendor=user.vendor_profile)
        elif hasattr(user, 'customer_profile'):
            return Preorder.objects.filter(customer=user.customer_profile)
        return Preorder.objects.none()

    @swagger_auto_schema(
        request_body=PreorderSerializer,
        responses={
            201: PreorderSerializer,
            400: openapi.Response('Invalid data'),
            403: openapi.Response('Not authorized')
        }
    )
    def perform_create(self, serializer):
        """
        Create a new preorder with the authenticated user's CustomerProfile.

        Args:
            serializer: The PreorderSerializer instance with validated data.
        """
        serializer.save(customer=self.request.user.customer_profile)

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Preorder confirmed', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)})),
            403: openapi.Response('Not authorized'),
            404: openapi.Response('Preorder not found')
        }
    )
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

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Preorder cancelled', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)})),
            403: openapi.Response('Not authorized'),
            404: openapi.Response('Preorder not found')
        }
    )
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

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Payment initiated', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'authorization_url': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: openapi.Response('Payment initialization failed'),
            403: openapi.Response('Not authorized'),
            404: openapi.Response('Preorder not found')
        }
    )
    @action(detail=True, methods=['post'], url_path='initiate_payment')
    def initiate_payment(self, request, pk=None):
        """
        Allow a customer to initiate a payment for a preorder via Paystack.

        Args:
            request: The HTTP request object.
            pk: The primary key of the preorder to pay for.

        Returns:
            Response: HTTP 200 with payment authorization URL, or HTTP 400/403/404 if invalid, unauthorized, or not found.
        """
        try:
            preorder = self.get_object()
            if preorder.customer != self.request.user.customer_profile:
                return Response({"detail": "Not authorized to initiate payment for this preorder"}, status=status.HTTP_403_FORBIDDEN)
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

    @swagger_auto_schema(
        responses={
            200: openapi.Response('Payment status', openapi.Schema(type=openapi.TYPE_OBJECT, properties={'status': openapi.Schema(type=openapi.TYPE_STRING)})),
            400: openapi.Response('Payment verification failed'),
            403: openapi.Response('Not authorized'),
            404: openapi.Response('Preorder or payment not found')
        }
    )
    @action(detail=True, methods=['get'], url_path='check_payment_status')
    def check_payment_status(self, request, pk=None):
        """
        Allow a customer to check the payment status of a preorder.

        Args:
            request: The HTTP request object.
            pk: The primary key of the preorder to check.

        Returns:
            Response: HTTP 200 with payment status, or HTTP 400/403/404 if invalid, unauthorized, or not found.
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