from rest_framework import serializers
from .models import Category, Restaurant, MenuItem, MenuCategory


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active']


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'description', 'order', 'is_active']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'price', 'image', 'category', 'category_name',
            'is_available', 'is_featured', 'preparation_time', 'calories'
        ]


class MenuItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            'name', 'description', 'price', 'image', 'category',
            'is_available', 'is_featured', 'preparation_time', 'calories'
        ]


class RestaurantListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'logo', 'category', 'category_name',
            'address', 'phone', 'rating', 'review_count', 'minimum_order',
            'delivery_fee', 'estimated_delivery_time', 'is_active', 'opening_time', 'closing_time'
        ]


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    categories = MenuCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'cover_image',
            'category', 'address', 'latitude', 'longitude', 'phone', 'email',
            'opening_time', 'closing_time', 'minimum_order', 'delivery_fee',
            'estimated_delivery_time', 'is_active', 'status', 'rating',
            'review_count', 'menu_items', 'categories', 'created_at'
        ]


class RestaurantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = [
            'name', 'description', 'logo', 'cover_image', 'category',
            'address', 'latitude', 'longitude', 'phone', 'email',
            'opening_time', 'closing_time', 'minimum_order', 'delivery_fee',
            'estimated_delivery_time'
        ]
