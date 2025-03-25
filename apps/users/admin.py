from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from admin_numeric_filter.admin import NumericFilterModelAdmin, RangeNumericFilter
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from .models import User


@admin.register(User)
class UserAdmin(NumericFilterModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at')
    list_display_links = ('id', 'full_name')
    list_editable = ('is_active', 'is_staff')
    list_filter = (
        ('is_active', DropdownFilter),
        ('is_staff', DropdownFilter),
        ('is_superuser', DropdownFilter),
        ('created_at', DateTimeRangeFilter),
        ('updated_at', DateTimeRangeFilter),
    )
    search_fields = ('full_name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('full_name', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )
    filter_horizontal = ('groups', 'user_permissions')

    actions = ['mark_as_active', 'mark_as_inactive']

    @admin.action(description=_('Mark selected users as active'))
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description=_('Mark selected users as inactive'))
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
