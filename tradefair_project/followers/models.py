"""
Models for the followers app in the TradeFair project.

Defines the Follow model to track customer-vendor follow relationships.
"""

from django.db import models
from users.models import CustomUser, VendorProfile

class Follow(models.Model):
    """
    Model representing a customer following a vendor.

    Attributes:
        customer (ForeignKey): The customer following the vendor.
        vendor (ForeignKey): The vendor being followed.
        created_at (DateTimeField): Timestamp of when the follow was created.
    """
    customer = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        help_text="The customer following the vendor."
    )
    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name='followers',
        help_text="The vendor being followed."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the follow was created."
    )

    class Meta:
        verbose_name = "Follow"
        verbose_name_plural = "Follows"
        unique_together = ('customer', 'vendor')

    def __str__(self):
        return f"{self.customer.username} follows {self.vendor.business_name}"