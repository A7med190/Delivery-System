import time

from django.http import HttpRequest, HttpResponse


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        import logging
        import uuid

        logger = logging.getLogger(__name__)
        start_time = time.time()
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        logger.info(
            f'Request started: {request.method} {request.path}',
            extra={'request_id': request_id}
        )

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(
            f'Request completed: {request.method} {request.path} {response.status_code} in {duration:.3f}s',
            extra={
                'request_id': request_id,
                'status_code': response.status_code,
                'duration': duration,
            }
        )

        response['X-Request-ID'] = request_id
        return response
