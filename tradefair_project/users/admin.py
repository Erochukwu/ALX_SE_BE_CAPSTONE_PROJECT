# users/admin.py
from django.contrib import admin
from .models import CustomUser, VendorProfile

admin.site.register(CustomUser)
admin.site.register(VendorProfile)

