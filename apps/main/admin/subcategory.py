from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.main.models import Subcategory


@admin.register(Subcategory)
class SubcategoryAdmin(ModelAdmin):
    icon_name = "account_tree"
    list_display = ("id", "name", "category", "order", "created_at")
    list_display_links = ("id", "name")
    list_filter = ("category",)
    search_fields = ("name", "category__name")
    list_editable = ("order",)
    autocomplete_fields = ("category",)
    ordering = ("category", "order", "name")
    list_per_page = 25

    fieldsets = (
        (
            None,
            {
                "fields": ("category", "name", "order"),
            },
        ),
    )

    class Media:
        css = {"all": ("admin/css/product_admin.css",)}


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1
    fields = ("name", "order")
    verbose_name = "Subkategoriya"
    verbose_name_plural = "Subkategoriyalar"
    ordering = ("order", "name")
