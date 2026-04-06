from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'type_display', 'title', 'message',
            'data', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'type', 'title', 'message', 'data', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'order_placed', 'order_confirmed', 'order_preparing', 'order_ready',
            'order_picked_up', 'order_delivered', 'order_cancelled', 'payment_received',
            'review_request', 'promotion', 'email_enabled', 'push_enabled'
        ]


class MarkReadSerializer(serializers.Serializer):
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
    )
    mark_all = serializers.BooleanField(default=False)
