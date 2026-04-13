from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import CategoryViewSet, RestaurantViewSet, MenuItemViewSet

router = SimpleRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('menu-items', MenuItemViewSet, basename='menu-item')
router.register('', RestaurantViewSet, basename='restaurant')

urlpatterns = router.urls