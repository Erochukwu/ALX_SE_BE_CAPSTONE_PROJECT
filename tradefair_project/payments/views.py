# payments/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from paystackapi.transaction import Transaction
import json
from payments.models import VendorPayment, Payment
from vendors.models import Shed

@login_required
def initiate_shed_payment(request, shed_id):
    """Initiate payment for a shed using Paystack."""
    try:
        shed = Shed.objects.get(id=shed_id, vendor__user=request.user)
    except Shed.DoesNotExist:
        return render(request, 'payments/error.html', {'error': 'Shed not found or not authorized', 'shed': {'id': shed_id}})
    
    if request.method == 'GET':
        return render(request, 'payments/initiate_shed.html', {'shed': shed})
    
    amount = 10000 * 100  # Convert to kobo
    email = request.user.email
    response = Transaction.initialize(
        reference=f'shed_{shed.id}_{request.user.id}',
        amount=amount,
        email=email,
        callback_url='http://localhost:8000/api/payments/paystack_webhook/'
    )

    if response['status']:
        VendorPayment.objects.create(
            vendor=shed.vendor,
            shed=shed,
            amount=10000.00,
            reference=response['data']['reference'],
            status='pending'
        )
        return redirect(response['data']['authorization_url'])
    else:
        return render(request, 'payments/error.html', {'error': response['message'], 'shed': shed})

@csrf_exempt
def paystack_webhook(request):
    """Handle Paystack webhook for payment verification."""
    if request.method != 'POST':
        return HttpResponse(status=405)
    
    payload = json.loads(request.body)
    event = payload.get('event')
    data = payload.get('data')
    
    if event == 'charge.success':
        reference = data.get('reference')
        try:
            vendor_payment = VendorPayment.objects.get(reference=reference)
            vendor_payment.status = 'success'
            vendor_payment.shed.secured = True
            vendor_payment.shed.save()
            vendor_payment.save()
            return HttpResponse(status=200)
        except VendorPayment.DoesNotExist:
            try:
                payment = Payment.objects.get(reference=reference)
                payment.status = 'completed'
                payment.save()
                return HttpResponse(status=200)
            except Payment.DoesNotExist:
                return HttpResponse(status=400)
    
    return HttpResponse(status=400)