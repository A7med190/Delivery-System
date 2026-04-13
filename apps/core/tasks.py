"""
Celery tasks for the Delivery System.
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_outbox_messages(self):
    """
    Periodic task to process pending outbox messages.
    """
    from apps.core.outbox import OutboxProcessor
    
    try:
        processor = OutboxProcessor()
        processed = processor.process_pending()
        logger.info(f'Processed {processed} outbox messages')
        return {'processed': processed}
    except Exception as e:
        logger.error(f'Error processing outbox messages: {e}')
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True, max_retries=3)
def retry_failed_outbox_messages(self):
    """
    Periodic task to retry failed outbox messages.
    """
    from apps.core.outbox import OutboxProcessor
    
    try:
        processor = OutboxProcessor()
        retried = processor.retry_failed()
        logger.info(f'Retried {retried} failed outbox messages')
        return {'retried': retried}
    except Exception as e:
        logger.error(f'Error retrying failed outbox messages: {e}')
        raise self.retry(exc=e, countdown=300)


@shared_task(bind=True, max_retries=3)
def cleanup_old_outbox_messages(self):
    """
    Periodic task to cleanup old processed outbox messages.
    """
    from apps.core.outbox import OutboxProcessor
    
    try:
        processor = OutboxProcessor()
        cleaned = processor.cleanup_old_messages(days=30)
        logger.info(f'Cleaned up {cleaned} old outbox messages')
        return {'cleaned': cleaned}
    except Exception as e:
        logger.error(f'Error cleaning up outbox messages: {e}')
        raise self.retry(exc=e, countdown=3600)


@shared_task(bind=True, max_retries=3)
def retry_failed_webhooks(self):
    """
    Periodic task to retry failed webhooks.
    """
    from apps.core.webhooks import WebhookService
    
    try:
        service = WebhookService()
        retried = service.retry_failed_webhooks()
        logger.info(f'Retried {retried} failed webhooks')
        return {'retried': retried}
    except Exception as e:
        logger.error(f'Error retrying failed webhooks: {e}')
        raise self.retry(exc=e, countdown=300)


@shared_task
def send_order_notification(order_id: int, event_type: str):
    """
    Send notification for order events.
    """
    from apps.core.services import notification_service
    
    try:
        result = notification_service.send_push_notification(
            user_id=order_id,
            title=f'Order Update',
            body=f'Your order has been {event_type}',
        )
        return result
    except Exception as e:
        logger.error(f'Error sending order notification: {e}')
        raise


@shared_task
def process_delivery_location_update(driver_id: int, lat: float, lon: float):
    """
    Process driver location update and broadcast via SSE.
    """
    from apps.core.sse import broadcast_sse
    
    try:
        broadcast_sse(
            channel=f'driver_{driver_id}',
            event_type='location_update',
            data={'driver_id': driver_id, 'lat': lat, 'lon': lon, 'timestamp': timezone.now().isoformat()},
        )
    except Exception as e:
        logger.error(f'Error broadcasting location update: {e}')
        raise
