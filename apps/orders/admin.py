from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from .models import Order


class DeliveredStatusFilter(SimpleListFilter):
    title = 'Delivery Status'
    parameter_name = 'delivered_status'

    def lookups(self, request, model_admin):
        return (
            ('delivered', 'Delivered'),
            ('not_delivered', 'Not Delivered'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'delivered':
            return queryset.filter(status='delivered')
        elif self.value() == 'not_delivered':
            return queryset.exclude(status='delivered')
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_info', 'courier_info', 'status', 'status_colored', 'order_price', 'delivery_price',
        'distance_km', 'created_at', 'map_preview'
    )
    list_display_links = ('id', 'user_info')
    list_filter = ('status', 'payment_by', 'deliver_payment_by', 'created_at', DeliveredStatusFilter)
    search_fields = ('user__full_name', 'courier__full_name', 'user__username', 'courier__username')
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at', 'map_preview')
    list_editable = ('status', 'order_price', 'delivery_price')
    list_per_page = 30
    date_hierarchy = 'created_at'
    save_as = True
    save_on_top = True

    def status_colored(self, obj):
        colors = {'pending': 'orange', 'in_progress': 'blue', 'delivered': 'green', 'cancelled': 'red'}
        return format_html('<span style="color: {}">{}</span>', colors.get(obj.status, 'gray'),
                           obj.get_status_display())

    def user_info(self, obj):
        return format_html('<b>{}</b><br>@{}', obj.user.full_name, obj.user.username or 'No username')

    user_info.short_description = "User"

    def courier_info(self, obj):
        if obj.courier:
            return format_html('<b>{}</b><br>@{}', obj.courier.full_name, obj.courier.username or 'No username')
        return "No courier assigned"

    courier_info.short_description = "Courier"

    def map_preview(self, obj):
        if obj.pickup_latitude and obj.delivery_latitude:
            return format_html(
                '<a href="https://www.google.com/maps/dir/{},{}/{},{}" target="_blank">View on Map</a>',
                obj.pickup_latitude, obj.pickup_longitude, obj.delivery_latitude, obj.delivery_longitude
            )
        return "No Location Data"

    map_preview.short_description = "Map"

    fieldsets = (
        (None, {
            'fields': (
                'user', 'courier', ('pickup_latitude', 'pickup_longitude', 'delivery_latitude', 'delivery_longitude'),
                ('pickup_address', 'delivery_address'), ('pickup_comment', 'delivery_comment'), 'status', 'image',
                'map_preview'
            ),
        }),
        ('Price & Payment', {
            'fields': (('order_price', 'delivery_price'), 'payment_by', 'deliver_payment_by'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    actions = ['mark_as_delivered', 'mark_as_in_progress', 'mark_as_canceled']

    @admin.action(description='Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description='Mark selected orders as In Progress')
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')

    @admin.action(description='Mark selected orders as Canceled')
    def mark_as_canceled(self, request, queryset):
        queryset.update(status='canceled')
