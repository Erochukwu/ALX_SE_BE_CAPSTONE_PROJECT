"""
products/models.py

Defines product-related models for the Trade Fair Project.
Each product belongs to a vendor’s shed and includes image, price, and description details.
"""

from django.db import models
from django.conf import settings
from vendors.models import Shed  # Use the correct Shed from vendors app


class Product(models.Model):
    """
    Represents a product listed under a vendor’s shed.

    Attributes:
        shed (ForeignKey): Links the product to a vendor's shed.
        vendor (ForeignKey): Links product to the vendor user.
        name (CharField): Name/title of the product.
        description (TextField): Optional description.
        price (DecimalField): Product price.
        quantity (IntegerField): Available stock.
        image (ImageField): Optional image for the product.
        created_at (DateTimeField): Timestamp when product is created.
        updated_at (DateTimeField): Timestamp when product is last updated.

    Notes:
        - Vendors can only manage products tied to their sheds.
        - Customers and guests can view product listings.
    """

    shed = models.ForeignKey(Shed, on_delete=models.CASCADE, related_name="products")
    vendor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to="product_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} - ₦{self.price}"


