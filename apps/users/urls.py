from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet

router = DefaultRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('change-password/', UserViewSet.as_view({'post': 'change-password'}), name='change-password'),
    path('', include(router.urls)),
]
