from django.urls import path, include

from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'cart', views.CartItemViewSet, base_name='cart')


urlpatterns = [
    path('', include(router.urls)),
]
