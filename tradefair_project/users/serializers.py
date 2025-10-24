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
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    username = serializers.CharField(required=True, max_length=150)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'username', 'email', 'password', 'password2'
        ]

    def validate(self, attrs):
        """Ensure passwords match and validate vendor-specific fields."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        return attrs

    def create(self, validated_data):
        """
        Create a user.
        """
        password = validated_data.pop('password')
        validated_data.pop('password2')

        # Create user
        user = CustomUser.objects.create(
            **validated_data,
        )
        user.set_password(password)
        user.save()

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
    
class VendorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorProfile
        fields = [
            'business_name', 'description', 'domain', 'shed_number',
            'payment_status', 'payment_reference'
        ]
        read_only_fields = ['shed_number', 'payment_status', 'payment_reference']

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile retrieval.
    """
    vendor_profile = VendorProfileSerializer(read_only=True)
    class Meta:
            model = CustomUser
            fields = [
                'id', 'username', 'email', 'first_name', 'last_name',
                'is_vendor', 'vendor_profile'
    ]
    read_only_fields = ['id', 'username', 'email', 'is_vendor', 'vendor_profile']

class VendorRegistrationSerializer(serializers.Serializer):
    """
    Serializer for vendor registration with Redis and Paystack integration.
    Validates vendor data before storing in Redis for 1 hour.
    """
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        required=True
    )
    password2 = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        label="Confirm Password",
        required=True
    )
    business_name = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(allow_blank=True, required=False)
    domain = serializers.ChoiceField(
    choices=VendorProfile.DOMAIN_CHOICES,
    required=True
    )
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        if CustomUser.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "This username is already taken."})
        domain = attrs['domain']
        existing_vendors = VendorProfile.objects.filter(domain=domain).count()
        if existing_vendors >= 100:
            raise serializers.ValidationError(
                {"domain": f"The sheds in this domain ({domain}) are fully booked."}
            )
        return attrs
