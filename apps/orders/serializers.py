from rest_framework import serializers
from .models import Order, TelegramUsers


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=TelegramUsers.objects.filter(is_courier=False))
    courier = serializers.PrimaryKeyRelatedField(queryset=TelegramUsers.objects.filter(is_courier=True))

    class Meta:
        model = Order
        fields = (
            'id', 'user', 'courier', 'pickup_location', 'delivery_location', 'image', 'pickup_comment',
            'delivery_comment', 'status', 'order_price', 'delivery_price', 'payment_by', 'created_at', 'updated_at'
        )

    def validate(self, data):
        if data['order_price'] < 0 or data['delivery_price'] < 0:
            raise serializers.ValidationError("Prices must be positive values.")
        return data
