"""
Models for the orders app in the TradeFair project.

Defines the Preorder model to manage customer preorders for vendor products, including
quantity, status, and timestamps.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Preorder(models.Model):
    """
    Model representing a preorder placed by a customer for a vendor's product.

    Stores relationships to customers, vendors, and products, along with order details
    such as quantity and status.

    Attributes:
        customer (ForeignKey): The CustomerProfile placing the preorder.
        vendor (ForeignKey): The User (vendor) associated with the product.
        product (ForeignKey): The Product being preordered.
        quantity (PositiveIntegerField): Number of items preordered.
        status (CharField): Current status of the preorder (pending, confirmed, cancelled).
        created_at (DateTimeField): Timestamp of preorder creation.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='preorders',
        help_text="The customer profile placing the preorder."
    )
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vendor_preorders',
        help_text="The vendor user associated with the product."
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='preorders',
        help_text="The product being preordered."
    )
    quantity = models.PositiveIntegerField(
        help_text="The number of product units preordered."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of the preorder (pending, confirmed, or cancelled)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the preorder was created."
    )

    class Meta:
        """
        Meta options for the Preorder model.

        Attributes:
            verbose_name (str): Singular name for the model.
            verbose_name_plural (str): Plural name for the model.
        """
        verbose_name = "Preorder"
        verbose_name_plural = "Preorders"

    def __str__(self):
        """
        Provide a string representation of the Preorder instance.

        Returns:
            str: A description of the preorder, including customer username, product name, and quantity.
        """
        return f"Preorder by {self.customer.user.username} for {self.product.name} (Qty: {self.quantity})"