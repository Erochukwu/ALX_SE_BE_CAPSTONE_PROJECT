"""
Serializers for product-related models in the TradeFair project.
Handles serialization and validation for the Product model, including nested shed and vendor information.
"""

from rest_framework import serializers
from .models import Product
from vendors.models import Shed

class ShedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shed
        fields = ['id', 'name', 'shed_number', 'domain']

class ProductSerializer(serializers.ModelSerializer):
    shed = ShedSerializer(read_only=True)
    shed_name = serializers.CharField(source='shed.name', read_only=True)
    shed_number = serializers.CharField(source='shed.shed_number', read_only=True)
    vendor_name = serializers.CharField(source='vendor.username', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'shed', 'shed_name', 'shed_number', 'vendor', 'vendor_name', 'name', 'description', 'price', 'quantity', 'image', 'created_at', 'updated_at']
        read_only_fields = ['shed_name', 'shed_number', 'vendor_name', 'created_at', 'updated_at']

    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:  # Max 5MB
                raise serializers.ValidationError("Image file too large (max 5MB).")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("Only image files are allowed.")
        return value