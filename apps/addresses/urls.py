from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import AddressViewSet

router = SimpleRouter()
router.register('', AddressViewSet, basename='address')

urlpatterns = router.urls
