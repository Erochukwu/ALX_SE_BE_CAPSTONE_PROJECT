# payments/views.py
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from paystackapi.transaction import Transaction
import json
from payments.models import VendorPayment, Payment
from vendors.models import Shed
from users.models import VendorProfile

def initiate_shed_payment(request, shed_id):
    shed = Shed.objects.get(id=shed_id)
    if request.method == 'POST':
        amount = 10000  # Example amount in kobo
        email = request.user.email
        reference = f"shed_{shed.id}_{request.user.id}"

        response = Transaction.initialize(
            reference=reference,
            amount=amount * 100,
            email=email,
            key=settings.PAYSTACK_SECRET_KEY
        )

        if response['status']:
            VendorPayment.objects.create(
                vendor=shed.vendor,  # Now VendorProfile
                shed=shed,
                amount=amount,
                reference=reference,
                status='pending'
            )
            return redirect(response['data']['authorization_url'])
        else:
            return render(request, 'payments/error.html', {'error': response['message']})

    return render(request, 'payments/initiate_shed.html', {'shed': shed})

@csrf_exempt
def paystack_webhook(request):
    if request.method == 'POST':
        payload = request.body.decode('utf-8')
        event = json.loads(payload)
        
        if event['event'] == 'charge.success':
            reference = event['data']['reference']
            try:
                vendor_payment = VendorPayment.objects.get(reference=reference)
                vendor_payment.status = 'success'
                vendor_payment.save()
                vendor_payment.shed.secured = True
                vendor_payment.shed.save()
            except VendorPayment.DoesNotExist:
                try:
                    payment = Payment.objects.get(reference=reference)
                    payment.status = 'completed'
                    payment.save()
                except Payment.DoesNotExist:
                    pass  # Log error if needed
        
        return HttpResponse(status=200)
    return HttpResponse(status=400)
