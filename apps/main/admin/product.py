from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from apps.main.models import Product
from apps.product.resources import ProductResource


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    resource_class = ProductResource
    list_display = ("id", "name", "market")
    list_display_links = ("id", "name")
    search_fields = ("name", "market__name")

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        qs = qs.select_related("market", )

        if user.is_staff and not user.is_superuser:
            markets = user.markets.all()
            qs = qs.filter(market__in=markets)
        
        return qs