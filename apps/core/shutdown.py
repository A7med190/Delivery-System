import logging
import signal
import sys
from typing import Callable, List

from django.apps import apps
from django.db import connection

logger = logging.getLogger(__name__)


class GracefulShutdown:
    def __init__(self):
        self.shutdown_in_progress = False
        self.callbacks: List[Callable] = []

    def register(self, callback: Callable) -> None:
        self.callbacks.append(callback)

    def shutdown(self, signum, frame):
        if self.shutdown_in_progress:
            return

        self.shutdown_in_progress = True
        logger.info(f'Received signal {signum}, initiating graceful shutdown...')

        for callback in self.callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f'Error in shutdown callback: {e}')

        self._close_db_connections()
        logger.info('Graceful shutdown complete')
        sys.exit(0)

    def _close_db_connections(self):
        connection.close()


shutdown_handler = GracefulShutdown()


def setup_graceful_shutdown():
    signals = [signal.SIGTERM, signal.SIGINT, signal.SIGABRT]

    for sig in signals:
        try:
            signal.signal(sig, shutdown_handler.shutdown)
        except (OSError, ValueError):
            pass

    shutdown_handler.register(_close_celery_connections)
    shutdown_handler.register(_flush_outbox)
    shutdown_handler.register(_cancel_pending_tasks)

    logger.info('Graceful shutdown handlers registered')


def _close_celery_connections():
    try:
        from config.celery import app
        app.control.shutdown()
        logger.info('Celery connections closed')
    except Exception as e:
        logger.warning(f'Could not close Celery connections: {e}')


def _flush_outbox():
    try:
        from apps.core.outbox import OutboxProcessor
        processor = OutboxProcessor()
        processed = processor.process_pending(batch_size=50)
        logger.info(f'Flushed {processed} outbox messages during shutdown')
    except Exception as e:
        logger.warning(f'Could not flush outbox: {e}')


def _cancel_pending_tasks():
    try:
        from config.celery import app
        inspector = app.control.inspect()
        active_tasks = inspector.active()
        if active_tasks:
            logger.info(f'Found {len(active_tasks)} active tasks')
    except Exception as e:
        logger.warning(f'Could not cancel pending tasks: {e}')


def request_shutdown():
    shutdown_handler.shutdown(signal.SIGTERM, None)
