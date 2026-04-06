from rest_framework import serializers
from .models import Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'label', 'street_address', 'apartment_unit',
            'city', 'state', 'postal_code', 'country', 'latitude', 'longitude',
            'is_default', 'delivery_instructions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user
        if validated_data.get('is_default'):
            Address.objects.filter(user=user).update(is_default=False)
        return Address.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default'):
            Address.objects.filter(user=instance.user).exclude(id=instance.id).update(is_default=False)
        return super().update(instance, validated_data)
