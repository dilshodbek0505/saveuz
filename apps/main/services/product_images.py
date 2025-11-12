from __future__ import annotations

from typing import Iterable

from django.db import transaction

from apps.main.models import Product, ProductImage


def _normalize_files(files: Iterable) -> list:
    normalized = []
    for file in files or []:
        if file:
            normalized.append(file)
    return normalized


def attach_product_images(
    product: Product,
    files: Iterable,
    *,
    replace: bool = False,
) -> None:
    """
    Attach uploaded image files to a product while preserving order.
    """
    upload_files = _normalize_files(files)
    if not upload_files:
        return

    with transaction.atomic():
        if replace:
            product.images.all().delete()
            start_position = 0
        else:
            max_position = (
                product.images.order_by("-position")
                .values_list("position", flat=True)
                .first()
            )
            start_position = 0 if max_position is None else max_position + 1

        for index, file in enumerate(upload_files):
            ProductImage.objects.create(
                product=product,
                image=file,
                position=start_position + index,
            )
