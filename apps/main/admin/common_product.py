from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from unfold.admin import ModelAdmin

from apps.main.models import CommonProduct, CommonProductImage, Subcategory
from apps.main.forms.product_admin import CommonProductAdminForm


class CommonProductImageInline(admin.TabularInline):
    model = CommonProductImage
    extra = 1
    fields = ("image", "position")


@admin.register(CommonProduct)
class CommonProductAdmin(ModelAdmin):
    form = CommonProductAdminForm
    icon_name = "inventory"
    list_display = ("id", "name", "category", "subcategory")
    list_display_links = ("id", "name")
    search_fields = ("name", "category__name", "subcategory__name")
    autocomplete_fields = ("category",)
    inlines = (CommonProductImageInline,)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "subcategory":
            obj = getattr(request, "_current_common_product_obj", None)
            if obj and obj.category_id:
                kwargs["queryset"] = Subcategory.objects.filter(
                    category_id=obj.category_id
                ).order_by("order", "name")
            else:
                kwargs["queryset"] = Subcategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._current_common_product_obj = obj
        return super().get_form(request, obj, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "get-subcategories/",
                self.admin_site.admin_view(self._get_subcategories),
                name="main_commonproduct_get_subcategories",
            ),
        ]
        return custom + urls

    class Media:
        js = ("admin/js/product_admin.js",)

    def _get_subcategories(self, request):
        category_id = request.GET.get("category_id")
        if not category_id:
            return JsonResponse({"subcategories": []})
        try:
            qs = Subcategory.objects.filter(category_id=int(category_id)).order_by(
                "order", "name"
            )
            subcategories = [{"id": s.pk, "name": s.name} for s in qs]
        except (ValueError, TypeError):
            subcategories = []
        return JsonResponse({"subcategories": subcategories})

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
