from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.delivery.models import Delivery
from apps.notifications.models import Notification


@receiver(post_save, sender=Delivery)
def delivery_status_changed(sender, instance, created, **kwargs):
    if not created:
        old_status = Delivery.objects.filter(pk=instance.pk).first()
        if old_status and old_status.status != instance.status:
            Notification.objects.create(
                user=instance.order.customer,
                type='delivery_update',
                title=f'Delivery {instance.status.title()}',
                message=f'Your order is now {instance.status}',
                related_object_id=str(instance.id)
            )