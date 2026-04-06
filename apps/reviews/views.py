from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg

from .models import Review, ReviewImage, ReviewReply
from .serializers import (
    ReviewSerializer, ReviewCreateSerializer,
    ReviewReplyCreateSerializer, ReviewReplySerializer
)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if not self.request.user.is_staff:
            queryset = queryset.filter(restaurant__owner=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

    def create(self, request):
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        from apps.orders.models import Order
        
        order_id = request.data.get('order_id')
        order = Order.objects.get(id=order_id, customer=request.user)
        
        review = Review.objects.create(
            customer=request.user,
            restaurant=order.restaurant,
            order=order,
            rating=serializer.validated_data['rating'],
            comment=serializer.validated_data.get('comment', ''),
        )
        
        restaurant = order.restaurant
        avg_rating = Review.objects.filter(restaurant=restaurant, is_approved=True).aggregate(Avg('rating'))['rating__avg']
        restaurant.rating = avg_rating or 0
        restaurant.review_count = Review.objects.filter(restaurant=restaurant, is_approved=True).count()
        restaurant.save()
        
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        review = self.get_object()
        
        if request.user != review.restaurant.owner and not request.user.is_staff:
            return Response(
                {'error': 'You can only reply to reviews of your restaurant'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReviewReplyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reply = ReviewReply.objects.create(
            review=review,
            restaurant=review.restaurant,
            comment=serializer.validated_data['comment']
        )
        
        return Response(ReviewReplySerializer(reply).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        reviews = Review.objects.filter(customer=request.user)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
