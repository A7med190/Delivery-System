from django.core.management.base import BaseCommand

from apps.core.outbox import OutboxProcessor
from apps.core.webhooks import WebhookService


class Command(BaseCommand):
    help = 'Retry failed outbox messages and webhooks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--webhooks',
            action='store_true',
            help='Only retry failed webhooks',
        )
        parser.add_argument(
            '--outbox',
            action='store_true',
            help='Only retry failed outbox messages',
        )
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Cleanup old outbox messages',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to keep old messages (for cleanup)',
        )

    def handle(self, *args, **options):
        if options['webhooks']:
            self.retry_webhooks()
        elif options['outbox']:
            self.retry_outbox()
        elif options['cleanup']:
            self.cleanup_outbox(options['days'])
        else:
            self.retry_webhooks()
            self.retry_outbox()

    def retry_webhooks(self):
        service = WebhookService()
        retried = service.retry_failed_webhooks()
        self.stdout.write(self.style.SUCCESS(f'Retried {retried} webhooks'))

    def retry_outbox(self):
        processor = OutboxProcessor()
        retried = processor.retry_failed()
        self.stdout.write(self.style.SUCCESS(f'Reset {retried} outbox messages for retry'))

    def cleanup_outbox(self, days):
        processor = OutboxProcessor()
        cleaned = processor.cleanup_old_messages(days=days)
        self.stdout.write(self.style.SUCCESS(f'Cleaned up {cleaned} old messages'))
