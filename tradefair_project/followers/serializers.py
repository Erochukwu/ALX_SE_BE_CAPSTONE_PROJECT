"""
followers/serializers.py

Handles serialization and validation for Follower model.
"""

from rest_framework import serializers
from .models import Follow


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for Follow model.
    """
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)
    vendor_name = serializers.CharField(source="vendor.user.username", read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "customer", "customer_name", "vendor", "vendor_name", "followed_at"]
        read_only_fields = ["followed_at"]
