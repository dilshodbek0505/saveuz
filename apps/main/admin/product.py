from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from import_export.admin import ExportMixin 
from unfold.admin import ModelAdmin

from apps.main.models import Product, ProductImage, CommonProduct, Subcategory
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
    import_export_change_list_template = "admin/main/product/change_list.html"
    list_display = ("id", "display_name", "market", "display_source")
    list_display_links = ("id", "display_name")
    search_fields = ("name", "common_product__name", "market__name")
    autocomplete_fields = ("category", "common_product")
    readonly_fields = ("discount_value", "discount_price", "discount_type", "display_common_product_info")
    
    fieldsets = (
        ("Qo'shish usuli", {
            "fields": ("add_mode",),
            "description": "Mahsulot qo'shish usulini tanlang: umumiy bazadan yoki qo'lda."
        }),
        ("Umumiy bazadan mahsulot", {
            "fields": ("common_product", "display_common_product_info"),
            "classes": ("common-product-section",),
            "description": "Umumiy bazadan mahsulotni tanlang. Nomi, tavsif va kategoriya avtomatik olinadi. Faqat narx va do'konni ko'rsating."
        }),
        ("Asosiy ma'lumot (qo'lda)", {
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
                "subcategory",
            ),
            "classes": ("manual-fields-section",),
            "description": "Mahsulotni qo'lda qo'shasangiz, bu maydonlarni to'ldiring. Subkategoriya tanlangan kategoriyaga tegishli bo'lishi kerak."
        }),
        ("Do'kon va narx", {
            "fields": ("market", "price"),
            "description": "Do'koningizni tanlang va mahsulot narxini kiriting."
        }),
    )
    
    inlines = (ProductImageInline,)

    @admin.display(description="Nomi")
    def display_name(self, obj):
        return obj.resolved_name

    @admin.display(description="Manba")
    def display_source(self, obj):
        if obj.common_product:
            return format_html(
                '<span style="color: #28a745;">✓ Umumiy bazadan</span>'
            )
        return format_html(
            '<span style="color: #ffc107;">✎ Qo\'lda</span>'
        )

    @admin.display(description="Mahsulot haqida ma'lumot")
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
                '<div class="common-product-info__image is-empty">Rasm</div>'
                '<div class="common-product-info__content">'
                '<div class="common-product-info__title">Umumiy bazadan mahsulot tanlang</div>'
                '<div class="common-product-info__text">Ma\'lumot va rasmini ko\'rish uchun</div>'
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
            '<div class="common-product-info__meta">Kategoriya: {}</div>'
            '<div class="common-product-info__meta">Subkategoriya: {}</div>'
            '</div>'
            '</div>'
            '</div>',
            info_url,
            image_url or "",
            common_product.name,
            common_product.description[:120] + ("..." if len(common_product.description) > 120 else ""),
            common_product.category.name if common_product.category else "-",
            getattr(common_product.subcategory, "name", None) or "-"
        )
    display_common_product_info.short_description = "Mahsulot haqida ma'lumot"

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request)
        qs = qs.select_related("market", "common_product", "common_product__category", "common_product__subcategory", "category", "subcategory")

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
        if db_field.name == "subcategory":
            obj = kwargs.get("obj") or getattr(request, "_current_product_obj", None)
            if obj:
                resolved = obj.resolved_category if hasattr(obj, "resolved_category") else getattr(obj, "category", None)
                if not resolved and getattr(obj, "subcategory_id", None):
                    resolved = getattr(obj.subcategory, "category", None)
                if resolved:
                    kwargs["queryset"] = Subcategory.objects.filter(category_id=resolved.pk).order_by("order", "name")
                else:
                    kwargs["queryset"] = Subcategory.objects.none()
            else:
                kwargs["queryset"] = Subcategory.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._current_product_obj = obj
        return super().get_form(request, obj, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, ProductImageInline) and request.method == "POST":
                add_mode = request.POST.get("add_mode")
                common_product = request.POST.get("common_product")
                if common_product and add_mode in (None, "", "common"):
                    continue
            yield inline.get_formset(request, obj), inline

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "common-product-info/",
                self.admin_site.admin_view(self.common_product_info),
                name="main_product_common_product_info",
            ),
            path(
                "get-subcategories/",
                self.admin_site.admin_view(self.get_subcategories),
                name="main_product_get_subcategories",
            ),
            path(
                "translate/",
                self.admin_site.admin_view(self.translate_product_text),
                name="main_product_translate",
            ),
        ]
        return custom + urls

    def get_subcategories(self, request):
        """JSON: subcategories for category_id (for dependent dropdown)."""
        category_id = request.GET.get("category_id")
        if not category_id:
            return JsonResponse({"subcategories": []})
        try:
            qs = Subcategory.objects.filter(category_id=int(category_id)).order_by("order", "name")
            subcategories = [{"id": s.pk, "name": s.name} for s in qs]
        except (ValueError, TypeError):
            subcategories = []
        return JsonResponse({"subcategories": subcategories})

    def common_product_info(self, request):
        product_id = request.GET.get("id")
        if not product_id:
            return JsonResponse({"detail": "Missing id"}, status=400)

        try:
            common_product = CommonProduct.objects.select_related("category", "subcategory").get(id=product_id)
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
            "subcategory": common_product.subcategory.name if getattr(common_product, "subcategory", None) else None,
            "image_url": image_url,
        }
        return JsonResponse(data)

    def translate_product_text(self, request):
        """POST: text, source_lang → { uz, ru, en }. Для имени и описания по отдельности."""
        if request.method != "POST":
            return JsonResponse({"error": "Method not allowed"}, status=405)
        from apps.main.services.translation import translate_to_all_languages
        import json
        try:
            body = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        text = (body.get("text") or "").strip()
        source_lang = (body.get("source_lang") or "uz").lower()
        if source_lang not in ("uz", "ru", "en"):
            source_lang = "uz"
        if not text:
            return JsonResponse({"uz": "", "ru": "", "en": ""})
        result = translate_to_all_languages(text, source_lang)
        return JsonResponse(result)

    class Media:
        css = {
            'all': ('admin/css/product_admin.css',)
        }
        js = ('admin/js/product_admin.js',)
