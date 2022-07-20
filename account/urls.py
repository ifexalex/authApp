from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()


router.register(r'register', RegisterUserViewset, basename='register')
router.register(r'login', LoginUserViewset, basename='login')
router.register(r'password-reset', SendPasswordResetLinkViewSet, basename='password-reset')
router.register(r'password-reset-confirm', PasswordResetConfirmViewSet, basename='password-reset-confirm')

urlpatterns = [
    path('', include(router.urls)),
]
