from django.db import models


class TelegramUsers(models.Model):
    chat_id = models.CharField(max_length=250)
    username = models.CharField(max_length=100, null=True)
    full_name = models.CharField(max_length=100)
    is_courier = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return f"{self.full_name} ({'Courier' if self.is_courier else 'User'})"
