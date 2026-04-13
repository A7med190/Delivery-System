import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from apps.core.channels import OrderConsumer, DriverLocationConsumer, NotificationConsumer, ChatConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<order_id>\w+)/$', OrderConsumer.as_asgi()),
    re_path(r'ws/driver/(?P<driver_id>\w+)/$', DriverLocationConsumer.as_asgi()),
    re_path(r'ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_id>\w+)/$', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
