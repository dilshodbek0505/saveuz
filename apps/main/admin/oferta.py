from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.main.models import Oferta


@admin.register(Oferta)
class OfertaAdmin(ModelAdmin):
    icon_name = "description"
    list_display = ("id", "title", "is_active", "created_at", "updated_at")
    list_display_links = ("id", "title")
    list_filter = ("is_active", "created_at")
    search_fields = ("title",)
    ordering = ["-created_at"]
    
    fieldsets = (
        (None, {
            "fields": ("title", "file", "is_active")
        }),
    )
    
    def has_add_permission(self, request):
        # Faqat superadmin qo'sha oladi
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        # Faqat superadmin o'zgartira oladi
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        # Faqat superadmin o'chira oladi
        return request.user.is_superuser

