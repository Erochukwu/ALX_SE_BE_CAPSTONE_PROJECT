"""
Serializers for the orders app in the TradeFair project.

Handles serialization and validation of Preorder model data, including nested fields for
customer, product, and vendor names to enhance API responses.
"""

from rest_framework import serializers
from .models import Preorder
from products.models import Product

class PreorderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Preorder model.

    Serializes preorder data with read-only fields for customer, product, and vendor names.
    Validates quantity to ensure it is positive and does not exceed product stock.
    The customer field is read-only and set by the viewset during creation.

    Attributes:
        customer_name (CharField): Read-only field for the customer's username.
        product_name (CharField): Read-only field for the product's name.
        vendor_name (CharField): Read-only field for the vendor's username.
    """
    customer_name = serializers.CharField(
        source="customer.user.username",
        read_only=True,
        help_text="The username of the customer who placed the preorder."
    )
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
        help_text="The name of the preordered product."
    )
    vendor_name = serializers.CharField(
        source="vendor.username",
        read_only=True,
        help_text="The username of the vendor associated with the product."
    )

    class Meta:
        """
        Meta options for the PreorderSerializer.

        Attributes:
            model: The Preorder model to serialize.
            fields (list): Fields to include in the serialized output.
            read_only_fields (list): Fields that cannot be modified via API input.
        """
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
        Validate preorder data.

        Ensures the quantity is positive and does not exceed the available product stock.

        Args:
            attrs (dict): Deserialized data containing preorder fields.

        Raises:
            serializers.ValidationError: If quantity is non-positive or exceeds product stock.

        Returns:
            dict: Validated preorder data.
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