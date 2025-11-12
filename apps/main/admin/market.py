from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.main.models import Market, Product




class ProductInline(admin.TabularInline):
    model = Product
    fields = ("name", "price", "category", "primary_image_preview")
    readonly_fields = ("primary_image_preview",)
    extra = 3
    min_num = 0
    verbose_name = "Product"
    verbose_name_plural = "Products"

    def primary_image_preview(self, obj):
        image_file = obj.primary_image_file
        if not image_file:
            return _("No image")
        return format_html('<img src="{}" style="max-height:80px;max-width:80px;" />', image_file.url)
    primary_image_preview.short_description = _("Primary image")


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "get_product_count")
    list_display_links = ("id", "name")
    inlines = [ProductInline]

    def get_queryset(self, request):
        user = request.user
        
        qs = super().get_queryset(request)

        qs = qs.select_related("owner")
        if user.is_staff == True and user.is_superuser == False:
            qs = qs.filter(owner=request.user)
        return qs

    def get_product_count(self, obj):
        return "{} ta".format(obj.products.all().count())
    get_product_count.short_description = _("Product count")
