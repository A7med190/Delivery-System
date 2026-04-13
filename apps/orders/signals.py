from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def create_delivery_record(sender, instance, created, **kwargs):
    if created and instance.status != 'cancelled':
        from apps.delivery.models import Delivery
        Delivery.objects.get_or_create(
            order=instance,
            defaults={
                'status': 'pending',
                'tracking_number': f'DEL-{instance.order_number}'
            }
        )
