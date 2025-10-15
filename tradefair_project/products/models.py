"""
Models for the products app in the TradeFair project.

Defines the Product model for items sold by vendors in sheds, including pricing,
quantity, and images.
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Product(models.Model):
    """
    Model representing a product sold by a vendor in a shed.

    Attributes:
        shed (ForeignKey): The shed where the product is listed.
        vendor (ForeignKey): The vendor user selling the product.
        name (CharField): The name of the product.
        description (TextField): A description of the product (optional).
        price (DecimalField): The price of the product in the local currency.
        quantity (PositiveIntegerField): The available stock of the product.
        image (ImageField): An optional image of the product.
        created_at (DateTimeField): Timestamp of product creation.
        updated_at (DateTimeField): Timestamp of last update.
    """
    shed = models.ForeignKey(
        'vendors.Shed',
        on_delete=models.CASCADE,
        related_name='products',
        help_text="The shed where the product is listed for sale."
    )
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="The vendor user selling the product."
    )
    name = models.CharField(
        max_length=100,
        help_text="The name of the product."
    )
    description = models.TextField(
        blank=True,
        help_text="A description of the product (optional)."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The price of the product in the local currency."
    )
    quantity = models.PositiveIntegerField(
        help_text="The available stock quantity of the product."
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text="An optional image of the product."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the product was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the product was last updated."
    )

    class Meta:
        """
        Meta options for the Product model.

        Attributes:
            verbose_name (str): Singular name for the model.
            verbose_name_plural (str): Plural name for the model.
        """
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        """
        Provide a string representation of the Product instance.

        Returns:
            str: The name of the product.
        """
        return self.name