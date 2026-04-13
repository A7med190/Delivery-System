import asyncio
import json
import logging
from typing import Any, Dict, Optional

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class BaseWebSocketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f'WebSocket connected: {self.channel_name}')

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info(f'WebSocket disconnected: {self.channel_name}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': message_type,
                    'data': data,
                    'sender_channel_name': self.channel_name,
                }
            )
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))

    async def message(self, event):
        await self.send(text_data=json.dumps(event['data']))


class OrderConsumer(BaseWebSocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs'].get('order_id')
        self.room_group_name = f'order_{self.order_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'order_id': self.order_id,
        }))

    async def order_update(self, event):
        await self.send(text_data=json.dumps(event['data']))


class DriverLocationConsumer(BaseWebSocketConsumer):
    async def connect(self):
        self.driver_id = self.scope['url_route']['kwargs'].get('driver_id')
        self.room_group_name = f'driver_{self.driver_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def location_update(self, event):
        await self.send(text_data=json.dumps(event['data']))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.room_group_name = f'notifications_{self.user.id}'
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()
            logger.info(f'User {self.user.id} connected to notifications')
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def notify(self, event):
        await self.send(text_data=json.dumps(event['data']))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs'].get('room_id')
        self.room_group_name = f'chat_{self.room_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': data.get('message', ''),
                'sender': self.scope['user'].username if self.scope['user'].is_authenticated else 'Anonymous',
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))
