from django.db import models

from apps.main.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=128, verbose_name="Nomi")
    image = models.ImageField(upload_to="category_images/", verbose_name="Rasm")
    parent = models.ForeignKey("self", on_delete=models.PROTECT,
                               blank=True, null=True,
                               related_name="children",
                               verbose_name="Tegishli kategoriya")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"