"""
vendors/views.py

ViewSets for vendor-related operations.
Includes:
- ShedViewSet: CRUD for sheds with filtering by domain or vendor.
"""

from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Shed
from .serializers import ShedSerializer


class IsVendorOrAdmin(permissions.BasePermission):
    """
    Custom permission:
    - Vendors can manage their own sheds.
    - Admins can access everything.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return hasattr(request.user, "vendor_profile") and obj.vendor.user == request.user


class ShedViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Sheds.
    Features:
        - List sheds by domain or vendor.
        - Retrieve shed details.
        - Create, update, and delete sheds.
    """
    serializer_class = ShedSerializer
    queryset = Shed.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsVendorOrAdmin]

    def get_queryset(self):
        """
        Allow filtering by domain or vendor.
        Example:
            /api/vendors/sheds/?domain=FB
            /api/vendors/sheds/?vendor=2
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
        Automatically assign the vendor from the logged-in user.
        Only vendors can create sheds for themselves.
        """
        user = self.request.user
        if not hasattr(user, 'vendor_profile'):
            raise PermissionError("Only vendors can create sheds.")
        serializer.save(vendor=user.vendor_profile)

    @action(detail=False, methods=['get'], url_path='available')
    def available_sheds(self, request):
        """
        Custom endpoint:
        Returns a list of available shed slots by domain.
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
