from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, VendorProfile
from .serializers import UserRegistrationSerializer, UserLoginSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for registering regular users.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new regular user",
        description="Creates a new regular user account with basic user information. "
                    "Vendor-specific fields are not required for regular user registration. "
                    "Returns user data and JWT access/refresh tokens.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "Regular user registration example",
                value={
                    "username": "john_doe",
                    "email": "john@example.com",
                    "password": "securepassword123",
                    "password2": "securepassword123",
                    "is_vendor": False
                },
                description="Example request for registering a regular user"
            ),
            OpenApiExample(
                "Regular user registration response",
                value={
                    "user": {
                        "username": "john_doe",
                        "email": "john@example.com",
                        "is_vendor": False
                    },
                    "refresh": "string",
                    "access": "string"
                },
                description="Example response with JWT tokens"
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'is_vendor': user.is_vendor
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class VendorRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for registering vendors.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new vendor",
        description="Creates a new vendor account with both user and vendor-specific information. "
                    "Vendor-specific fields (business_name, domain) are required. "
                    "Returns user data, vendor profile data, and JWT access/refresh tokens.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "Vendor registration example",
                value={
                    "username": "vendor1",
                    "email": "vendor@example.com",
                    "password": "securepassword123",
                    "password2": "securepassword123",
                    "is_vendor": True,
                    "business_name": "Vendor Shop",
                    "description": "Quality clothing and accessories",
                    "domain": "CB"
                },
                description="Example request for registering a vendor"
            ),
            OpenApiExample(
                "Vendor registration response",
                value={
                    "user": {
                        "username": "vendor1",
                        "email": "vendor@example.com",
                        "is_vendor": True
                    },
                    "vendor_profile": {
                        "business_name": "Vendor Shop",
                        "description": "Quality clothing and accessories",
                        "domain": "CB"
                    },
                    "refresh": "string",
                    "access": "string"
                },
                description="Example response with JWT tokens"
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        # Ensure is_vendor is True for vendor registration
        data = request.data.copy()
        data['is_vendor'] = True
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        headers = self.get_success_headers(serializer.data)
        response_data = {
            'user': {
                'username': user.username,
                'email': user.email,
                'is_vendor': user.is_vendor
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        
        # Include vendor profile data if available
        if user.is_vendor:
            vendor_profile = user.vendor_profile
            response_data['vendor_profile'] = {
                'business_name': vendor_profile.business_name,
                'description': vendor_profile.description,
                'domain': vendor_profile.domain
            }
        
        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for user login (both regular users and vendors).
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User login",
        description="Authenticates both regular users and vendors using username and password. "
                    "Returns user information and JWT access/refresh tokens upon successful authentication.",
        request=UserLoginSerializer,
        responses={
            200: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "Login example",
                value={
                    "username": "john_doe",
                    "password": "securepassword123"
                },
                description="Example request for user login"
            ),
            OpenApiExample(
                "Login response",
                value={
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "is_vendor": False
                    },
                    "refresh": "string",
                    "access": "string",
                    "message": "Login successful"
                },
                description="Example response with JWT tokens"
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_vendor': user.is_vendor
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        }
        
        # Include vendor profile data if user is a vendor
        if user.is_vendor:
            vendor_profile = user.vendor_profile
            response_data['vendor_profile'] = {
                'business_name': vendor_profile.business_name,
                'description': vendor_profile.description,
                'domain': vendor_profile.domain
            }
        
        return Response(response_data, status=status.HTTP_200_OK)