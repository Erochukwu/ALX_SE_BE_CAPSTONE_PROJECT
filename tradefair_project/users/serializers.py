"""
Serializers for user-related models in the TradeFair project.
Handles serialization/deserialization for CustomUser, VendorProfile, and CustomerProfile.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import VendorProfile, CustomerProfile

CustomUser = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_vendor']

class VendorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'business_name', 'description']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if not user:
            raise serializers.ValidationError("Authenticated user required to create VendorProfile.")
        if hasattr(user, 'vendorprofile'):
            raise serializers.ValidationError("User already has a VendorProfile.")
        return VendorProfile.objects.create(user=user, **validated_data)

class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_number', 'address']
        
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if not user:
            raise serializers.ValidationError("Authenticated user required to create CustomerProfile.")
        if hasattr(user, 'customerprofile'):
            raise serializers.ValidationError("User already has a CustomerProfile.")
        return CustomerProfile.objects.create(user=user, **validated_data)