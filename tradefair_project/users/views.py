from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from vendors.models import Shed
from .models import CustomUser, VendorProfile
from .serializers import UserRegistrationSerializer, UserLoginSerializer, VendorProfileSerializer, VendorRegistrationSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.types import OpenApiTypes
from django.conf import settings
from paystackapi.transaction import Transaction
import uuid
import redis
import json
from django.contrib.auth.hashers import make_password

redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def generate_unique_shed_number(domain):
        prefix = f"{domain}"  # e.g., JA, CB, EC, FB
        number = 1
        while Shed.objects.filter(shed_number=f"{prefix}{number}").exists() or \
            VendorProfile.objects.filter(shed_number=f"{prefix}{number}").exists():
            number += 1
            if number > 100:  # Limit to 100 sheds per domain
                raise ValueError(f"No available shed numbers for domain {domain}")
        return f"{prefix}{number}"

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
                    "first_name": "John",
                    "last_name": "Doe",
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
                        "first_name": "John",
                        "last_name": "Doe",
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
                    'first_name': user.first_name,
                    'last_name': user.last_name,
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
    ViewSet for registering vendors with Paystack payment integration.
    """
    queryset = CustomUser.objects.all()
    serializer_class = VendorRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Initiate vendor registration",
        description="Stores vendor registration data in Redis for 1 hour and generates a Paystack payment link for 30,000 NGN. "
                    "Shed is assigned and registration completed only after payment confirmation within 1 hour.",
        request=VendorRegistrationSerializer,
        responses={
            201: OpenApiTypes.OBJECT,
            400: OpenApiTypes.OBJECT,
            500: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "Vendor registration example",
                value={
                    "username": "vendor1",
                    "email": "vendor@example.com",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "password": "securepassword123",
                    "password2": "securepassword123",
                    "business_name": "Vendor Shop",
                    "description": "Quality clothing and accessories",
                    "domain": "CB"
                },
                description="Example request for initiating vendor registration"
            ),
            OpenApiExample(
                "Vendor registration response",
                value={
                    "message": "Please complete payment of 30,000 NGN to secure your shed allocation.",
                    "payment_link": "https://checkout.paystack.com/...",
                    "reference": "SHED-PENDING-uuid"
                },
                description="Example response with Paystack payment link"
            ),
            OpenApiExample(
                "Domain fully booked error",
                value={
                    "domain": "The sheds in this domain (CB) are fully booked."
                },
                description="Error response when the domain has reached its 100-shed limit"
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        vendor_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'password': make_password(validated_data['password']),
            'business_name': validated_data['business_name'],
            'description': validated_data.get('description', ''),
            'domain': validated_data['domain']
        }
        reference = f"SHED-PENDING-{uuid.uuid4()}"
        redis_client.setex(
            reference,
            3600,
            json.dumps(vendor_data)
        )
        transaction = Transaction(secret_key=settings.PAYSTACK_SECRET_KEY)
        payment_data = {
            'amount': 30000 * 100,
            'email': vendor_data['email'],
            'reference': reference,
            'callback_url': settings.PAYSTACK_CALLBACK_URL,
            'metadata': {'reference': reference}
        }
        try:
            payment_response = transaction.initialize(**payment_data)
            if payment_response['status']:
                payment_link = payment_response['data']['authorization_url']
                return Response(
                    {
                        'message': 'Please complete payment of 30,000 NGN to secure your shed allocation.',
                        'payment_link': payment_link,
                        'reference': reference
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                redis_client.delete(reference)
                return Response(
                    {'error': 'Failed to initiate payment'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        except Exception as e:
            redis_client.delete(reference)
            return Response(
                {'error': f'Payment initiation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
def paystack_payment_callback(request):
    """
    Callback endpoint for Paystack payment verification.
    Completes vendor registration on successful payment.
    """
    reference = request.GET.get('reference')
    if not reference:
        return Response({'error': 'Missing payment reference'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        transaction = Transaction(secret_key=settings.PAYSTACK_SECRET_KEY)
        verification = transaction.verify(reference)
        if verification['status'] and verification['data']['status'] == 'success':
            vendor_data_json = redis_client.get(reference)
            if not vendor_data_json:
                return Response(
                    {'error': 'Registration data expired or not found. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            vendor_data = json.loads(vendor_data_json)
            user = CustomUser.objects.create(
                username=vendor_data['username'],
                email=vendor_data['email'],
                first_name=vendor_data['first_name'],
                last_name=vendor_data['last_name'],
                is_vendor=True
            )
            user.set_password(vendor_data['password'])
            user.save()
            shed_number = generate_unique_shed_number(vendor_data['domain'])
            vendor_profile = VendorProfile.objects.create(
                user=user,
                business_name=vendor_data['business_name'],
                description=vendor_data['description'],
                domain=vendor_data['domain'],
                shed_number=shed_number,
                payment_status='COMPLETED',
                payment_reference=reference
            )
            Shed.objects.create(
                vendor=vendor_profile,
                shed_number=shed_number,
                name=f"{vendor_data['business_name']} Stall",
                domain=vendor_data['domain'],
                secured=True
            )
            redis_client.delete(reference)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': f"Successfully registered! Your shed allocation is confirmed. Business: {vendor_profile.business_name}, Description: {vendor_profile.description}, Shed Number: {vendor_profile.shed_number}.",
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_vendor': user.is_vendor
                    },
                    'vendor_profile': {
                        'business_name': vendor_profile.business_name,
                        'description': vendor_profile.description,
                        'domain': vendor_profile.domain,
                        'shed_number': vendor_profile.shed_number,
                        'payment_status': vendor_profile.payment_status,
                        'payment_reference': vendor_profile.payment_reference
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )
        else:
            redis_client.delete(reference)
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        redis_client.delete(reference)
        return Response({'error': f'Payment verification error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
@extend_schema(
    summary="Mock Paystack callback for testing",
    description="Simulates Paystack payment verification for testing vendor registration. "
                "Accepts a payment reference and completes registration if data exists in Redis. "
                "For local testing only; assumes payment is successful.",
    parameters=[
        {
            'name': 'reference',
            'in': 'query',
            'required': True,
            'schema': {'type': 'string'},
            'description': 'Payment reference (e.g., SHED-PENDING-uuid)'
        },
        {
            'name': 'status',
            'in': 'query',
            'required': False,
            'schema': {'type': 'string', 'enum': ['success', 'failed'], 'default': 'success'},
            'description': 'Simulated payment status (success or failed)'
        }
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT,
        500: OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            "Mock callback success response",
            value={
                "message": "Successfully registered! Your shed allocation is confirmed. Business: Vendor Shop, Description: Quality clothing and accessories, Shed Number: CB1.",
                "user": {
                    "id": 1,
                    "username": "vendor1",
                    "email": "vendor@example.com",
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "is_vendor": True
                },
                "vendor_profile": {
                    "business_name": "Vendor Shop",
                    "description": "Quality clothing and accessories",
                    "domain": "CB",
                    "shed_number": "CB1",
                    "payment_status": "COMPLETED",
                    "payment_reference": "SHED-PENDING-uuid"
                },
                "refresh": "string",
                "access": "string"
            },
            description="Example response for successful mock payment verification"
        ),
        OpenApiExample(
            "Mock callback failure response",
            value={
                "error": "Payment verification failed."
            },
            description="Example response when mock payment status is 'failed'"
        ),
        OpenApiExample(
            "Mock callback expired data response",
            value={
                "error": "Registration data expired or not found. Please try again."
            },
            description="Example response when Redis data is missing"
        )
    ]
)
def mock_paystack_callback(request):
    """
    Mock Paystack callback endpoint for testing vendor registration.
    Simulates payment verification without calling Paystack API.
    """
    reference = request.GET.get('reference')
    if not reference:
        return Response({'error': 'Missing payment reference'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        payment_status = request.GET.get('status', 'success')
        if payment_status == 'success':
            vendor_data_json = redis_client.get(reference)
            if not vendor_data_json:
                return Response(
                    {'error': 'Registration data expired or not found. Please try again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            vendor_data = json.loads(vendor_data_json)
            user = CustomUser.objects.create(
                username=vendor_data['username'],
                email=vendor_data['email'],
                first_name=vendor_data['first_name'],
                last_name=vendor_data['last_name'],
                is_vendor=True
            )
            user.set_password(vendor_data['password'])
            user.save()
            shed_number = generate_unique_shed_number(vendor_data['domain'])
            vendor_profile = VendorProfile.objects.create(
                user=user,
                business_name=vendor_data['business_name'],
                description=vendor_data['description'],
                domain=vendor_data['domain'],
                shed_number=shed_number,
                payment_status='COMPLETED',
                payment_reference=reference
            )
            Shed.objects.create(
                vendor=vendor_profile,
                shed_number=shed_number,
                name=f"{vendor_data['business_name']} Stall",
                domain=vendor_data['domain'],
                secured=True
            )
            redis_client.delete(reference)
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': f"Successfully registered! Your shed allocation is confirmed. Business: {vendor_profile.business_name}, Description: {vendor_profile.description}, Shed Number: {vendor_profile.shed_number}.",
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_vendor': user.is_vendor
                    },
                    'vendor_profile': {
                        'business_name': vendor_profile.business_name,
                        'description': vendor_profile.description,
                        'domain': vendor_profile.domain,
                        'shed_number': vendor_profile.shed_number,
                        'payment_status': vendor_profile.payment_status,
                        'payment_reference': vendor_profile.payment_reference
                    },
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                },
                status=status.HTTP_200_OK
            )
        else:
            redis_client.delete(reference)
            return Response({'error': 'Payment verification failed.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        redis_client.delete(reference)
        return Response({'error': f'Mock callback error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    

@api_view(['GET'])
def test_redis(request):
    """
    Test Redis connectivity by setting and retrieving a test value.
    """
    try:
        redis_client.set('test_key', 'test_value')
        value = redis_client.get('test_key')
        redis_client.delete('test_key')
        return Response({'status': 'success', 'value': value}, status=200)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=500)

class UserLoginViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
        """
        ViewSet for user login (both regular users and vendors).
        """
        serializer_class = UserLoginSerializer
        permission_classes = [AllowAny]

        @extend_schema(
            summary="User login",
            description="Authenticates both regular users and vendors using username and password. "
                        "Returns user information, vendor profile (if applicable), and JWT access/refresh tokens.",
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
                    "Login response (regular user)",
                    value={
                        "user": {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "is_vendor": False
                        },
                        "refresh": "string",
                        "access": "string",
                        "message": "Login successful"
                    },
                    description="Example response for regular user login"
                ),
                OpenApiExample(
                    "Login response (vendor)",
                    value={
                        "user": {
                            "id": 2,
                            "username": "vendor1",
                            "email": "vendor@example.com",
                            "first_name": "Jane",
                            "last_name": "Smith",
                            "is_vendor": True
                        },
                        "vendor_profile": {
                            "business_name": "Vendor Shop",
                            "description": "Quality clothing and accessories",
                            "domain": "CB",
                            "shed_number": 1
                        },
                        "refresh": "string",
                        "access": "string",
                        "message": "Login successful"
                    },
                    description="Example response for vendor login with shed number"
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
                    'first_name': user.first_name,
                    'last_name': user.last_name,
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
                    'domain': vendor_profile.domain,
                    'shed_number': vendor_profile.shed_number
                }
            
            return Response(response_data, status=status.HTTP_200_OK)

class UserProfileViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for viewing authenticated user's details.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="View user profile",
        description="Allows an authenticated user to view their own details, including "
                    "user information and vendor profile (if applicable).",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "User profile response (regular user)",
                value={
                    "user": {
                        "id": 1,
                        "username": "john_doe",
                        "email": "john@example.com",
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_vendor": False
                    },
                    "vendor_profile": None
                },
                description="Example response for a regular user"
            ),
            OpenApiExample(
                "User profile response (vendor)",
                value={
                    "user": {
                        "id": 2,
                        "username": "vendor1",
                        "email": "vendor@example.com",
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "is_vendor": True
                    },
                    "vendor_profile": {
                        "business_name": "Vendor Shop",
                        "description": "Quality clothing and accessories",
                        "domain": "CB",
                        "shed_number": 1,
                        "payment_status": "COMPLETED",
                        "payment_reference": "tx_ref_123"
                    }
                },
                description="Example response for a vendor"
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_vendor': user.is_vendor
            },
            'vendor_profile': None
        }
        if user.is_vendor:
            vendor_profile = user.vendor_profile
            response_data['vendor_profile'] = VendorProfileSerializer(vendor_profile).data
        return Response(response_data, status=status.HTTP_200_OK)

class UserDeleteViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for deleting authenticated user's account.
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Delete user account",
        description="Allows an authenticated user to delete their own account. "
                    "If the user is a vendor, their associated VendorProfile is also deleted "
                    "due to CASCADE deletion.",
        responses={
            204: None,
            401: OpenApiTypes.OBJECT
        },
        examples=[
            OpenApiExample(
                "Delete account response",
                value={},
                description="Successful deletion returns no content"
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    