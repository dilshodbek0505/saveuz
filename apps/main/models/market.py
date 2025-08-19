from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from apps.main.models import BaseModel

User = get_user_model()


class Market(BaseModel):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    description = models.TextField(verbose_name=_("Description"))
    logo = models.ImageField(upload_to="market_logos/", verbose_name=_("Logo"))
    lon = models.FloatField(verbose_name=_("Longitude"))
    lat = models.FloatField(verbose_name=_("Latitude"))
    address = models.CharField(max_length=255, 
                               blank=True, null=True, 
                               verbose_name=_("Address"))
    open_time = models.TimeField(verbose_name=_("Open time"))
    end_time = models.TimeField(verbose_name=_("End time"))
    owner = models.ForeignKey(User,
                              on_delete=models.PROTECT,
                              related_name="markets",
                              verbose_name=_("Owner"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Market")
        verbose_name_plural = _("Markets")
