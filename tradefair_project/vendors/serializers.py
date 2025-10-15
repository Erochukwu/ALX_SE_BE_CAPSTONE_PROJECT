"""
Serializers for the vendors app in the TradeFair project.

Defines serializers for the Shed model to handle API data.
"""

from rest_framework import serializers
from .models import Shed

class ShedSerializer(serializers.ModelSerializer):
    """
    Serializer for the Shed model.

    Serializes shed data for API responses, including vendor details.
    """
    vendor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Shed
        fields = ['id', 'vendor', 'shed_number', 'name', 'domain', 'secured', 'collage']