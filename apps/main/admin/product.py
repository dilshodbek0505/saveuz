from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from import_export.admin import ExportMixin 
from unfold.admin import ModelAdmin

from apps.main.models import Product, ProductImage
from apps.product.formats import ImageAwareXLSX
from apps.product.resources import ProductResource


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "position")


# ExportMixin va ModelAdmin'dan meros olindi
@admin.register(Product)
class ProductAdmin(ExportMixin, ModelAdmin):
    icon_name = "inventory_2" 
    resource_class = ProductResource
    formats = [ImageAwareXLSX] # Export uchun formatlar saqlab qolindi
    list_display = ("id", "display_name", "market")
    list_display_links = ("id", "display_name")
    search_fields = ("name", "common_product__name", "market__name")
    readonly_fields = ("discount_value", "discount_price", "discount_type")
    inlines = (ProductImageInline,)

    @admin.display(description=_("Name"))
    def display_name(self, obj):
        return obj.resolved_name

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        qs = qs.select_related("market")

        if user.is_staff and not user.is_superuser:
            markets = user.markets.all()
            qs = qs.filter(market__in=markets)

        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if (
            db_field.name == "market"
            and request.user.is_staff
            and not request.user.is_superuser
        ):
            kwargs["queryset"] = request.user.markets.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
