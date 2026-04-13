from django.core.management.base import BaseCommand

from apps.core.outbox import OutboxProcessor


class Command(BaseCommand):
    help = 'Process pending outbox messages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of messages to process per batch',
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Interval between batches in seconds (for continuous mode)',
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        continuous = options['continuous']
        interval = options['interval']

        processor = OutboxProcessor(batch_size=batch_size)

        if continuous:
            self.stdout.write(f'Starting continuous outbox processing (batch size: {batch_size})')
            import time
            try:
                while True:
                    processed = processor.process_pending()
                    if processed:
                        self.stdout.write(f'Processed {processed} messages')
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Stopped outbox processor'))
        else:
            processed = processor.process_pending()
            self.stdout.write(self.style.SUCCESS(f'Processed {processed} messages'))
