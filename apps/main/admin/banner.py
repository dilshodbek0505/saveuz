from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.main.models import Banner


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    icon_name = "image"
    list_display = ("id", "name", "is_active")
    list_display_links = ("id", "name")
    ordering = ["position"]
