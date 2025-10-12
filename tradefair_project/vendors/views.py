# vendors/views.py
"""
API views for vendor-related operations in the TradeFair project.

Handles shed management and vendor dashboard functionality.
Includes:
- ShedViewSet: CRUD for sheds with filtering by domain or vendor, collage uploads, and payment status.
- VendorDashboardViewSet: Aggregates products, preorders, followers, and shed information for vendors.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .models import Shed
from .serializers import ShedSerializer
from products.models import Product
from orders.models import Preorder
from followers.models import Follow
from payments.models import VendorPayment


class IsVendorOrAdmin(permissions.BasePermission):
    """
    Custom permission for Shed model.

    Allows read access to all users (including anonymous).
    Restricts write access (create/update/delete) to the shed's vendor or superusers.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Args:
            request: HTTP request.
            view: View handling the request.
            obj: Shed instance.

        Returns:
            bool: True if permission granted, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        if request.user.is_superuser:
            return True
        return hasattr(request.user, "vendor_profile") and obj.vendor.user == request.user


class ShedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing sheds.

    Features:
        - List/retrieve sheds (all users, including anonymous).
        - Create/update/delete sheds (vendors only).
        - Filter by domain or vendor ID.
        - Upload/update product collage.
        - Check payment status.
    """
    serializer_class = ShedSerializer
    queryset = Shed.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsVendorOrAdmin]
    parser_classes = [MultiPartParser, FormParser]  # Support file uploads for collages

    def get_queryset(self):
        """
        Filter sheds by domain or vendor ID.

        Query params:
            domain: Filter by domain code (e.g., 'CL' for Clothing).
            vendor: Filter by vendor ID.

        Example:
            /api/vendors/sheds/?domain=CL
            /api/vendors/sheds/?vendor=2

        Returns:
            QuerySet: Filtered Shed objects.
        """
        queryset = Shed.objects.all()
        domain = self.request.query_params.get('domain')
        vendor_id = self.request.query_params.get('vendor')
        if domain:
            queryset = queryset.filter(domain=domain)
        if vendor_id:
            queryset = queryset.filter(vendor__id=vendor_id)
        return queryset

    def perform_create(self, serializer):
        """
        Create a new shed for the authenticated vendor.

        Args:
            serializer: ShedSerializer instance with validated data.

        Raises:
            PermissionError: If the user is not a vendor.
        """
        user = self.request.user
        if not hasattr(user, 'vendor_profile'):
            raise PermissionError("Only vendors can create sheds.")
        serializer.save(vendor=user.vendor_profile)

    @action(detail=False, methods=['get'], url_path='available')
    def available_sheds(self, request):
        """
        GET /api/vendors/sheds/available/

        Returns available shed slots by domain.

        Returns:
            Response: JSON with domain-wise shed availability (total, used, available).
        """
        data = {}
        for code, label in Shed.DOMAIN_CHOICES:
            total = 100
            used = Shed.objects.filter(domain=code).count()
            remaining = total - used
            data[label] = {
                "total": total,
                "used": used,
                "available": remaining
            }
        return Response(data)

    @action(detail=True, methods=['post', 'put', 'patch'], url_path='collage')
    def update_collage(self, request, pk=None):
        """
        POST/PUT/PATCH /api/vendors/sheds/{id}/collage/

        Uploads or updates a shed's product collage.

        Args:
            request: HTTP request with file data.
            pk: Shed ID.

        Returns:
            Response: Success message with collage URL or error if no file provided.
        """
        shed = self.get_object()
        if not request.user.is_superuser and (not hasattr(request.user, "vendor_profile") or shed.vendor != request.user.vendor_profile):
            raise PermissionDenied("You can only update collage for your own shed.")
        if 'collage' in request.FILES:
            shed.collage = request.FILES['collage']
            shed.save()
            return Response({
                "message": "Collage updated successfully",
                "collage_url": shed.collage.url if shed.collage else None
            })
        else:
            return Response({"error": "No collage file provided"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='payment-status')
    def payment_status(self, request, pk=None):
        """
        GET /api/vendors/sheds/{id}/payment-status/

        Returns payment status for a shed.

        Args:
            request: HTTP request.
            pk: Shed ID.

        Returns:
            Response: JSON with payment status, reference, and secured status.
        """
        shed = self.get_object()
        try:
            vendor_payment = VendorPayment.objects.get(shed=shed)
            return Response({
                "secured": shed.secured,
                "payment_status": vendor_payment.status,
                "reference": vendor_payment.reference
            })
        except VendorPayment.DoesNotExist:
            return Response({
                "secured": shed.secured,
                "payment_status": "no_payment",
                "message": "No payment initiated yet"
            })


class VendorDashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for vendor dashboard.

    Aggregates products, preorders, followers, and shed information for the authenticated vendor.
    """
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request):
        """
        GET /api/vendors/dashboard/

        Returns aggregated dashboard data for the vendor.

        Args:
            request: HTTP request.

        Returns:
            Response: JSON with shed details, stats (products, preorders, followers), payment status, and action URLs.
        """
        user = request.user
        if not hasattr(user, 'vendor_profile'):
            raise PermissionDenied("Only vendors can access dashboard.")
        
        vendor = user.vendor_profile
        try:
            shed = Shed.objects.get(vendor=vendor)
        except Shed.DoesNotExist:
            return Response({
                "error": "No shed allocated to this vendor"
            }, status=status.HTTP_404_NOT_FOUND)

        # Aggregate data
        products = Product.objects.filter(shed=shed).count()
        preorders = Preorder.objects.filter(product__shed=shed).select_related('product').all()
        followers_count = Follow.objects.filter(vendor=vendor).count()
        
        # Get payment status
        payment_status = {}
        try:
            vendor_payment = VendorPayment.objects.get(shed=shed)
            payment_status = {
                "status": vendor_payment.status,
                "reference": vendor_payment.reference,
                "secured": shed.secured
            }
        except VendorPayment.DoesNotExist:
            payment_status = {"status": "no_payment", "secured": shed.secured}

        dashboard_data = {
            "shed": {
                "id": shed.id,
                "shed_number": shed.shed_number,
                "name": shed.name,
                "domain": shed.get_domain_display(),
                "secured": shed.secured,
                "collage_url": shed.collage.url if shed.collage else None,
                "location": shed.location
            },
            "stats": {
                "products_count": products,
                "preorders_count": Preorder.objects.filter(product__shed=shed).count(),
                "followers_count": followers_count
            },
            "payment_status": payment_status,
            "actions": {
                "upload_collage_url": f"/api/vendors/sheds/{shed.id}/collage/",
                "secure_shed_url": f"/api/payments/initiate-shed/{shed.id}/" if not shed.secured else None,
                "products_url": "/api/products/",
                "preorders_url": f"/api/preorders/?shed={shed.id}"
            }
        }
        
        return Response(dashboard_data)