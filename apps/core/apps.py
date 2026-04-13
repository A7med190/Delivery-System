from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    verbose_name = 'Core Utilities'

    def ready(self):
        import apps.core.signals  # noqa
        from apps.core.shutdown import setup_graceful_shutdown
        setup_graceful_shutdown()
