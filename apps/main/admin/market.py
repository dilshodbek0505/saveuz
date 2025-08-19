from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.main.models import Market


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "get_product_count")
    list_display_links = ("id", "name")

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