from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()



urlpatterns = [
    path('', views.index, name='index'),
]
