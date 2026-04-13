"""
Serializers for common core functionality.
"""
from rest_framework import serializers


class IdempotencyKeySerializer(serializers.Serializer):
    idempotency_key = serializers.CharField(
        required=True,
        max_length=64,
        help_text='Unique key for idempotent operations',
    )


class WebhookSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    event_types = serializers.ListField(
        child=serializers.CharField(max_length=255),
        required=True,
    )
    secret = serializers.CharField(max_length=255, required=False, allow_blank=True)


class WebhookDeliverySerializer(serializers.Serializer):
    webhook_id = serializers.IntegerField()
    url = serializers.URLField()
    success = serializers.BooleanField()


class HealthCheckSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['healthy', 'unhealthy'])
    checks = serializers.ListField()


class HealthCheckResultSerializer(serializers.Serializer):
    name = serializers.CharField()
    status = serializers.ChoiceField(choices=['healthy', 'unhealthy'])
    message = serializers.CharField(allow_blank=True)
    details = serializers.DictField(required=False)
