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
        first_name (CharField): The user's first name.
        last_name (CharField): The user's last name.
    """
    is_vendor = models.BooleanField(
        default=False,
        help_text="Designates whether the user is a vendor."
    )
    first_name = models.CharField(
        max_length=150,
        help_text="The user's first name."
    )
    last_name = models.CharField(
        max_length=150,
        help_text="The user's last name."
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
        domain (CharField): Category/domain of the shed.
        shed_number (PositiveIntegerField): Unique shed number (1-100) within the domain.
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
        ('FB', 'Food and Beverages'),
        ('JA', 'Jewelry and Accessories'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
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
    shed_number = models.PositiveIntegerField(
        help_text="Unique shed number (1-100) within the domain.",
        unique=True
    )
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    payment_reference = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Vendor Profile"
        verbose_name_plural = "Vendor Profiles"
        constraints = [
            models.UniqueConstraint(
                fields=['domain', 'shed_number'],
                name='unique_shed_per_domain'
            )
        ]

    def __str__(self):
        return f"{self.business_name} (Shed {self.shed_number})"