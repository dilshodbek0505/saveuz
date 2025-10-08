from django.conf import settings
from django.db.models import Q

from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget

from apps.main.models import Category, Market, Product


class TranslatedForeignKeyWidget(ForeignKeyWidget):
    def __init__(self, model, field="name"):
        super().__init__(model, field)
        self.language_codes = [code for code, _ in settings.LANGUAGES]

    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            return None

        value = value.strip()
        lookup = Q(**{f"{self.field}__iexact": value})
        for lang_code in self.language_codes:
            lookup |= Q(**{f"{self.field}_{lang_code}__iexact": value})

        try:
            return self.model.objects.get(lookup)
        except self.model.DoesNotExist:
            raise ValueError(f"{self.model.__name__} with name '{value}' not found.")
        except self.model.MultipleObjectsReturned:
            raise ValueError(f"Multiple {self.model.__name__} entries found for '{value}'.")


class ProductResource(resources.ModelResource):
    id = fields.Field(column_name="id", attribute="id", readonly=True)
    name = fields.Field(column_name="name", attribute="name")
    price = fields.Field(column_name="price", attribute="price")
    discount_price = fields.Field(
        column_name="discount_price", attribute="discount_price", readonly=True
    )
    discount_type = fields.Field(
        column_name="discount_type", attribute="discount_type", readonly=True
    )
    discount_value = fields.Field(
        column_name="discount_value", attribute="discount_value", readonly=True
    )
    category = fields.Field(
        column_name="category",
        attribute="category",
        widget=TranslatedForeignKeyWidget(Category, "name"),
    )
    market = fields.Field(
        column_name="market",
        attribute="market",
        widget=TranslatedForeignKeyWidget(Market, "name"),
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "discount_price",
            "discount_type",
            "discount_value",
            "category",
            "market",
        )
        export_order = (
            "id",
            "name",
            "price",
            "discount_price",
            "discount_type",
            "discount_value",
            "category",
            "market",
        )
