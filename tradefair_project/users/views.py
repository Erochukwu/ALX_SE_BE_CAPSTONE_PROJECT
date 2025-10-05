# users/views.py

from rest_framework import generics, permissions
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import VendorProfile, CustomerProfile
from .serializers import (
    UserSerializer, VendorProfileSerializer, CustomerProfileSerializer
)

CustomUser = get_user_model()


class SignupView(APIView):
    """
    Handles user signup for both vendor and customer types.
    Automatically creates authentication token.
    """
    def post(self, request):
        is_vendor = request.data.get('is_vendor', False)

        if is_vendor:
            serializer = VendorProfileSerializer(data=request.data)
        else:
            serializer = CustomerProfileSerializer(data=request.data)

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
    Handles user authentication and token retrieval.
    """
    def post(self, request):
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


class VendorProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Vendor Profiles.
    Only accessible to authenticated users.
    """
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Vendors can only see their own profile.
        """
        return VendorProfile.objects.filter(user=self.request.user)


class CustomerProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Customer Profiles.
    Only accessible to authenticated users.
    """
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Customers can only see their own profile.
        """
        return CustomerProfile.objects.filter(user=self.request.user)

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Use your CustomUser model
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "User registered successfully",
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_201_CREATED)
