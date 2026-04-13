"""
Django signals for the Delivery System.
"""
import logging
from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    if hasattr(instance, '__log_name__'):
        action = 'created' if created else 'updated'
        logger.info(f'{instance.__log_name__} {instance.pk} {action}')


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    if hasattr(instance, '__log_name__'):
        logger.info(f'{instance.__log_name__} {instance.pk} deleted')


def setup_signals():
    """
    Initialize any signal connections that need to be set up at startup.
    """
    logger.info('Django signals initialized')
