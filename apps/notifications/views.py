from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer, MarkReadSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'count': count})

    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        queryset = self.get_queryset()
        
        if serializer.validated_data.get('mark_all'):
            queryset.filter(is_read=False).update(is_read=True)
        elif serializer.validated_data.get('notification_ids'):
            queryset.filter(
                id__in=serializer.validated_data['notification_ids']
            ).update(is_read=True)
        
        return Response({'message': 'Notifications marked as read'})

    @action(detail=False, methods=['get', 'put', 'patch'])
    def preferences(self, request):
        pref, created = NotificationPreference.objects.get_or_create(user=request.user)
        
        if request.method == 'GET':
            serializer = NotificationPreferenceSerializer(pref)
            return Response(serializer.data)
        
        serializer = NotificationPreferenceSerializer(pref, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
