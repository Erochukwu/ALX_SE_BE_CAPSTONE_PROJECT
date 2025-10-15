"""
Models for the payments app in the TradeFair project.

Defines models for handling payment transactions, including payments for preorders
and vendor payments for sheds.
"""

from django.db import models
from orders.models import Preorder
from vendors.models import Shed

class Payment(models.Model):
    """
    Model representing a payment transaction for a preorder.

    Attributes:
        preorder (ForeignKey): The Preorder associated with the payment.
        amount (DecimalField): The payment amount in the local currency.
        reference (CharField): The unique Paystack transaction reference.
        status (CharField): The status of the payment (pending, success, failed).
        created_at (DateTimeField): Timestamp of payment creation.
        updated_at (DateTimeField): Timestamp of last update.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    preorder = models.ForeignKey(
        Preorder,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="The preorder associated with this payment."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The payment amount in the local currency."
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
        help_text="The unique Paystack transaction reference."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of the payment (pending, success, or failed)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the payment was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the payment was last updated."
    )

    class Meta:
        """
        Meta options for the Payment model.

        Attributes:
            verbose_name (str): Singular name for the model.
            verbose_name_plural (str): Plural name for the model.
        """
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        """
        Provide a string representation of the Payment instance.

        Returns:
            str: Description of the payment, including preorder and amount.
        """
        return f"Payment for Preorder {self.preorder.id} - {self.amount}"

class VendorPayment(models.Model):
    """
    Model representing a payment transaction for a vendor's shed.

    Attributes:
        shed (ForeignKey): The Shed associated with the payment.
        amount (DecimalField): The payment amount in the local currency.
        reference (CharField): The unique Paystack transaction reference.
        status (CharField): The status of the payment (pending, success, failed).
        created_at (DateTimeField): Timestamp of payment creation.
        updated_at (DateTimeField): Timestamp of last update.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]

    shed = models.ForeignKey(
        Shed,
        on_delete=models.CASCADE,
        related_name='vendor_payments',
        help_text="The shed associated with this payment."
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="The payment amount in the local currency."
    )
    reference = models.CharField(
        max_length=100,
        unique=True,
        help_text="The unique Paystack transaction reference."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="The current status of the payment (pending, success, or failed)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the payment was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the payment was last updated."
    )

    class Meta:
        """
        Meta options for the VendorPayment model.

        Attributes:
            verbose_name (str): Singular name for the model.
            verbose_name_plural (str): Plural name for the model.
        """
        verbose_name = "Vendor Payment"
        verbose_name_plural = "Vendor Payments"

    def __str__(self):
        """
        Provide a string representation of the VendorPayment instance.

        Returns:
            str: Description of the payment, including shed and amount.
        """
        return f"Payment for Shed {self.shed.id} - {self.amount}"