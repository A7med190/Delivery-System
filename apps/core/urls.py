from django.urls import path
from apps.core.sse import OrderSSEConsumer, NotificationSSEConsumer
from apps.core.views import (
    HealthCheckView,
    SSEOrderView,
    SSENotificationsView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('sse/orders/<str:order_id>/', SSEOrderView.as_view(), name='sse-order'),
    path('sse/notifications/<int:user_id>/', SSENotificationsView.as_view(), name='sse-notifications'),
]
