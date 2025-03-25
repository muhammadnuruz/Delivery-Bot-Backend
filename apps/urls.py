from django.urls import path, include

urlpatterns = [
    path('telegram-users/', include("apps.telegram_users.urls")),
    path('orders/', include("apps.orders.urls")),
]
