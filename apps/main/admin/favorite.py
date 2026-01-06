from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.main.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(ModelAdmin):
    icon_name = "bookmark"
    list_display = ("id", "user", "product")
    list_display_links = ("id", "user")