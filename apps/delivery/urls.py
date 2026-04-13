from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import DeliveryViewSet

router = SimpleRouter()
router.register('', DeliveryViewSet, basename='delivery')

urlpatterns = router.urls