from __future__ import annotations

from typing import Iterable, List, Optional

from django import forms
from django.core.exceptions import ValidationError

from apps.main.services.product_images import attach_product_images


class MultiImageWidget(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.FileField):
    """
    File field that accepts multiple images through a single widget.
    """

    widget = MultiImageWidget(
        attrs={
            "multiple": True,
            "accept": "image/*",
            "class": "bulk-input",
            "data-role": "image-input",
        }
    )

    def clean(self, data, initial=None):
        if not data:
            return []

        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned: List = []
        errors: List[ValidationError] = []
        for item in data:
            try:
                cleaned.append(super().clean(item, initial))
            except ValidationError as exc:  # noqa: PERF203
                errors.extend(exc.error_list)

        if errors:
            raise ValidationError(errors)

        return cleaned


class ProductImagesFormMixin:
    """
    Injects an ``images`` field into forms and persists uploads to ProductImage.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["images"] = MultipleImageField(required=False)

    _pending_images: Optional[Iterable] = None

    def save(self, commit=True):
        image_files = self.cleaned_data.get("images") or []
        instance = super().save(commit=commit)
        if commit:
            attach_product_images(instance, image_files)
        else:
            self._pending_images = image_files
        return instance

    def save_m2m(self):
        super().save_m2m()
        if getattr(self, "_pending_images", None) and getattr(self, "instance", None):
            attach_product_images(self.instance, self._pending_images)
            self._pending_images = None
