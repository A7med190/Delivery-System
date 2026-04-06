from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'user', 'amount', 'method',
            'status', 'transaction_id', 'payment_reference', 'paid_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'transaction_id', 'payment_reference', 'created_at']


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    method = serializers.ChoiceField(choices=Payment.METHOD_CHOICES)


class PaymentVerifySerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
