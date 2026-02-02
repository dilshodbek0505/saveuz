from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from import_export.admin import ExportMixin 
from unfold.admin import ModelAdmin

from apps.main.models import Product, ProductImage, CommonProduct
from apps.main.forms.product_admin import ProductAdminForm
from apps.product.formats import ImageAwareXLSX
from apps.product.resources import ProductResource


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "position")
    classes = ("product-images-inline",)


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
            "fields": (
                "name",
                "name_ru",
                "name_uz",
                "name_en",
                "description",
                "description_ru",
                "description_uz",
                "description_en",
                "category",
            ),
            "classes": ("manual-fields-section",),
            "description": _("Заполните эти поля, если добавляете продукт вручную.")
        }),
        (_("Маркет и цена"), {
            "fields": ("market", "price"),
            "description": _("Выберите свой маркет и укажите цену продукта.")
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
        info_url = reverse("admin:main_product_common_product_info")

        # Получаем выбранный common_product из формы
        if obj and obj.common_product:
            common_product = obj.common_product
        else:
            # При создании нового продукта obj может быть None
            # Информация будет обновляться через JavaScript
            return format_html(
                '<div id="common-product-info" class="common-product-info is-empty" data-url="{}">'
                '<div class="common-product-info__layout">'
                '<div class="common-product-info__image is-empty">Фото</div>'
                '<div class="common-product-info__content">'
                '<div class="common-product-info__title">Выберите продукт из общей базы</div>'
                '<div class="common-product-info__text">Чтобы увидеть информацию и фото</div>'
                '</div>'
                '</div>'
                '</div>',
                info_url
            )

        image_url = None
        if common_product.primary_image_file:
            try:
                image_url = common_product.primary_image_file.url
            except Exception:
                image_url = None

        return format_html(
            '<div id="common-product-info" class="common-product-info is-filled" data-url="{}">'
            '<div class="common-product-info__layout">'
            '<div class="common-product-info__image" style="background-image:url({});"></div>'
            '<div class="common-product-info__content">'
            '<div class="common-product-info__title">{} </div>'
            '<div class="common-product-info__text">{}</div>'
            '<div class="common-product-info__meta">Категория: {}</div>'
            '</div>'
            '</div>'
            '</div>',
            info_url,
            image_url or "",
            common_product.name,
            common_product.description[:120] + ("..." if len(common_product.description) > 120 else ""),
            common_product.category.name if common_product.category else "-"
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

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "common-product-info/",
                self.admin_site.admin_view(self.common_product_info),
                name="main_product_common_product_info",
            )
        ]
        return custom + urls

    def common_product_info(self, request):
        product_id = request.GET.get("id")
        if not product_id:
            return JsonResponse({"detail": "Missing id"}, status=400)

        try:
            common_product = CommonProduct.objects.select_related("category").get(id=product_id)
        except CommonProduct.DoesNotExist:
            return JsonResponse({"detail": "Not found"}, status=404)

        image_url = None
        if common_product.primary_image_file:
            try:
                image_url = request.build_absolute_uri(common_product.primary_image_file.url)
            except Exception:
                image_url = None

        data = {
            "id": common_product.id,
            "name": common_product.name,
            "name_ru": getattr(common_product, "name_ru", None),
            "name_uz": getattr(common_product, "name_uz", None),
            "name_en": getattr(common_product, "name_en", None),
            "description": common_product.description,
            "description_ru": getattr(common_product, "description_ru", None),
            "description_uz": getattr(common_product, "description_uz", None),
            "description_en": getattr(common_product, "description_en", None),
            "category": common_product.category.name if common_product.category else None,
            "image_url": image_url,
        }
        return JsonResponse(data)

    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
        js = ('admin/js/product_admin.js',)
