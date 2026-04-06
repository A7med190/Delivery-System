from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from apps.restaurants.models import Restaurant, MenuItem


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        if user.is_restaurant_owner:
            return Order.objects.filter(restaurant__owner=user)
        return Order.objects.filter(customer=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        restaurant = Restaurant.objects.get(id=data['restaurant_id'])
        address = request.user.addresses.get(id=data['address_id'])
        
        subtotal = 0
        items_data = []
        for item_data in data['items']:
            menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
            quantity = int(item_data['quantity'])
            item_total = menu_item.price * quantity
            subtotal += item_total
            items_data.append({
                'menu_item': menu_item,
                'quantity': quantity,
                'unit_price': menu_item.price,
                'instructions': item_data.get('instructions', '')
            })
        
        order = Order.objects.create(
            customer=request.user,
            restaurant=restaurant,
            delivery_address=address,
            subtotal=subtotal,
            delivery_fee=restaurant.delivery_fee,
            tax=subtotal * 0.1,
            special_instructions=data.get('special_instructions', ''),
        )
        
        for item in items_data:
            OrderItem.objects.create(
                order=order,
                menu_item=item['menu_item'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                special_instructions=item['instructions']
            )
        
        order.save()
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order.status = serializer.validated_data['status']
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            status=serializer.validated_data['status'],
            notes=serializer.validated_data.get('notes', ''),
            updated_by=request.user
        )
        
        if serializer.validated_data['status'] == 'delivered':
            order.actual_delivery_time = timezone.now()
            order.save()
        
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        queryset = self.get_queryset()
        return Response({
            'total_orders': queryset.count(),
            'pending': queryset.filter(status='pending').count(),
            'completed': queryset.filter(status='delivered').count(),
            'cancelled': queryset.filter(status='cancelled').count(),
            'total_revenue': queryset.filter(status='delivered').aggregate(Sum('total'))['total__sum'] or 0,
        })
