from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at', 'updated_at')
    search_fields = ('full_name',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_active', 'is_staff')

    fieldsets = (
        (None, {'fields': ('full_name', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    actions = ['make_active', 'make_inactive']

    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Selected users have been activated.")

    make_active.short_description = "Activate selected users"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Selected users have been deactivated.")

    make_inactive.short_description = "Deactivate selected users"

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def get_role(self, obj):
        if obj.is_superuser:
            return "Superuser"
        elif obj.is_staff:
            return "Staff"
        return "User"

    get_role.short_description = "Role"

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:
            queryset = queryset.filter(is_superuser=False)
        return queryset
