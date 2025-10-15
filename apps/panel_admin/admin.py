from django.contrib import admin

from apps.panel_admin.models import AdminDevice


@admin.register(AdminDevice)
class AdminDeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name", "token")
