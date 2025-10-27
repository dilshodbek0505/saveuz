from django import forms
from django.forms import modelformset_factory

from apps.main.models import Product


class ProductBulkForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "price",
            "image",
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


ProductBulkFormSet = modelformset_factory(
    Product,
    form=ProductBulkForm,
    extra=1,
    can_delete=False,
)
