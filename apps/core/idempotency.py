import hashlib
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Optional

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class IdempotencyStore:
    def __init__(self, prefix: str = None):
        self.prefix = prefix or getattr(settings, 'IDEMPOTENCY_CACHE_PREFIX', 'idempotency:')

    def _make_key(self, key: str) -> str:
        return f'{self.prefix}{key}'

    def get(self, key: str) -> Optional[dict]:
        data = cache.get(self._make_key(key))
        if data:
            return json.loads(data)
        return None

    def set(self, key: str, response_data: dict, expiry: int = None) -> None:
        expiry = expiry or getattr(settings, 'IDEMPOTENCY_EXPIRY_SECONDS', 86400)
        cache.set(
            self._make_key(key),
            json.dumps(response_data),
            timeout=expiry,
        )

    def delete(self, key: str) -> None:
        cache.delete(self._make_key(key))


class IdempotentOperation:
    def __init__(self, store: IdempotencyStore = None):
        self.store = store or IdempotencyStore()

    def get_or_create_response(self, idempotency_key: str, operation: Callable, *args, **kwargs) -> Any:
        cached = self.store.get(idempotency_key)
        if cached:
            logger.debug(f'Idempotency hit for key: {idempotency_key}')
            return cached

        result = operation(*args, **kwargs)

        response_data = {
            'result': result,
            'timestamp': datetime.utcnow().isoformat(),
        }
        self.store.set(idempotency_key, response_data)

        return result


def generate_idempotency_key(request: HttpRequest) -> str:
    key = getattr(settings, 'IDEMPOTENCY_KEY_HEADER', 'HTTP_X_IDEMPOTENCY_KEY')
    provided_key = request.META.get(key)
    if provided_key:
        return hashlib.sha256(provided_key.encode()).hexdigest()
    return hashlib.sha256(f'{request.path}:{uuid.uuid4()}'.encode()).hexdigest()


class IdempotencyMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.store = IdempotencyStore()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method not in ('POST', 'PUT', 'PATCH'):
            return self.get_response(request)

        idempotency_key = request.META.get(
            getattr(settings, 'IDEMPOTENCY_KEY_HEADER', 'HTTP_X_IDEMPOTENCY_KEY')
        )

        if not idempotency_key:
            return self.get_response(request)

        cache_key = hashlib.sha256(idempotency_key.encode()).hexdigest()
        cached_response = self.store.get(cache_key)

        if cached_response:
            logger.info(f'Returning cached idempotent response for key: {idempotency_key}')
            response = HttpResponse(
                content=json.dumps(cached_response.get('result', {})),
                content_type='application/json',
                status=cached_response.get('status', 200),
            )
            response['X-Idempotency-Replayed'] = 'true'
            return response

        request._idempotency_key = cache_key
        response = self.get_response(request)

        if response.status_code < 400:
            try:
                response_data = {
                    'result': json.loads(response.content.decode()),
                    'status': response.status_code,
                    'timestamp': datetime.utcnow().isoformat(),
                }
                self.store.set(cache_key, response_data)
            except (json.JSONDecodeError, AttributeError):
                pass

        return response
