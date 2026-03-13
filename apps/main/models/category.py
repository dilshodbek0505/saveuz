from django.db import models
from django.db.models import F

from apps.main.models import BaseModel


class CategoryManager(models.Manager):
    """Порядок: сначала корневые (parent_id=NULL), затем по parent_id, order, name."""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by(F("parent_id").asc(nulls_first=True), "order", "name")
        )


class Category(BaseModel):
    """Иерархическая категория: parent=None — корневая, иначе субкатегория."""
    name = models.CharField(max_length=128, verbose_name="Nomi")
    image = models.ImageField(upload_to="category_images/", verbose_name="Rasm")
    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="children",
        verbose_name="Tegishli kategoriya (bo'sh = asosiy kategoriya)",
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib",
        help_text="O'zaro tartib (kichik raqam birinchi).",
    )

    objects = CategoryManager()

    def __str__(self):
        if self.parent_id:
            return f"{self.parent.name} › {self.name}"
        return self.name

    def get_breadcrumb(self):
        """Breadcrumb: ['Root', 'Sub', 'SubSub']."""
        parts = []
        cur = self
        while cur:
            parts.append(cur.name)
            cur = cur.parent
        return list(reversed(parts))

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["parent_id", "order", "name"]