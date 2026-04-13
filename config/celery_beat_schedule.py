from django.conf import settings
from celery import Celery
from celery.beat import PeriodicTask, PeriodicTasks
import pytz

app = Celery('delivery_system')

CELERYBEAT_SCHEDULE = {
    'process-outbox-messages': {
        'task': 'apps.core.tasks.process_outbox_messages',
        'schedule': 5.0,
        'options': {'queue': 'default'},
    },
    'retry-failed-outbox': {
        'task': 'apps.core.tasks.retry_failed_outbox_messages',
        'schedule': 60.0,
        'options': {'queue': 'default'},
    },
    'cleanup-old-outbox': {
        'task': 'apps.core.tasks.cleanup_old_outbox_messages',
        'schedule': 3600.0,
        'options': {'queue': 'default'},
    },
    'retry-failed-webhooks': {
        'task': 'apps.core.tasks.retry_failed_webhooks',
        'schedule': 300.0,
        'options': {'queue': 'default'},
    },
}
