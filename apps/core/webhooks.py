import hashlib
import hmac
import json
import logging
import time
from typing import Any, Callable, Dict, List, Optional

import requests
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class Webhook(models.Model):
    url = models.URLField(max_length=2048)
    event_types = models.JSONField(default=list)
    secret = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'webhooks'

    def __str__(self):
        return f'{self.url} - {self.event_types}'


class WebhookDelivery(models.Model):
    webhook = models.ForeignKey(Webhook, on_delete=models.CASCADE, related_name='deliveries')
    event_type = models.CharField(max_length=255)
    payload = models.JSONField()
    response_status = models.IntegerField(null=True)
    response_body = models.TextField(blank=True)
    attempt = models.IntegerField(default=1)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webhook_deliveries'
        ordering = ['-created_at']


class WebhookService:
    def __init__(self):
        self.timeout = getattr(settings, 'WEBHOOK_DELIVERY_TIMEOUT', 30)
        self.max_retries = getattr(settings, 'WEBHOOK_MAX_RETRIES', 3)

    def _generate_signature(self, payload: str, secret: str) -> str:
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    def _deliver(self, webhook: Webhook, event_type: str, payload: Dict) -> bool:
        from django.utils import timezone
        import requests

        payload_str = json.dumps(payload, default=str)
        signature = self._generate_signature(payload_str, webhook.secret) if webhook.secret else None

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'DeliverySystem-Webhook/1.0',
            'X-Webhook-Event': event_type,
            'X-Webhook-Timestamp': str(int(time.time())),
        }
        if signature:
            headers['X-Webhook-Signature'] = f'sha256={signature}'

        try:
            response = requests.post(
                webhook.url,
                data=payload_str,
                headers=headers,
                timeout=self.timeout,
            )

            delivery = WebhookDelivery.objects.create(
                webhook=webhook,
                event_type=event_type,
                payload=payload,
                response_status=response.status_code,
                response_body=response.text[:1000],
                delivered_at=timezone.now(),
            )

            return 200 <= response.status_code < 300

        except requests.RequestException as e:
            WebhookDelivery.objects.create(
                webhook=webhook,
                event_type=event_type,
                payload=payload,
                response_body=str(e)[:1000],
            )
            logger.error(f'Webhook delivery failed for {webhook.url}: {e}')
            return False

    def send_webhook(self, event_type: str, payload: Dict, webhook_id: int = None) -> List[Dict]:
        results = []

        if webhook_id:
            webhooks = [Webhook.objects.get(id=webhook_id)]
        else:
            webhooks = Webhook.objects.filter(is_active=True, event_types__contains=[event_type])

        for webhook in webhooks:
            success = self._deliver(webhook, event_type, payload)
            results.append({
                'webhook_id': webhook.id,
                'url': webhook.url,
                'success': success,
            })

            if not success:
                webhook.retry_count += 1
                if webhook.retry_count >= webhook.max_retries:
                    webhook.is_active = False
                webhook.save(update_fields=['retry_count', 'is_active', 'updated_at'])

        return results

    def retry_failed_webhooks(self) -> int:
        failed_webhooks = Webhook.objects.filter(is_active=False, retry_count__lt=models.F('max_retries'))
        count = failed_webhooks.update(is_active=True)
        logger.info(f'Reactivated {count} failed webhooks')
        return count
