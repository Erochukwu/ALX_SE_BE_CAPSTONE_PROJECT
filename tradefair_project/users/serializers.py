# users/serializers.py
"""
Serializers for user-related models in the TradeFair project.

Handles serialization/deserialization for CustomUser, VendorProfile, and CustomerProfile.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import VendorProfile, CustomerProfile

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser model.

    Includes basic user fields for serialization.
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_vendor']


class VendorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for VendorProfile model.

    Includes user data and business_name for vendor profiles.
    Handles creation of CustomUser and VendorProfile.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'business_name', 'description']

    def create(self, validated_data):
        """
        Create a new VendorProfile with associated CustomUser.

        Args:
            validated_data: Validated data from the request.

        Returns:
            VendorProfile: Created profile instance.
        """
        user_data = validated_data.pop('user', {})
        user = CustomUser.objects.create_user(**user_data)
        return VendorProfile.objects.create(user=user, **validated_data)


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerProfile model.

    Includes user data for customer profiles.
    Handles creation of CustomUser and CustomerProfile.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_number', 'address'] 
        
    def create(self, validated_data):
        """
        Create a new CustomerProfile with associated CustomUser.

        Args:
            validated_data: Validated data from the request.

        Returns:
            CustomerProfile: Created profile instance.
        """
        user_data = validated_data.pop('user', {})
        user = CustomUser.objects.create_user(**user_data)
        return CustomerProfile.objects.create(user=user, **validated_data)