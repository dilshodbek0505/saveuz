from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.main.models import Market, Product




class ProductInline(admin.TabularInline):
    model = Product
    fields = ("name", "price", "image", "category")
    extra = 3
    min_num = 0
    verbose_name = "Product"
    verbose_name_plural = "Products"


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
