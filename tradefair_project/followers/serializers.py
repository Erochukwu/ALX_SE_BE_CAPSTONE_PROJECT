"""
Serializers for the followers app in the TradeFair project.
"""

from rest_framework import serializers
from .models import Follow
from users.models import VendorProfile

class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for the Follow model.
    """
    vendor = serializers.PrimaryKeyRelatedField(queryset=VendorProfile.objects.all())

    def validate_vendor(self, value):
        """
        Validate that the vendor's associated user is a vendor.
        """
        if not value.user.is_vendor:
            raise serializers.ValidationError("The specified user is not a vendor.")
        return value

    class Meta:
        model = Follow
        fields = ['id', 'vendor', 'created_at']
        read_only_fields = ['customer', 'created_at']