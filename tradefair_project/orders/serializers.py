"""
orders/serializers.py

Handles serialization and validation for Preorder model.
"""

from rest_framework import serializers
from .models import Preorder


class PreorderSerializer(serializers.ModelSerializer):
    """
    Serializer for Preorder model.
    """
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    vendor_name = serializers.CharField(source="vendor.username", read_only=True)

    class Meta:
        model = Preorder
        fields = [
            "id",
            "customer",
            "customer_name",
            "vendor",
            "vendor_name",
            "product",
            "product_name",
            "quantity",
            "status",
            "created_at",
        ]
        read_only_fields = ["created_at", "customer_name", "vendor_name", "product_name"]
