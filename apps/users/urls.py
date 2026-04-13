from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet, RegisterView

router = SimpleRouter()
router.register('', UserViewSet, basename='user')

urlpatterns = router.urls + [
    path('register/', RegisterView.as_view(), name='register'),
]