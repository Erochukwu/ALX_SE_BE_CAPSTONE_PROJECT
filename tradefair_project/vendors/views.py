"""
Views for the vendors app in the TradeFair project.

Handles API endpoints for managing products in a vendor's shed.
"""

from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter
from .models import Shed, Product
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products in a vendor's shed.

    Allows vendors to create, retrieve, update, delete, and list products in their shed.
    Only the authenticated vendor who owns the shed can perform these actions.
    """
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Skip logic during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()  # Return empty queryset for schema
        vendor_profile = self.request.user.vendor_profile
        return Product.objects.filter(shed__vendor=vendor_profile)

    @extend_schema(
        summary="List all products in the vendor's shed",
        description="Retrieves a list of all products in the authenticated vendor's shed.",
        responses={200: ProductSerializer(many=True)},
        examples=[
            OpenApiExample(
                "List products response",
                value=[
                    {
                        "id": 1,
                        "shed": 1,
                        "name": "Smartphone",
                        "description": "Latest 5G smartphone",
                        "price": "150000.00",
                        "image": None,
                        "created_at": "2025-10-24T15:00:00Z",
                        "updated_at": "2025-10-24T15:00:00Z"
                    },
                    {
                        "id": 2,
                        "shed": 1,
                        "name": "Headphones",
                        "description": "Wireless noise-canceling headphones",
                        "price": "25000.00",
                        "image": None,
                        "created_at": "2025-10-24T15:01:00Z",
                        "updated_at": "2025-10-24T15:01:00Z"
                    }
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve a product",
        description="Retrieves details of a specific product in the vendor's shed by ID.",
        responses={200: ProductSerializer},
        examples=[
            OpenApiExample(
                "Retrieve product response",
                value={
                    "id": 1,
                    "shed": 1,
                    "name": "Smartphone",
                    "description": "Latest 5G smartphone",
                    "price": "150000.00",
                    "image": None,
                    "created_at": "2025-10-24T15:00:00Z",
                    "updated_at": "2025-10-24T15:00:00Z"
                }
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create a new product",
        description="Adds a new product to the authenticated vendor's shed.",
        request=ProductSerializer,
        responses={201: ProductSerializer},
        examples=[
            OpenApiExample(
                "Create product request",
                value={
                    "name": "Smartphone",
                    "description": "Latest 5G smartphone",
                    "price": "150000.00",
                    "image": None
                },
                request_only=True
            ),
            OpenApiExample(
                "Create product response",
                value={
                    "id": 1,
                    "shed": 1,
                    "name": "Smartphone",
                    "description": "Latest 5G smartphone",
                    "price": "150000.00",
                    "image": None,
                    "created_at": "2025-10-24T15:00:00Z",
                    "updated_at": "2025-10-24T15:00:00Z"
                }
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        vendor_profile = request.user.vendor_profile
        shed = get_object_or_404(Shed, vendor=vendor_profile)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(shed=shed)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Update a product",
        description="Updates an existing product in the vendor's shed by ID.",
        request=ProductSerializer,
        responses={200: ProductSerializer},
        examples=[
            OpenApiExample(
                "Update product request",
                value={
                    "name": "Smartphone Pro",
                    "description": "Upgraded 5G smartphone with better camera",
                    "price": "180000.00",
                    "image": None
                },
                request_only=True
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update a product",
        description="Partially updates an existing product in the vendor's shed by ID.",
        request=ProductSerializer,
        responses={200: ProductSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete a product",
        description="Deletes a specific product from the vendor's shed by ID, leaving other products and the shed intact.",
        responses={204: None},
        examples=[
            OpenApiExample(
                "Delete product response",
                value={},
                description="No content returned on successful deletion."
            ),
            OpenApiExample(
                "Product not found",
                value={"detail": "Not found."},
                status_codes=["404"],
                description="Returned if the product ID does not exist."
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        """
        Deletes a single product from the vendor's shed.
        """
        return super().destroy(request, *args, **kwargs)