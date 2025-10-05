# users/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import VendorProfile, CustomerProfile

CustomUser = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomUser.
    Handles user creation and exposes basic fields.
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'is_vendor']

    def create(self, validated_data):
        """
        Create and return a new user with a hashed password.
        """
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class VendorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for VendorProfile model.
    Includes related CustomUser data.
    """
    user = UserSerializer()

    class Meta:
        model = VendorProfile
        fields = ['id', 'user', 'business_name', 'description']

    def create(self, validated_data):
        """
        Create a Vendor user and associated VendorProfile.
        """
        user_data = validated_data.pop('user')
        user_data['is_vendor'] = True  # ensure user is marked as vendor
        user = UserSerializer().create(user_data)
        profile = VendorProfile.objects.create(user=user, **validated_data)
        return profile


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for CustomerProfile model.
    Includes related CustomUser data.
    """
    user = UserSerializer()

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_number', 'address']

    def create(self, validated_data):
        """
        Create a Customer user and associated CustomerProfile.
        """
        user_data = validated_data.pop('user')
        user_data['is_vendor'] = False  # ensure user is marked as customer
        user = UserSerializer().create(user_data)
        profile = CustomerProfile.objects.create(user=user, **validated_data)
        return profile
