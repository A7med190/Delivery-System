from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Delivery, DeliveryLocation
from .serializers import DeliverySerializer, DeliveryUpdateSerializer, DeliveryLocationSerializer

User = get_user_model()


class DeliveryViewSet(viewsets.ModelViewSet):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Delivery.objects.all()
        if user.is_driver:
            return Delivery.objects.filter(driver=user)
        return Delivery.objects.filter(order__customer=user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        delivery = self.get_object()
        serializer = DeliveryUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        delivery.status = serializer.validated_data['status']
        
        if serializer.validated_data['status'] == 'picked_up':
            delivery.pickup_time = timezone.now()
        elif serializer.validated_data['status'] == 'delivered':
            delivery.delivery_time = timezone.now()
        
        if 'latitude' in serializer.validated_data:
            delivery.current_latitude = serializer.validated_data['latitude']
            delivery.current_longitude = serializer.validated_data['longitude']
        
        if 'notes' in serializer.validated_data:
            delivery.delivery_notes = serializer.validated_data['notes']
        
        delivery.save()
        
        return Response(DeliverySerializer(delivery).data)

    @action(detail=True, methods=['post'])
    def assign_driver(self, request, pk=None):
        delivery = self.get_object()
        driver_id = request.data.get('driver_id')
        
        try:
            driver = User.objects.get(id=driver_id, is_driver=True)
        except User.DoesNotExist:
            return Response(
                {'error': 'Driver not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        delivery.driver = driver
        delivery.status = 'assigned'
        delivery.save()
        
        return Response(DeliverySerializer(delivery).data)

    @action(detail=True, methods=['post'])
    def update_location(self, request, pk=None):
        delivery = self.get_object()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        accuracy = request.data.get('accuracy')
        speed = request.data.get('speed')
        
        location = DeliveryLocation.objects.create(
            delivery=delivery,
            latitude=latitude,
            longitude=longitude,
            accuracy=accuracy,
            speed=speed
        )
        
        delivery.current_latitude = latitude
        delivery.current_longitude = longitude
        delivery.save()
        
        return Response(DeliveryLocationSerializer(location).data)

    @action(detail=False, methods=['get'])
    def available(self, request):
        deliveries = Delivery.objects.filter(
            status='pending',
            driver__isnull=True
        )
        serializer = DeliverySerializer(deliveries, many=True)
        return Response(serializer.data)
