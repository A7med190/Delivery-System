from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def update_order_totals(sender, instance, created, **kwargs):
    if created:
        subtotal = sum(item.total_price for item in instance.items.all())
        instance.subtotal = subtotal
        instance.save()
