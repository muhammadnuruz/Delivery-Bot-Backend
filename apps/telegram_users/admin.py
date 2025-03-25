from django.contrib import admin
from django.core.exceptions import ValidationError
from django_admin_listfilter_dropdown.filters import DropdownFilter
from .models import TelegramUsers
from ..orders.models import Order


@admin.register(TelegramUsers)
class TelegramUsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'username', 'chat_id', 'is_courier', 'is_available', 'created_at', 'updated_at')
    list_display_links = ('id', 'full_name')
    list_editable = ('is_courier', 'is_available')
    list_filter = (
        ('is_courier', DropdownFilter),
        ('is_available', DropdownFilter),
        ('created_at', admin.DateFieldListFilter),
    )
    search_fields = ('full_name', 'username', 'chat_id')
    list_per_page = 20

    class OrderInline(admin.TabularInline):
        model = Order
        fk_name = 'user'
        extra = 1

    inlines = [OrderInline]

    def save_model(self, request, obj, form, change):
        if obj.username and not obj.username.isalnum():
            raise ValidationError("Username faqat harf va raqamlardan iborat bo‘lishi kerak!")
        super().save_model(request, obj, form, change)

    actions = ['mark_as_courier', 'mark_as_available', 'mark_as_unavailable']

    @admin.action(description="Mark selected users as couriers")
    def mark_as_courier(self, request, queryset):
        queryset.update(is_courier=True)

    @admin.action(description="Mark selected users as available")
    def mark_as_available(self, request, queryset):
        queryset.update(is_available=True)

    @admin.action(description="Mark selected users as unavailable")
    def mark_as_unavailable(self, request, queryset):
        queryset.update(is_available=False)
