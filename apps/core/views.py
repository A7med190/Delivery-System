import asyncio
import json
import logging
from typing import Any

from asgiref.sync import sync_to_async
from django.http import HttpRequest, HttpResponse
from rest_framework.views import APIView

from apps.core.health import run_health_checks
from apps.core.sse import SSEManager, broadcast_sse

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request: HttpRequest) -> HttpResponse:
        health_data = run_health_checks()
        status_code = 200 if health_data.get('status') == 'healthy' else 503
        return HttpResponse(
            json.dumps(health_data),
            content_type='application/json',
            status=status_code,
        )


def sse_event_generator(queue):
    import asyncio
    try:
        while True:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                message = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=30))
                yield f'event: {message.get("type", "message")}\ndata: {json.dumps(message.get("data", {}))}\n\n'
            except asyncio.TimeoutError:
                yield f': keepalive\n\n'
    except GeneratorExit:
        pass


class SSEOrderView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request: HttpRequest, order_id: str) -> HttpResponse:
        client_id = f'order_{order_id}_{id(request)}'
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue = loop.run_until_complete(SSEManager.add_client(client_id))

        def event_stream():
            try:
                while True:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        message = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=30))
                        yield f'event: {message.get("type", "message")}\ndata: {json.dumps(message.get("data", {}))}\n\n'
                    except asyncio.TimeoutError:
                        yield f': keepalive\n\n'
            except GeneratorExit:
                loop.run_until_complete(SSEManager.remove_client(client_id))

        response = HttpResponse(
            event_stream(),
            content_type='text/event-stream',
            status=200,
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class SSENotificationsView(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request: HttpRequest, user_id: int) -> HttpResponse:
        client_id = f'notifications_{user_id}_{id(request)}'
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        queue = loop.run_until_complete(SSEManager.add_client(client_id))

        def event_stream():
            try:
                while True:
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        message = loop.run_until_complete(asyncio.wait_for(queue.get(), timeout=30))
                        yield f'event: {message.get("type", "message")}\ndata: {json.dumps(message.get("data", {}))}\n\n'
                    except asyncio.TimeoutError:
                        yield f': keepalive\n\n'
            except GeneratorExit:
                loop.run_until_complete(SSEManager.remove_client(client_id))

        response = HttpResponse(
            event_stream(),
            content_type='text/event-stream',
            status=200,
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
