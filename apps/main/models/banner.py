from django.db import models

from apps.main.models import BaseModel

class Banner(BaseModel):
    name = models.CharField(max_length=128, verbose_name="Nomi")
    image = models.ImageField(upload_to="banner_images/", verbose_name="Rasm")
    position = models.IntegerField(blank=True, null=True, verbose_name="O'rin")
    is_active = models.BooleanField(default=True, verbose_name="Faol")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Bannerlar"