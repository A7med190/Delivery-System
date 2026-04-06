from rest_framework import serializers
from .models import Delivery, DeliveryLocation


class DeliveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocation
        fields = ['id', 'latitude', 'longitude', 'accuracy', 'speed', 'recorded_at']


class DeliverySerializer(serializers.ModelSerializer):
    locations = DeliveryLocationSerializer(many=True, read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'order_number', 'driver', 'driver_name', 'tracking_number',
            'status', 'pickup_time', 'delivery_time', 'current_latitude', 'current_longitude',
            'delivery_notes', 'signature_image', 'locations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'tracking_number', 'created_at']

    def get_driver_name(self, obj):
        if obj.driver:
            return f"{obj.driver.first_name} {obj.driver.last_name}"
        return None


class DeliveryUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Delivery.STATUS_CHOICES)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, required=False)
    notes = serializers.CharField(required=False, allow_blank=True)


class DeliveryAssignSerializer(serializers.Serializer):
    delivery_id = serializers.IntegerField()
    driver_id = serializers.IntegerField()
