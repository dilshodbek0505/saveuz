from django.db import models

from apps.main.models import BaseModel


class Subcategory(BaseModel):
    """Субкатегория, привязанная к одной категории."""
    category = models.ForeignKey(
        "main.Category",
        on_delete=models.PROTECT,
        related_name="subcategories",
        verbose_name="Kategoriya",
    )
    name = models.CharField(max_length=128, verbose_name="Nomi")
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib",
        help_text="O'zaro tartib (kichik raqam birinchi).",
    )

    def __str__(self):
        return f"{self.category.name} › {self.name}"

    class Meta:
        verbose_name = "Subkategoriya"
        verbose_name_plural = "Subkategoriyalar"
        ordering = ["category", "order", "name"]
