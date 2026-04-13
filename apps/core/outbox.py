import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class OutboxMessage(models.Model):
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='pending',
        db_index=True,
    )
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    last_error = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'outbox_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f'{self.event_type} - {self.status}'


def create_outbox_message(event_type: str, payload: Dict[str, Any], **kwargs) -> OutboxMessage:
    return OutboxMessage.objects.create(
        event_type=event_type,
        payload=payload,
        **kwargs,
    )


def emit_event(event_type: str, payload: Dict[str, Any], **kwargs) -> OutboxMessage:
    return create_outbox_message(event_type, payload, **kwargs)


class OutboxProcessor:
    def __init__(self, batch_size: int = None, max_retries: int = None):
        self.batch_size = batch_size or getattr(settings, 'OUTBOX_PROCESSOR_BATCH_SIZE', 100)
        self.max_retries = max_retries or 3

    def process_pending(self, batch_size: int = None) -> int:
        batch_size = batch_size or self.batch_size
        processed = 0

        messages = OutboxMessage.objects.filter(
            status='pending'
        ).order_by('created_at')[:batch_size]

        for message in messages:
            self._process_message(message)
            processed += 1

        return processed

    def _process_message(self, message: OutboxMessage) -> None:
        try:
            message.status = 'processing'
            message.save(update_fields=['status'])

            self._deliver_message(message)

            message.status = 'sent'
            message.processed_at = timezone.now()
            message.save(update_fields=['status', 'processed_at'])

            logger.info(f'Outbox message {message.id} processed successfully')

        except Exception as e:
            message.retry_count += 1
            message.last_error = str(e)

            if message.retry_count >= message.max_retries:
                message.status = 'failed'
                logger.error(f'Outbox message {message.id} failed permanently: {e}')
            else:
                message.status = 'pending'
                logger.warning(f'Outbox message {message.id} failed, retry {message.retry_count}: {e}')

            message.save()

    def _deliver_message(self, message: OutboxMessage) -> None:
        from apps.core.webhooks import WebhookService
        webhook_service = WebhookService()
        webhook_service.send_webhook(
            event_type=message.event_type,
            payload=message.payload,
        )

    def retry_failed(self) -> int:
        failed_messages = OutboxMessage.objects.filter(
            status='failed',
            retry_count__lt=models.F('max_retries'),
        )
        count = failed_messages.update(status='pending', retry_count=0)
        logger.info(f'Reset {count} failed outbox messages for retry')
        return count

    def cleanup_old_messages(self, days: int = 30) -> int:
        cutoff = timezone.now() - timezone.timedelta(days=days)
        count, _ = OutboxMessage.objects.filter(
            status='sent',
            processed_at__lt=cutoff,
        ).delete()
        logger.info(f'Cleaned up {count} old outbox messages')
        return count
