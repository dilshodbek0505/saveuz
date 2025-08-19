from django.contrib import admin

from apps.main.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product")
    list_display_links = ("id", "user")