from django.contrib import admin
from .models import Order
from django.utils.html import format_html
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from django.contrib.admin import SimpleListFilter


class DeliveredStatusFilter(SimpleListFilter):
    title = 'Delivered Orders'
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
        'id',
        'user',
        'courier',
        'formatted_pickup_location',
        'formatted_delivery_location',
        'status_colored',
        'status',
        'order_price',
        'delivery_price',
        'payment_by_colored',
        'created_at',
    )
    list_display_links = ('id', 'user')
    list_filter = (
        'status',
        ('user', RelatedDropdownFilter),
        DeliveredStatusFilter,
        ('created_at', DropdownFilter),
    )
    search_fields = ('user__full_name', 'courier__full_name')
    ordering = ['-created_at']
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)  # Use the actual model field instead
    list_per_page = 30
    date_hierarchy = 'created_at'
    save_as = True
    save_on_top = True

    def status_colored(self, obj):
        color = {
            'pending': 'orange',
            'in_progress': 'blue',
            'delivered': 'green'
        }.get(obj.status, 'gray')
        return format_html('<span style="color: {};">{}</span>', color, obj.get_status_display())

    def payment_by_colored(self, obj):
        color = 'purple' if obj.payment_by == 'courier' else 'brown'
        return format_html('<span style="color: {};">{}</span>', color, obj.get_payment_by_display())

    def formatted_pickup_location(self, obj):
        return format_html('<strong>{}</strong>', obj.pickup_location)

    def formatted_delivery_location(self, obj):
        return format_html('<strong>{}</strong>', obj.delivery_location)

    status_colored.short_description = "Status"
    payment_by_colored.short_description = "Payment By"
    formatted_pickup_location.short_description = "Pickup Location"
    formatted_delivery_location.short_description = "Delivery Location"

    fieldsets = (
        (None, {
            'fields': (
                'user',
                'courier',
                ('pickup_latitude', 'pickup_longitude', 'delivery_latitude', 'delivery_longitude'),
                ('pickup_comment', 'delivery_comment'),
                'status',
            ),
        }),
        ('Price & Payment', {
            'fields': (
                ('order_price', 'delivery_price'),
                'payment_by'
            ),
            'classes': ('collapse',),  # Collapsed section
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    actions = ['mark_as_delivered', 'mark_as_in_progress']

    @admin.action(description='Mark selected orders as Delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')

    @admin.action(description='Mark selected orders as In Progress')
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'delivered':
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'delivered':
            return False
        return super().has_delete_permission(request, obj)
