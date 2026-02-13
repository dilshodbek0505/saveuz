from django.db import models
from django.contrib.auth import get_user_model

from apps.main.models import BaseModel

User = get_user_model()


class Market(BaseModel):
    name = models.CharField(max_length=128, verbose_name="Nomi")
    description = models.TextField(verbose_name="Tavsif")
    logo = models.ImageField(upload_to="market_logos/", verbose_name="Logotip")
    lon = models.FloatField(verbose_name="Uzunlik")
    lat = models.FloatField(verbose_name="Kenglik")
    address = models.CharField(max_length=255,
                               blank=True, null=True,
                               verbose_name="Manzil")
    open_time = models.TimeField(verbose_name="Ochilish vaqti")
    end_time = models.TimeField(verbose_name="Yopilish vaqti")
    owner = models.ForeignKey(User,
                              on_delete=models.PROTECT,
                              related_name="markets",
                              verbose_name="Egasi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Do'kon"
        verbose_name_plural = "Do'konlar"
