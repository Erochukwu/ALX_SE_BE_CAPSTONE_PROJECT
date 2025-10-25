"""
Models for the vendors app in the TradeFair project.

Defines the Shed and Product models to represent vendor stalls and their products in the marketplace.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Shed(models.Model):
    """
    Model representing a vendor's shed in the marketplace.

    Attributes:
        vendor (ForeignKey): The vendor owning the shed.
        shed_number (CharField): Unique identifier for the shed.
        name (CharField): Name of the shed.
        domain (CharField): Category/domain of the shed (e.g., Clothing, Electronics).
        secured (BooleanField): Whether the shed is secured (e.g., payment completed).
        collage (ImageField): Image collage of products in the shed.
    """
    vendor = models.ForeignKey(
        'users.VendorProfile',
        on_delete=models.CASCADE,
        related_name='sheds',
        help_text="The vendor owning this shed."
    )
    shed_number = models.CharField(
        max_length=10,
        unique=True,
        help_text="Unique identifier for the shed."
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the shed."
    )
    domain = models.CharField(
        max_length=2,
        choices=[
            ('CB', 'Clothings and Beddings'),
            ('EC', 'Electronics and Computer wares'),
            ('FB', 'Food and Beverages'),
            ('JA', 'Jewelry and Accessories'),
        ],
        help_text="Category/domain of the shed."
    )
    secured = models.BooleanField(
        default=False,
        help_text="Whether the shed is secured (e.g., payment completed)."
    )
    collage = models.ImageField(
        upload_to='shed_collages/',
        blank=True,
        null=True,
        help_text="Image collage of products in the shed."
    )

    class Meta:
        verbose_name = "Shed"
        verbose_name_plural = "Sheds"

    def __str__(self):
        return f"{self.shed_number} - {self.name}"

class Product(models.Model):
    """
    Model representing a product in a vendor's shed.

    Attributes:
        shed (ForeignKey): The shed containing the product.
        name (CharField): Name of the product.
        description (TextField): Description of the product.
        price (DecimalField): Price of the product in NGN.
        image (ImageField): Optional image of the product.
        created_at (DateTimeField): When the product was added.
        updated_at (DateTimeField): When the product was last updated.
    """
    shed = models.ForeignKey(
        Shed,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="The shed containing this product."
    )
    name = models.CharField(
        max_length=100,
        help_text="Name of the product."
    )
    description = models.TextField(
        help_text="Description of the product."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of the product in NGN."
    )
    image = models.ImageField(
        upload_to='product_images/',
        blank=True,
        null=True,
        help_text="Optional image of the product."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the product was added."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the product was last updated."
    )

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} - {self.shed.name}"