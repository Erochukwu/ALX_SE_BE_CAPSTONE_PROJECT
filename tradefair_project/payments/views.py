"""
API views for the payments app in the TradeFair project.

Handles payment initiation and verification for sheds using Paystack.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.conf import settings
from paystackapi.transaction import Transaction
from vendors.models import Shed
from .models import VendorPayment
import time

class InitiateShedPayment(APIView):
    """
    API endpoint to initiate a payment for securing a shed.

    POST /api/payments/initiate-shed/{shed_id}/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, shed_id):
        try:
            shed = Shed.objects.get(id=shed_id)
        except Shed.DoesNotExist:
            return Response({"error": "Shed not found"}, status=status.HTTP_404_NOT_FOUND)

        if not hasattr(request.user, 'vendor_profile') or shed.vendor != request.user.vendor_profile:
            return Response({"error": "You can only initiate payment for your own shed"}, status=status.HTTP_403_FORBIDDEN)

        if shed.secured:
            return Response({"error": "Shed is already secured"}, status=status.HTTP_400_BAD_REQUEST)

        amount = request.data.get('amount')
        if not amount or float(amount) <= 0:
            return Response({"error": "Valid amount is required"}, status=status.HTTP_400_BAD_REQUEST)

        amount_kobo = int(float(amount) * 100)
        response = Transaction.initialize(
            reference=f"shed_{shed.id}_{request.user.id}_{int(time.time())}",
            amount=amount_kobo,
            email=request.user.email,
            callback_url=f"{settings.SITE_URL}/api/payments/verify-shed/{shed.id}/"
        )

        if response['status']:
            vendor_payment = VendorPayment.objects.create(
                shed=shed,
                amount=amount,
                reference=response['data']['reference'],
                status='pending'
            )
            return Response({
                "message": "Payment initiated successfully",
                "authorization_url": response['data']['authorization_url'],
                "reference": response['data']['reference']
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": response['message']}, status=status.HTTP_400_BAD_REQUEST)

class PaystackWebhook(APIView):
    """
    API endpoint for Paystack webhook to handle payment events.

    POST /api/payments/webhook/
    """
    permission_classes = [AllowAny]

    def post(self, request):
        event = request.data.get('event')
        data = request.data.get('data')
        if event == 'charge.success' and data.get('status') == 'success':
            reference = data.get('reference')
            try:
                vendor_payment = VendorPayment.objects.get(reference=reference)
                vendor_payment.status = 'success'
                vendor_payment.shed.secured = True
                vendor_payment.shed.save()
                vendor_payment.save()
                return Response({"message": "Payment verified"}, status=status.HTTP_200_OK)
            except VendorPayment.DoesNotExist:
                return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid event or status"}, status=status.HTTP_400_BAD_REQUEST)