from django.db import models
from django.conf import settings


class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    )

    METHOD_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash on Delivery'),
        ('wallet', 'Digital Wallet'),
        ('bank_transfer', 'Bank Transfer'),
    )

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, default='')
    payment_reference = models.CharField(max_length=100, unique=True, editable=False)
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_reference} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            import uuid
            self.payment_reference = f"PAY-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)
