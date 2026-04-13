import hashlib
import json
import logging
import time
import uuid
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse

logger = logging.getLogger(__name__)


class IdempotencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.prefix = getattr(settings, 'IDEMPOTENCY_CACHE_PREFIX', 'idempotency:')
        self.expiry = getattr(settings, 'IDEMPOTENCY_EXPIRY_SECONDS', 86400)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if request.method not in ('POST', 'PUT', 'PATCH'):
            return self.get_response(request)

        idempotency_key = request.META.get(
            getattr(settings, 'IDEMPOTENCY_KEY_HEADER', 'HTTP_X_IDEMPOTENCY_KEY')
        )

        if not idempotency_key:
            return self.get_response(request)

        cache_key = f'{self.prefix}{hashlib.sha256(idempotency_key.encode()).hexdigest()}'
        cached = cache.get(cache_key)

        if cached:
            logger.info(f'Idempotency hit for key: {idempotency_key}')
            response = JsonResponse(cached.get('response', {}))
            response['X-Idempotency-Replayed'] = 'true'
            return response

        request._idempotency_key = cache_key
        response = self.get_response(request)

        if 200 <= response.status_code < 300:
            try:
                cache.set(
                    cache_key,
                    {
                        'response': json.loads(response.content.decode()) if response.content else {},
                        'timestamp': datetime.utcnow().isoformat(),
                    },
                    timeout=self.expiry,
                )
            except (json.JSONDecodeError, AttributeError):
                pass

        return response


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        import time
        start_time = time.time()
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(
            f'{request.method} {request.path} {response.status_code} {duration:.3f}s',
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user_id': getattr(request.user, 'id', None),
                'ip': self._get_client_ip(request),
            }
        )

        response['X-Request-ID'] = request_id
        return response

    def _get_client_ip(self, request: HttpRequest) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
