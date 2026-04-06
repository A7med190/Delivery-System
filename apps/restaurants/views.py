from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg

from .models import Category, Restaurant, MenuItem, MenuCategory
from .serializers import (
    CategorySerializer, RestaurantListSerializer, RestaurantDetailSerializer,
    RestaurantCreateSerializer, MenuItemSerializer, MenuItemCreateSerializer,
    MenuCategorySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantListSerializer
        if self.action == 'create':
            return RestaurantCreateSerializer
        return RestaurantDetailSerializer

    def get_queryset(self):
        queryset = Restaurant.objects.all()
        if self.action == 'list':
            queryset = queryset.filter(is_active=True)
        if not self.request.user.is_staff:
            queryset = queryset.filter(owner=self.request.user)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def menu(self, request, pk=None):
        restaurant = self.get_object()
        items = restaurant.menu_items.filter(is_available=True)
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data)


class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MenuItem.objects.filter(restaurant__owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MenuItemCreateSerializer
        return MenuItemSerializer

    def perform_create(self, serializer):
        restaurant_id = self.request.data.get('restaurant')
        restaurant = Restaurant.objects.get(id=restaurant_id, owner=self.request.user)
        serializer.save(restaurant=restaurant)
