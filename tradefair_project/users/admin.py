"""
Admin configuration for the users app in the TradeFair project.

Registers CustomerProfile and VendorProfile models for administration in the
Django admin interface. The default Django User model is managed by Django's
built-in admin app.
"""

from django.contrib import admin
from .models import VendorProfile

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the VendorProfile model.

    Attributes:
        list_display (tuple): Fields to display in the admin list view.
        search_fields (tuple): Fields to search in the admin interface.
    """
    list_display = ('user', 'business_name')
    search_fields = ('user__username', 'business_name')