from django.contrib import admin

from apps.main.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    icon_name = "category"
    list_display = ("id", "name", "parent")
    list_display_links = ("id", "name")