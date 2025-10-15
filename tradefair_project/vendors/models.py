"""
Models for the vendors app in the TradeFair project.

Defines the Shed model to represent vendor stalls in the marketplace.
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
    DOMAIN_CHOICES = [
        ('CL', 'Clothing'),
        ('EL', 'Electronics'),
        ('FD', 'Food'),
        ('OT', 'Other'),
    ]

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
        choices=DOMAIN_CHOICES,
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
        """
        Meta options for the Shed model.

        Attributes:
            verbose_name (str): Singular name for the model.
            verbose_name_plural (str): Plural name for the model.
        """
        verbose_name = "Shed"
        verbose_name_plural = "Sheds"

    def __str__(self):
        """
        Provide a string representation of the Shed instance.

        Returns:
            str: Shed number and name.
        """
        return f"{self.shed_number} - {self.name}"