"""
Serializers for the vendors app in the TradeFair project.

Handles serialization and validation for Shed and Product models.
"""

from rest_framework import serializers
from .models import Shed, Product

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.

    Serializes product data including name, description, price, and image.
    """
    class Meta:
        model = Product
        fields = ['id', 'shed', 'name', 'description', 'price', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'shed', 'created_at', 'updated_at']

    def validate_price(self, value):
        """
        Ensure the price is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

class ShedSerializer(serializers.ModelSerializer):
    """
    Serializer for the Shed model, including its products.
    """
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Shed
        fields = ['id', 'shed_number', 'name', 'domain', 'secured', 'collage', 'products']
        read_only_fields = ['id', 'shed_number', 'vendor', 'secured']