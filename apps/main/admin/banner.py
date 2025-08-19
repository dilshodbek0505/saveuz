from django.contrib import admin

from apps.main.models import Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "is_active")
    list_display_links = ("id", "name")
    ordering = ["position"]
