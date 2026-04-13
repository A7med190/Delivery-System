from django.apps import AppConfig


class CeleryBeatConfig(AppConfig):
    name = 'django_celery_beat'
    verbose_name = 'Celery Beat'

    def ready(self):
        pass
