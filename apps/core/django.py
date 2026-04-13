"""
Django app configuration for core.
"""
from django.apps import AppConfig
from django.db.models.signals import post_migrate


def setup_health_check_celery(sender, **kwargs):
    pass


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core Utilities'

    def ready(self):
        from apps.core.shutdown import setup_graceful_shutdown
        from apps.core.signals import setup_signals
        
        setup_graceful_shutdown()
        setup_signals()
