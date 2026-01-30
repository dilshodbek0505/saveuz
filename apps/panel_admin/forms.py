from django import forms
from django.forms import modelformset_factory

from apps.main.forms.product import ProductImagesFormMixin
from apps.main.models import Product


class ProductBulkForm(ProductImagesFormMixin, forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "price",
            "description",
            "market",
            "category",
            "discount_price",
            "discount_type",
            "discount_value",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            if "bulk-input" not in existing.split():
                field.widget.attrs["class"] = (existing + " bulk-input").strip()

    def clean(self):
        cleaned = super().clean()
        missing = []
        if not cleaned.get("name"):
            missing.append("name")
        if not cleaned.get("description"):
            missing.append("description")
        if not cleaned.get("category"):
            missing.append("category")
        if missing:
            raise forms.ValidationError(
                "Missing required fields: " + ", ".join(missing)
            )
        return cleaned


ProductBulkFormSet = modelformset_factory(
    Product,
    form=ProductBulkForm,
    extra=1,
    can_delete=False,
)
