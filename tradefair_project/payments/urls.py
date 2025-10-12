# payments/urls.py
from django.urls import path, include
from .views import initiate_shed_payment, paystack_webhook

urlpatterns = [
    path('initiate-shed/<int:shed_id>/', initiate_shed_payment, name='initiate_shed_payment'),
    path('webhook/', paystack_webhook, name='paystack_webhook'),
    path('orders/', include('orders.urls')),
]