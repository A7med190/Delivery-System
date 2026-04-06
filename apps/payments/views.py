from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=self.request.user)

    def create(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.orders.models import Order
        
        order = Order.objects.get(id=serializer.validated_data['order_id'], customer=request.user)
        
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total,
            method=serializer.validated_data['method'],
        )
        
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'completed'
        payment.paid_at = timezone.now()
        payment.transaction_id = f"TXN-{payment.payment_reference}"
        payment.save()
        
        payment.order.status = 'confirmed'
        payment.order.save()
        
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        payment = self.get_object()
        payment.status = 'refunded'
        payment.save()
        
        payment.order.status = 'cancelled'
        payment.order.save()
        
        return Response(PaymentSerializer(payment).data)
