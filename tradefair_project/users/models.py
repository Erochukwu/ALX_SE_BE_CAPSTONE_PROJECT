"""
Models for the users app in the TradeFair project.

Defines CustomUser, CustomerProfile, and VendorProfile models.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model extending AbstractUser.

    Attributes:
        is_vendor (BooleanField): Indicates if the user is a vendor.
    """
    is_vendor = models.BooleanField(
        default=False,
        help_text="Designates whether the user is a vendor."
    )

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.username


class VendorProfile(models.Model):
    """
    Model extending CustomUser with vendor-specific attributes.

    Attributes:
        user (OneToOneField): The associated CustomUser account.
        business_name (CharField): The name of the vendor's business.
        description (TextField): A description of the vendor's business.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vendor_profile',
        help_text="The user account linked to this vendor profile."
    )
    DOMAIN_CHOICES = [
        ('CB', 'Clothings and Beddings'),
        ('EC', 'Electronics and Computer wares'),
        ('FB', 'Food abd Beverages'),
        ('JA', 'Jewelry and Accessories'),
    ]
    domain = models.CharField(
        max_length=2,
        choices=DOMAIN_CHOICES,
        help_text="Category/domain of the shed."
    )
    business_name = models.CharField(
        max_length=100,
        help_text="The name of the vendor's business."
    )
    description = models.TextField(
        blank=True,
        help_text="A description of the vendor's business (optional)."
    )

    class Meta:
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"

    def __str__(self):
        return self.business_name
