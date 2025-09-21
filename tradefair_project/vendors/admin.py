# vendors/admin.py
from django.contrib import admin
from .models import Shed

@admin.register(Shed)
class ShedAdmin(admin.ModelAdmin):
    list_display = ("shed_number", "domain", "name", "vendor", "location")

