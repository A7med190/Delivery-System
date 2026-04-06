from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('order_placed', 'Order Placed'),
        ('order_confirmed', 'Order Confirmed'),
        ('order_preparing', 'Order Preparing'),
        ('order_ready', 'Order Ready'),
        ('order_picked_up', 'Order Picked Up'),
        ('order_delivered', 'Order Delivered'),
        ('order_cancelled', 'Order Cancelled'),
        ('payment_received', 'Payment Received'),
        ('review_request', 'Review Request'),
        ('promotion', 'Promotion'),
        ('system', 'System'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.email}"

    @classmethod
    def send(cls, user, notification_type, title, message, data=None):
        return cls.objects.create(
            user=user,
            type=notification_type,
            title=title,
            message=message,
            data=data or {}
        )


class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preference')
    order_placed = models.BooleanField(default=True)
    order_confirmed = models.BooleanField(default=True)
    order_preparing = models.BooleanField(default=True)
    order_ready = models.BooleanField(default=True)
    order_picked_up = models.BooleanField(default=True)
    order_delivered = models.BooleanField(default=True)
    order_cancelled = models.BooleanField(default=True)
    payment_received = models.BooleanField(default=True)
    review_request = models.BooleanField(default=True)
    promotion = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"
