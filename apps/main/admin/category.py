from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Count, F
from unfold.admin import ModelAdmin

from apps.main.models import Category
from apps.main.admin.subcategory import SubcategoryInline


class CategoryRootFilter(admin.SimpleListFilter):
    title = _("Tur")
    parameter_name = "root"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Asosiy kategoriyalar (subkategoriyasi yo'q)")),
            ("no", _("Subkategoriyalar")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(parent__isnull=True)
        if self.value() == "no":
            return queryset.filter(parent__isnull=False)
        return queryset


def get_descendant_ids(category):
    """Рекурсивно собирает id всех потомков (для проверки цикла)."""
    ids = []
    for child in category.children.all():
        ids.append(child.pk)
        ids.extend(get_descendant_ids(child))
    return ids


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    icon_name = "category"
    inlines = (SubcategoryInline,)
    list_display = (
        "id",
        "image_thumbnail",
        "name_tree_display",
        "parent",
        "children_count_display",
        "order",
        "created_at",
    )
    list_display_links = ("id", "name_tree_display")
    list_filter = (CategoryRootFilter, "parent")
    search_fields = ("name",)
    list_editable = ("order",)
    autocomplete_fields = ("parent",)
    ordering = ("parent_id", "order", "name")
    list_per_page = 25

    fieldsets = (
        (
            None,
            {
                "fields": ("name", "image", "parent", "order"),
                "description": "Asosiy kategoriya uchun «Tegishli kategoriya»ni bo'sh qoldiring. "
                "Subkategoriya uchun ota kategoriyani tanlang.",
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related("parent").annotate(
            _children_count=Count("children", distinct=True)
        )
        return qs.order_by(F("parent_id").asc(nulls_first=True), "order", "name")

    def image_thumbnail(self, obj):
        if not obj.image:
            return mark_safe('<span class="category-admin-no-image">—</span>')
        url = obj.image.url
        return format_html(
            '<img src="{}" alt="" class="category-admin-thumb" loading="lazy" />',
            url,
        )

    image_thumbnail.short_description = "Rasm"

    def name_tree_display(self, obj):
        if obj.parent_id:
            indent = '<span class="category-admin-indent"></span>'
            return format_html(
                '{}<span class="category-admin-sub">{} › {}</span>',
                mark_safe(indent),
                obj.parent.name,
                obj.name,
            )
        return format_html(
            '<span class="category-admin-root">{}</span>',
            obj.name,
        )

    name_tree_display.short_description = "Kategoriya"
    name_tree_display.admin_order_field = "name"

    def children_count_display(self, obj):
        count = getattr(obj, "_children_count", 0) or obj.children.count()
        if count == 0:
            return "—"
        return format_html(
            '<span class="category-admin-children-count">{}</span>',
            count,
        )

    children_count_display.short_description = "Subkategoriyalar"
    children_count_display.admin_order_field = "_children_count"

    def save_model(self, request, obj, form, change):
        # Запрет цикла уже в form.clean
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Подмешиваем валидацию parent в форму
        original_clean = form.clean

        def clean_with_parent_validation(self):
            data = original_clean(self)
            parent = data.get("parent")
            if obj and obj.pk and parent:
                if parent.pk == obj.pk:
                    raise ValidationError(
                        "Kategoriyani o'zini ota sifatida tanlash mumkin emas."
                    )
                descendant_ids = get_descendant_ids(obj)
                if parent.pk in descendant_ids:
                    raise ValidationError(
                        "Kategoriyani o'zining ostkategoriyasi sifatida ota qilib "
                        "tanlash mumkin emas (tsikl yuzaga keladi)."
                    )
            return data

        form.clean = clean_with_parent_validation
        return form

    class Media:
        css = {"all": ("admin/css/product_admin.css",)}
