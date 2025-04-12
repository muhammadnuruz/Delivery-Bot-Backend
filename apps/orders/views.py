from rest_framework import viewsets
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from ..telegram_users.models import TelegramUsers


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [AllowAny]
    serializer_class = OrderSerializer
    filterset_fields = ['status', 'user', 'courier']
    search_fields = ['user__full_name', 'courier__full_name', 'pickup_comment', 'delivery_comment']
    ordering_fields = ['created_at', 'order_price', 'delivery_price']
    ordering = ['-created_at']

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != "cancelled":
            order.status = "cancelled"
            order.save()
            return Response({"message": "Order cancelled successfully!"}, status=status.HTTP_200_OK)
        return Response({"message": "Order is already cancelled!"}, status=status.HTTP_400_BAD_REQUEST)


from django.utils import timezone
from datetime import timedelta

class CourierOrdersByChatIdViewSet(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        chat_id = self.request.query_params.get('chat_id')
        period = self.request.query_params.get('period')  # new!
        courier = TelegramUsers.objects.filter(chat_id=chat_id, is_courier=True).first()
        if not courier:
            return Order.objects.none()
        queryset = Order.objects.filter(courier=courier)
        now = timezone.now()
        if period == "today":
            queryset = queryset.filter(created_at__date=now.date())
        elif period == "week":
            week_ago = now - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=week_ago)
        elif period == "month":
            month_ago = now - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=month_ago)
        return queryset


class OrdersUpdateViewSet(UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]
