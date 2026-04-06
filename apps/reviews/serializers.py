from rest_framework import serializers
from .models import Review, ReviewImage, ReviewReply


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['id', 'image', 'caption']


class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ['id', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(many=True, read_only=True)
    reply = ReviewReplySerializer(read_only=True)
    customer_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            'id', 'customer', 'customer_name', 'restaurant', 'order',
            'rating', 'comment', 'is_approved', 'images', 'reply',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'is_approved', 'created_at']

    def get_customer_name(self, obj):
        return f"{obj.customer.first_name} {obj.customer.last_name}"


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class ReviewReplyCreateSerializer(serializers.Serializer):
    comment = serializers.CharField(max_length=1000)
