from django.db import models
from django.conf import settings


class Delivery(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    )

    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='deliveries'
    )
    tracking_number = models.CharField(max_length=50, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_time = models.DateTimeField(null=True, blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_notes = models.TextField(blank=True, default='')
    signature_image = models.ImageField(upload_to='signatures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'deliveries'
        ordering = ['-created_at']

    def __str__(self):
        return f"Delivery {self.tracking_number} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            import uuid
            self.tracking_number = f"TRK-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class DeliveryLocation(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name='locations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    accuracy = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_locations'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Location for {self.delivery.tracking_number} at {self.recorded_at}"
