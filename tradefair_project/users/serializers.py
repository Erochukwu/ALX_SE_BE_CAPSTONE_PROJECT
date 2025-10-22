"""
Serializers for user registration and authentication in the TradeFair project.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, VendorProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles both regular user and vendor registration.
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label="Confirm Password"
    )

    # Vendor-specific fields (optional for regular users)
    business_name = serializers.CharField(
        required=False,
        allow_blank=True
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True
    )
    domain = serializers.ChoiceField(
        choices=VendorProfile.DOMAIN_CHOICES,
        required=False
    )

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password2',
            'is_vendor', 'business_name', 'description', 'domain'
        ]

    def validate(self, attrs):
        """Ensure passwords match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        """
        Create a user (and vendor profile if applicable).
        """
        password = validated_data.pop('password')
        validated_data.pop('password2')

        is_vendor = validated_data.pop('is_vendor', False)

        business_name = validated_data.pop('business_name', None)
        description = validated_data.pop('description', None)
        domain = validated_data.pop('domain', None)

        # Create user
        user = CustomUser.objects.create(
            **validated_data,
            is_vendor=is_vendor
        )
        user.set_password(password)
        user.save()

        # If vendor, create VendorProfile
        if is_vendor:
            if not business_name or not domain:
                raise serializers.ValidationError(
                    {"vendor_profile": "Vendors must provide business name and domain."}
                )
            VendorProfile.objects.create(
                user=user,
                business_name=business_name,
                description=description or "",
                domain=domain
            )

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):
        """Authenticate user with provided credentials."""
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid username or password.")
        else:
            raise serializers.ValidationError("Both username and password are required.")

        attrs['user'] = user
        return attrs
