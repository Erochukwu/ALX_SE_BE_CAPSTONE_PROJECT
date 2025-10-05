"""
products/models.py

Defines product-related models for the Trade Fair Project.
Each product belongs to a vendor’s shed and includes image, price, and description details.
"""

from django.db import models
from vendors.models import Shed


class Product(models.Model):
    """
    Represents a product listed under a vendor’s shed.

    Attributes:
        shed (ForeignKey): Links the product to a vendor's shed.
        name (CharField): Name/title of the product.
        description (TextField): Short description of the product.
        price (DecimalField): Product price (in NGN or chosen currency).
        stock (PositiveIntegerField): Quantity in stock.
        image (ImageField): Optional uploaded image for the product.
        created_at (DateTimeField): Timestamp when product is created.
        updated_at (DateTimeField): Timestamp when product is last updated.

    Notes:
        - Vendors can only manage products tied to their sheds.
        - Customers and guests can view product listings.
    """

    shed = models.ForeignKey(Shed, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} - ₦{self.price}"


