from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from .models import Order
from .serializers import OrderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().select_related('user', 'courier')
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_by']
    search_fields = ['pickup_location', 'delivery_location']
    ordering_fields = ['created_at', 'order_price']

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Noto‘g‘ri status'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save()
        return Response({'status': f"Buyurtma statusi {new_status} ga o'zgartirildi."})
