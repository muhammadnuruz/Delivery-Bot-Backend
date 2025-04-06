from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'courier',
            'pickup_latitude', 'pickup_longitude', 'delivery_latitude', 'delivery_longitude',
            'image', 'pickup_comment', 'delivery_comment', 'status', 'order_price', 'delivery_price', 'payment_by', 'deliver_payment_by',
            'created_at', 'updated_at', 'pickup_address', 'delivery_address', 'distance_km', 'map'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
