from django.contrib import admin

from apps.main.models import Discount, Product


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "type", "value", "is_active")
    list_display_links = ("id", "product",)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user = request.user
        if db_field.name == "product" and not user.is_superuser and user.is_staff:
            qs = Product.objects.filter(market__owner=user)
            kwargs["queryset"] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        qs = qs.select_related("product")
        if not user.is_superuser and user.is_staff:
            qs = qs.filter(product__market__owner=user)
        return qs