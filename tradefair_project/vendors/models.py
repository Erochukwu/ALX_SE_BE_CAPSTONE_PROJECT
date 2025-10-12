"""
vendors/models.py

Defines vendor-related models.
- Shed: Represents a vendor's physical/digital shop.
- Domain: The four allowed categories for vendors.
"""

from django.db import models
from users.models import VendorProfile


class Shed(models.Model):
    """
    A shed represents a vendor's shop/stall.

    Rules:
    - Vendor must choose one of the four domains.
    - A unique shed_number is automatically allocated 
      based on the vendor's chosen domain.
    """

    DOMAIN_CHOICES = [
        ("CL", "Clothing and Bedding"),
        ("FB", "Food and Beverages"),
        ("JC", "Jewelries and Accessories"),
        ("EC", "Electronics and Computer Wares"),
    ]

    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name="sheds")
    domain = models.CharField(max_length=2, choices=DOMAIN_CHOICES)
    shed_number = models.CharField(max_length=6, unique=True, editable=False)  # e.g., CL001, FB023
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    secured = models.BooleanField(default=False)  # Added for payment task
    collage = models.ImageField(upload_to='shed_collages/', blank=True, null=True)  # Added for collage

    def save(self, *args, **kwargs):
        """
        Override save() to automatically assign shed_number based on domain.
        Example ranges:
            - Clothing & Bedding: CL001–CL100
            - Food & Beverages: FB001–FB100
            - Jewelries & Accessories: JC001–JC100
            - Electronics & Computer Wares: EC001–EC100
        """
        if not self.shed_number:
            # Get prefix (e.g., CL, FB, JC, EC)
            prefix = self.domain

            # Count existing sheds in the same domain
            count = Shed.objects.filter(domain=self.domain).count() + 1

            # Ensure we don’t exceed 100
            if count > 100:
                raise ValueError(f"No more sheds available in {self.get_domain_display()}")

            # Format shed number (e.g., CL001)
            self.shed_number = f"{prefix}{count:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.shed_number} - {self.name} ({self.get_domain_display()})"
