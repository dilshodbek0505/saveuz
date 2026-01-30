from django.contrib import admin
from unfold.admin import ModelAdmin

from apps.main.models import CommonProduct, CommonProductImage


class CommonProductImageInline(admin.TabularInline):
    model = CommonProductImage
    extra = 1
    fields = ("image", "position")


@admin.register(CommonProduct)
class CommonProductAdmin(ModelAdmin):
    icon_name = "inventory"
    list_display = ("id", "name", "category")
    list_display_links = ("id", "name")
    search_fields = ("name", "category__name")
    inlines = (CommonProductImageInline,)

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
