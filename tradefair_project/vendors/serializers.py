"""
vendors/serializers.py

Serializers for vendor and shed data exchange via REST API.
Handles serialization/deserialization for Shed model.
"""

from rest_framework import serializers
from .models import Shed


class ShedSerializer(serializers.ModelSerializer):
    """
    Serializer for the Shed model.
    Includes vendor info (read-only) and domain/category metadata.
    """
    vendor_name = serializers.CharField(source="vendor.business_name", read_only=True)
    domain_display = serializers.CharField(source="get_domain_display", read_only=True)

    class Meta:
        model = Shed
        fields = [
            'id',
            'vendor',
            'vendor_name',
            'domain',
            'domain_display',
            'shed_number',
            'name',
            'location',
        ]
        read_only_fields = ['shed_number']

    def get_collage_url(self, obj):
        request = self.context.get('request')
        if obj.collage and hasattr(obj.collage, 'url'):
            return request.build_absolute_uri(obj.collage.url)
        return None
    
    def validate_collage(self, value):
        # Optional: Add file validation (size, type, etc.)
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("Collage file too large (max 5MB).")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("Only image files are allowed.")
        return value
