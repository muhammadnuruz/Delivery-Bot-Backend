from django.db import models

from apps.telegram_users.models import TelegramUsers


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('user', 'Paid by User'),
        ('courier', 'Paid by Courier'),
    ]

    SECOND_PAYMENT_CHOICES = [
        ('user', 'Paid by User'),
        ('customer', 'Paid by Customer'),
    ]

    user = models.ForeignKey(TelegramUsers, on_delete=models.CASCADE, related_name='orders')
    courier = models.ForeignKey(
        TelegramUsers, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries'
    )
    pickup_latitude = models.FloatField(help_text="Pickup location latitude")
    pickup_longitude = models.FloatField(help_text="Pickup location longitude")
    pickup_address = models.TextField(null=True)
    delivery_latitude = models.FloatField(help_text="Delivery location latitude")
    delivery_longitude = models.FloatField(help_text="Delivery location longitude")
    delivery_address = models.TextField(null=True)
    distance_km = models.FloatField(null=True)
    image = models.CharField(help_text="Optional image for the order")
    map = models.TextField(null=True)
    pickup_comment = models.TextField(null=True, blank=True, help_text="Additional comment for the pickup")
    delivery_comment = models.TextField(null=True, blank=True, help_text="Additional comment for the delivery")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price of the order")
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Delivery fee")
    payment_by = models.CharField(max_length=10, choices=PAYMENT_CHOICES,
                                  help_text="Who will pay the delivery price")
    deliver_payment_by = models.CharField(max_length=10, choices=SECOND_PAYMENT_CHOICES,
                                          help_text="Who will pay the product price")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.full_name} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
