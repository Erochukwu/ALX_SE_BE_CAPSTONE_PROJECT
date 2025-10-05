"""
products/serializers.py

Handles serialization and validation for Product model.
"""

from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    Handles nested shed information and image uploads.
    """
    shed_name = serializers.CharField(source='shed.name', read_only=True)
    vendor_name = serializers.CharField(source='shed.vendor.business_name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'shed',
            'shed_name',
            'vendor_name',
            'name',
            'description',
            'price',
            'image',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
