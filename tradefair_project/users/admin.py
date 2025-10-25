"""
Admin configuration for the users app in the TradeFair project.
Registers CustomerProfile and VendorProfile models for administration in the
Django admin interface. The default Django User model is managed by Django's
built-in admin app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, VendorProfile

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
    list_filter = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'domain', 'description']
    search_fields = ['user__username', 'business_name']
    list_filter = ['domain']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(VendorProfile, VendorProfileAdmin)