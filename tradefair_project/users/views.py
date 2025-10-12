# users/views.py
"""
API views for user management in the TradeFair project.

Handles user signup, login, and profile management for vendors and customers.
Uses token-based authentication with Django REST Framework.
"""

from rest_framework import generics, permissions, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import VendorProfile, CustomerProfile
from .serializers import UserSerializer, VendorProfileSerializer, CustomerProfileSerializer

# Get the custom user model defined in settings.AUTH_USER_MODEL
CustomUser = get_user_model()


class SignupView(APIView):
    """
    API view for user signup.

    Creates VendorProfile or CustomerProfile based on 'is_vendor' flag.
    Automatically generates an authentication token upon successful signup.
    """
    def post(self, request):
        """
        Handle POST request for user signup.

        Args:
            request: HTTP request containing user data and 'is_vendor' flag.

        Returns:
            Response: JSON with token and user data on success, or errors on failure.
        """
        is_vendor = request.data.get('is_vendor', False)
        serializer = VendorProfileSerializer(data=request.data) if is_vendor else CustomerProfileSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save()
            token, _ = Token.objects.get_or_create(user=profile.user)
            return Response({
                "message": "Signup successful",
                "token": token.key,
                "user": UserSerializer(profile.user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view for user login.

    Authenticates users and returns an authentication token.
    """
    def post(self, request):
        """
        Handle POST request for user login.

        Args:
            request: HTTP request with username and password.

        Returns:
            Response: JSON with token and user info on success, or error on invalid credentials.
        """
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                "message": "Login successful",
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
                "is_vendor": user.is_vendor
            }, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission for VendorProfile.

    Allows read access to all users (or anonymous).
    Restricts write access (update/delete) to the profile's owner.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions.

        Args:
            request: HTTP request.
            view: View handling the request.
            obj: VendorProfile instance.

        Returns:
            bool: True if permission granted, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, "vendor_profile") and obj.user == request.user


class VendorProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing vendor profiles.

    - All users can list/retrieve vendors.
    - Only vendors can update/delete their own profile.
    """
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVendorOwnerOrReadOnly]


class CustomerProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customer profiles.

    Only authenticated customers can access their own profile.
    """
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Restrict queryset to the authenticated customer's profile.

        Returns:
            QuerySet: Filtered CustomerProfile objects.
        """
        return CustomerProfile.objects.filter(user=self.request.user)


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.

    Creates a CustomUser and associated VendorProfile or CustomerProfile.
    Generates an authentication token.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Handle POST request for user registration.

        Args:
            request: HTTP request with username, email, password, and optional is_vendor.

        Returns:
            Response: JSON with token and user data on success, or error on failure.
        """
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        is_vendor = request.data.get("is_vendor", False)

        if not username or not password:
            return Response({"error": "Username and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(username=username, email=email, password=password, is_vendor=is_vendor)
        token, _ = Token.objects.get_or_create(user=user)

        # Create profile based on is_vendor
        if is_vendor:
            VendorProfile.objects.create(user=user, business_name=request.data.get("business_name", ""))
        else:
            CustomerProfile.objects.create(user=user)

        return Response({
            "message": "User registered successfully",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_vendor": user.is_vendor
            }
        }, status=status.HTTP_201_CREATED)