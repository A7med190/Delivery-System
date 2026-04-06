from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_name', 'quantity', 'unit_price', 'total_price', 'special_instructions']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'restaurant', 'restaurant_name', 'customer', 'customer_email',
            'status', 'delivery_address', 'subtotal', 'delivery_fee', 'tax', 'discount',
            'total', 'special_instructions', 'estimated_delivery_time', 'actual_delivery_time',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'subtotal', 'total', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    address_id = serializers.IntegerField()
    items = serializers.ListField(
        child=serializers.DictField(child=serializers.CharField())
    )
    special_instructions = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        for item in value:
            if 'menu_item_id' not in item or 'quantity' not in item:
                raise serializers.ValidationError("Each item must have menu_item_id and quantity")
        return value


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
