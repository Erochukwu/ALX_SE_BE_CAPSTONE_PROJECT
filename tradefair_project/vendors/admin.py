"""
Admin configuration for the vendors app in the TradeFair project.

Registers the Shed model for administration in the Django admin interface.
"""

from django.contrib import admin
from vendors.models import Shed, Product

class ShedAdmin(admin.ModelAdmin):
    list_display = ['shed_number', 'vendor', 'name', 'domain', 'secured']
    search_fields = ['shed_number', 'name']
    list_filter = ['domain', 'secured']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'shed', 'price', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['shed__domain']

admin.site.register(Shed, ShedAdmin)
admin.site.register(Product, ProductAdmin)