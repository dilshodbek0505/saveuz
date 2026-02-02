from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from import_export.admin import ExportMixin 
from unfold.admin import ModelAdmin

from apps.main.models import Product, ProductImage
from apps.main.forms.product_admin import ProductAdminForm
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
    form = ProductAdminForm
    list_display = ("id", "display_name", "market", "display_source")
    list_display_links = ("id", "display_name")
    search_fields = ("name", "common_product__name", "market__name")
    readonly_fields = ("discount_value", "discount_price", "discount_type", "display_common_product_info")
    
    fieldsets = (
        (_("Способ добавления"), {
            "fields": ("add_mode",),
            "description": _("Выберите способ добавления продукта: из общей базы или вручную.")
        }),
        (_("Продукт из общей базы"), {
            "fields": ("common_product", "display_common_product_info"),
            "classes": ("common-product-section",),
            "description": _("Выберите продукт из общей базы. Название, описание и категория будут взяты автоматически. Вам нужно указать только цену и маркет.")
        }),
        (_("Основная информация (ручное заполнение)"), {
            "fields": ("name", "description", "category"),
            "classes": ("manual-fields-section",),
            "description": _("Заполните эти поля, если добавляете продукт вручную.")
        }),
        (_("Маркет и цена"), {
            "fields": ("market", "price"),
            "description": _("Выберите свой маркет и укажите цену продукта.")
        }),
        (_("Скидка (необязательно)"), {
            "fields": ("discount_price", "discount_type", "discount_value"),
            "classes": ("collapse",),
            "description": _("Укажите скидку, если необходимо.")
        }),
    )
    
    inlines = (ProductImageInline,)

    @admin.display(description=_("Name"))
    def display_name(self, obj):
        return obj.resolved_name

    @admin.display(description=_("Источник"))
    def display_source(self, obj):
        if obj.common_product:
            return format_html(
                '<span style="color: #28a745;">✓ Из общей базы</span>'
            )
        return format_html(
            '<span style="color: #ffc107;">✎ Вручную</span>'
        )

    @admin.display(description=_("Информация о продукте"))
    def display_common_product_info(self, obj=None):
        # Получаем выбранный common_product из формы
        if obj and obj.common_product:
            common_product = obj.common_product
        else:
            # При создании нового продукта obj может быть None
            # Информация будет обновляться через JavaScript
            return format_html(
                '<div id="common-product-info" style="padding: 10px; background: #fff3cd; border-radius: 4px; color: #856404;">'
                'Выберите продукт из общей базы, чтобы увидеть информацию'
                '</div>'
            )
        
        return format_html(
            '<div id="common-product-info" style="padding: 10px; background: #e7f3ff; border-radius: 4px;">'
            '<strong>Название:</strong> {}<br>'
            '<strong>Описание:</strong> {}<br>'
            '<strong>Категория:</strong> {}'
            '</div>',
            common_product.name,
            common_product.description[:100] + ('...' if len(common_product.description) > 100 else ''),
            common_product.category.name if common_product.category else '-'
        )
    display_common_product_info.short_description = _("Информация о продукте")

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        qs = qs.select_related("market", "common_product", "common_product__category")

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

    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
        js = ('admin/js/product_admin.js',)
