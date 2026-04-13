import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any, Optional

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class SSELifetime:
    CLEANUP_INTERVAL = 30
    MAX_CLIENTS = 1000


class SSEManager:
    _clients: Dict[str, asyncio.Queue] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def add_client(cls, client_id: str) -> asyncio.Queue:
        async with cls._lock:
            queue = asyncio.Queue(maxsize=100)
            cls._clients[client_id] = queue
            if len(cls._clients) > SSELifetime.MAX_CLIENTS:
                oldest = next(iter(cls._clients))
                await cls.remove_client(oldest)
            return queue

    @classmethod
    async def remove_client(cls, client_id: str):
        async with cls._lock:
            if client_id in cls._clients:
                del cls._clients[client_id]

    @classmethod
    async def broadcast(cls, channel: str, event_type: str, data: Dict[str, Any]):
        async with cls._lock:
            clients_to_remove = []
            for client_id, queue in cls._clients.items():
                try:
                    message = {
                        'channel': channel,
                        'type': event_type,
                        'data': data,
                    }
                    await asyncio.wait_for(queue.put(message), timeout=1)
                except asyncio.queues.QueueFull:
                    clients_to_remove.append(client_id)
                except Exception:
                    clients_to_remove.append(client_id)

            for client_id in clients_to_remove:
                await cls.remove_client(client_id)

    @classmethod
    async def get_clients_count(cls, channel: str = None) -> int:
        async with cls._lock:
            if channel:
                return sum(1 for c in cls._clients if c.startswith(f'{channel}_'))
            return len(cls._clients)


class SSEConsumer(AsyncWebsocketConsumer):
    CHANNEL = 'sse'
    KEEPALIVE_INTERVAL = 30

    async def connect(self):
        await self.accept()
        self.client_id = f'{self.CHANNEL}_{id(self)}'
        self.queue = await SSEManager.add_client(self.client_id)
        self._task = asyncio.create_task(self._stream())
        self._keepalive_task = asyncio.create_task(self._keepalive())
        await self.send(text_data=self._event_formatter('connected', {'status': 'ok'}))

    async def disconnect(self, close_code):
        if hasattr(self, '_task'):
            self._task.cancel()
        if hasattr(self, '_keepalive_task'):
            self._keepalive_task.cancel()
        await SSEManager.remove_client(self.client_id)

    async def _stream(self):
        try:
            while True:
                message = await asyncio.wait_for(self.queue.get(), timeout=60)
                await self.send(text_data=self._event_formatter(
                    message.get('type', 'message'),
                    message.get('data', {})
                ))
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass

    async def _keepalive(self):
        try:
            while True:
                await asyncio.sleep(self.KEEPALIVE_INTERVAL)
                await self.send(text_data=': keepalive\n\n')
        except asyncio.CancelledError:
            pass

    def _event_formatter(self, event_type: str, data: Any) -> str:
        return f'event: {event_type}\ndata: {json.dumps(data)}\n\n'

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            event_type = data.get('type', 'message')
            if event_type == 'ping':
                await self.send(text_data=self._event_formatter('pong', {}))
        except json.JSONDecodeError:
            pass


class OrderSSEConsumer(SSEConsumer):
    CHANNEL = 'orders'

    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs'].get('order_id')
        await super().connect()
        await self.send(text_data=self._event_formatter('subscribed', {'order_id': self.order_id}))


class NotificationSSEConsumer(SSEConsumer):
    CHANNEL = 'notifications'

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs'].get('user_id')
        await super().connect()


async def sse_generator(client_id: str) -> AsyncGenerator[str, None]:
    queue = await SSEManager.add_client(client_id)
    try:
        while True:
            message = await queue.get()
            yield f'event: {message.get("type", "message")}\ndata: {json.dumps(message.get("data", {}))}\n\n'
            await asyncio.sleep(0)
    except asyncio.CancelledError:
        await SSEManager.remove_client(client_id)


@sync_to_async
def broadcast_sse(channel: str, event_type: str, data: Dict[str, Any]):
    asyncio.create_task(SSEManager.broadcast(channel, event_type, data))
