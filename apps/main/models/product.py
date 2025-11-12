from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.main.models import BaseModel, Market


class Product(BaseModel):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    description = models.TextField(verbose_name=_("Description"))
    market = models.ForeignKey(
        Market,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Market"),
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name=_("Discount price"),
    )
    discount_type = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        verbose_name=_("Discount type"),
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        "main.Category",
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name=_("Category"),
    )

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        if hasattr(self, "_primary_image_cache"):
            return self._primary_image_cache

        if hasattr(self, "_prefetched_objects_cache") and "images" in self._prefetched_objects_cache:
            images = sorted(
                self._prefetched_objects_cache["images"],
                key=lambda img: (img.position, img.id),
            )
            primary = images[0] if images else None
        else:
            primary = self.images.order_by("position", "id").first()

        self._primary_image_cache = primary
        return self._primary_image_cache

    @property
    def primary_image_file(self):
        primary = self.primary_image
        return primary.image if primary else None

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
    )
    image = models.ImageField(upload_to="product_images/", verbose_name=_("Image"))
    position = models.PositiveIntegerField(default=0, verbose_name=_("Position"))

    class Meta:
        verbose_name = _("Product image")
        verbose_name_plural = _("Product images")
        ordering = ("position", "id")

    def __str__(self):
        return f"{self.product_id}-{self.position}"
