from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.main.models import Category


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    icon_name = "category"
    list_display = ("id", "name", "parent")
    list_display_links = ("id", "name")