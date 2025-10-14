"""
Serializers for preorder-related models in the TradeFair project.

Handles serialization and validation for the Preorder model, including nested customer,
product, and vendor information.
"""

from rest_framework import serializers
from .models import Preorder
from products.models import Product

class PreorderSerializer(serializers.ModelSerializer):
    """
    Serializer for Preorder model.

    Includes nested fields (customer_name, product_name, vendor_name) for enriched API responses.
    Validates quantity against product availability.
    The customer field is read-only as it is set by the viewset.
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
        read_only_fields = ["customer", "customer_name", "product_name", "vendor_name", "created_at"]

    def validate(self, attrs):
        """
        Validate the preorder data.

        Ensures the quantity is positive and does not exceed the product's available quantity.

        Args:
            attrs (dict): Dictionary of deserialized data.

        Raises:
            serializers.ValidationError: If quantity is invalid or exceeds product stock.

        Returns:
            dict: Validated data.
        """
        product = attrs.get("product")
        quantity = attrs.get("quantity")

        if quantity <= 0:
            raise serializers.ValidationError({"quantity": "Quantity must be greater than zero."})

        if product and quantity:
            if quantity > product.quantity:
                raise serializers.ValidationError({
                    "quantity": f"Requested quantity ({quantity}) exceeds available stock ({product.quantity})."
                })

        return attrs