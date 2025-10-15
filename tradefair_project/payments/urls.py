"""
URL configuration for the payments app in the TradeFair project.
"""

from django.urls import path
from .views import InitiateShedPayment, PaystackWebhook

urlpatterns = [
    path('initiate-shed/<int:shed_id>/', InitiateShedPayment.as_view(), name='initiate_shed_payment'),
    path('webhook/', PaystackWebhook.as_view(), name='paystack_webhook'),
]