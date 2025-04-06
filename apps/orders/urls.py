from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.orders.views import OrderViewSet, CourierOrdersByChatIdViewSet, OrdersUpdateViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('courier/orders/', CourierOrdersByChatIdViewSet.as_view(), name='courier-orders-by-chat-id'),
    path('update/<int:pk>/', OrdersUpdateViewSet.as_view(),
         name='orders-update'),
]
